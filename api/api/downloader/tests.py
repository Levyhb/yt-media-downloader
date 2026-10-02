import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase


class DownloadApiTests(TestCase):
	def test_health_endpoint_returns_ok(self):
		response = self.client.get("/health")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), {"status": "ok"})

	def test_download_requires_url(self):
		response = self.client.get("/api/download-video/")

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json()["error"], "O parâmetro url é obrigatório.")

	def test_download_rejects_non_youtube_url(self):
		with patch("downloader.views._prepare_download") as prepare_download:
			response = self.client.get("/api/download-video/?url=https://example.com/video")

		self.assertEqual(response.status_code, 400)
		prepare_download.assert_not_called()

	def test_audio_format_must_be_supported(self):
		response = self.client.get(
			"/api/download-audio/?url=https://youtu.be/video-id&format=wav"
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json()["error"], "Formato de áudio não suportado.")

	def test_streamed_download_removes_temporary_file_on_close(self):
		with tempfile.TemporaryDirectory() as parent:
			directory = Path(parent) / "download"
			directory.mkdir()
			path = directory / "video.mp4"
			path.write_bytes(b"video-bytes")

			with patch(
				"downloader.views._prepare_download",
				return_value=(str(directory), path, "sample video"),
			):
				response = self.client.get(
					"/api/download-video/?url=https://youtu.be/video-id"
				)

			self.assertEqual(response.status_code, 200)
			self.assertTrue(response.streaming)
			self.assertEqual(response["Content-Type"], "video/mp4")
			self.assertIn("sample_video.mp4", response["Content-Disposition"])
			self.assertEqual(b"".join(response.streaming_content), b"video-bytes")
			response.close()
			self.assertFalse(directory.exists())

	def test_download_failure_does_not_expose_exception_details(self):
		with patch(
			"downloader.views._prepare_download",
			side_effect=RuntimeError("private infrastructure detail"),
		):
			response = self.client.get(
				"/api/download-video/?url=https://youtu.be/video-id"
			)

		self.assertEqual(response.status_code, 502)
		self.assertNotIn("private infrastructure detail", response.content.decode())
