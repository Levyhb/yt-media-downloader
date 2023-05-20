from django.http import HttpResponse
from pytube import YouTube
import tempfile
import os


def download_video(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponse('URL parameter is required.', status=400)

    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        temp_file = video_stream.download()

        filename = yt.title + '.' + video_stream.mime_type.split('/')[-1]
        with open(temp_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

        os.remove(temp_file)

        return response
    except Exception as e:
        return HttpResponse(str(e), status=500)


def download_audio(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponse('URL parameter is required.', status=400)

    try:
        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        temp_file = audio_stream.download()

        filename = yt.title + '.' + audio_stream.mime_type.split('/')[-1]
        with open(temp_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

        os.remove(temp_file)

        return response
    except Exception as e:
        return HttpResponse(str(e), status=500)
