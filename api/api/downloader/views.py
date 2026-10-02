import logging
import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from django.http import FileResponse, JsonResponse
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)
MAX_VIDEO_DURATION_SECONDS = int(os.environ.get("MAX_VIDEO_DURATION_SECONDS", "3600"))
MAX_DOWNLOAD_SIZE_BYTES = int(os.environ.get("MAX_DOWNLOAD_SIZE_BYTES", str(512 * 1024 * 1024)))
DOWNLOAD_CHUNK_SIZE = 64 * 1024
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
YTDLP_COOKIE_FILE = os.environ.get("YTDLP_COOKIE_FILE")


class TemporaryDownload:
    def __init__(self, path, directory):
        self.name = str(path)
        self._file = open(path, "rb")
        self._directory = directory

    def read(self, size=DOWNLOAD_CHUNK_SIZE):
        return self._file.read(size)

    def tell(self):
        return self._file.tell()

    def seek(self, offset, whence=0):
        return self._file.seek(offset, whence)

    def close(self):
        try:
            if not self._file.closed:
                self._file.close()
        finally:
            shutil.rmtree(self._directory, ignore_errors=True)


def _is_valid_youtube_url(value):
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme == "https"
            and parsed.hostname in YOUTUBE_HOSTS
            and parsed.username is None
            and parsed.password is None
            and parsed.port is None
        )
    except ValueError:
        return False


def _duration_filter(info, *, incomplete):
    duration = info.get("duration")
    if duration is None:
        return "Video duration is unavailable."
    if duration > MAX_VIDEO_DURATION_SECONDS:
        return "Video exceeds the maximum allowed duration."
    return None


def _youtube_options():
    options = {"js_runtimes": {"node": {}}}
    if YTDLP_COOKIE_FILE:
        options["cookiefile"] = YTDLP_COOKIE_FILE
    return options


def _prepare_download(url, media_type, audio_format):
    directory = tempfile.mkdtemp(prefix="yt-media-")
    options = {
        **_youtube_options(),
        "outtmpl": os.path.join(directory, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 2,
        "fragment_retries": 2,
        "max_filesize": MAX_DOWNLOAD_SIZE_BYTES,
        "match_filter": _duration_filter,
    }

    if media_type == "video":
        quality = audio_format
        quality_filter = f"[height<={quality}]" if quality else "[height<=1080]"
        options.update({
            "format": f"bestvideo{quality_filter}[ext=mp4]+bestaudio[ext=m4a]/best{quality_filter}[ext=mp4]/best{quality_filter}/best",
            "merge_output_format": "mp4",
        })
    else:
        options["format"] = "bestaudio/best"
        if audio_format == "mp3":
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=True)

        files = [
            path for path in Path(directory).iterdir()
            if path.is_file() and not path.name.endswith((".part", ".ytdl"))
        ]
        if len(files) != 1 or files[0].stat().st_size > MAX_DOWNLOAD_SIZE_BYTES:
            raise ValueError("Downloaded file is missing or exceeds the configured size limit.")
        return directory, files[0], str(info.get("title") or "download")
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise


def _download(request, media_type):
    url = request.GET.get("url", "")
    if not url:
        return JsonResponse({"error": "O parâmetro url é obrigatório."}, status=400)
    if not _is_valid_youtube_url(url):
        return JsonResponse({"error": "Informe uma URL HTTPS válida do YouTube."}, status=400)

    audio_format = request.GET.get("format", "original")
    if media_type == "audio" and audio_format not in {"original", "mp3"}:
        return JsonResponse({"error": "Formato de áudio não suportado."}, status=400)
    if media_type == "video":
        try:
            audio_format = int(request.GET.get("quality", "1080"))
        except ValueError:
            return JsonResponse({"error": "Qualidade de vídeo inválida."}, status=400)
        if audio_format not in {144, 240, 360, 480, 720, 1080}:
            return JsonResponse({"error": "Qualidade de vídeo não suportada."}, status=400)

    try:
        directory, path, title = _prepare_download(url, media_type, audio_format)
    except Exception as error:
        logger.warning("Media download failed (%s).", type(error).__name__)
        return JsonResponse(
            {"error": "Não foi possível processar este vídeo. Verifique se ele está disponível e tente novamente."},
            status=502,
        )

    filename = f"{get_valid_filename(title)[:150] or 'download'}{path.suffix}"
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    temporary_file = None
    try:
        temporary_file = TemporaryDownload(path, directory)
        return FileResponse(
            temporary_file,
            as_attachment=True,
            filename=filename,
            content_type=content_type,
        )
    except Exception:
        if temporary_file is not None:
            temporary_file.close()
        else:
            shutil.rmtree(directory, ignore_errors=True)
        raise


@require_GET
def download_video(request):
    return _download(request, "video")


@require_GET
def download_audio(request):
    return _download(request, "audio")


@require_GET
def video_info(request):
    url = request.GET.get("url", "")
    if not _is_valid_youtube_url(url):
        return JsonResponse({"error": "Informe uma URL HTTPS válida do YouTube."}, status=400)

    try:
        options = {
            **_youtube_options(),
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "socket_timeout": 15,
        }
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=False)
        qualities = sorted({
            int(format_info["height"])
            for format_info in info.get("formats", [])
            if format_info.get("height") and format_info.get("vcodec") not in {None, "none"}
            and int(format_info["height"]) in {144, 240, 360, 480, 720, 1080}
        })
        return JsonResponse({
            "id": info.get("id"),
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "qualities": qualities or [360, 720, 1080],
        })
    except Exception as error:
        logger.warning("Video info failed (%s).", type(error).__name__)
        return JsonResponse({"error": "Não foi possível carregar os dados deste vídeo."}, status=502)


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})
