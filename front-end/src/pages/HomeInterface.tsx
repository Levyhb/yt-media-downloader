import { useState } from "react";

function HomeInterface() {
  const [url, setUrl] = useState("");

  const handleDownload = async (type: string) => {
    if (url) {
      try {
        const response =
          type === "video"
            ? await fetch(`http://127.0.0.1:8000/api/download-video?url=${url}`)
            : await fetch(
                `http://127.0.0.1:8000/api/download-audio?url=${url}`
              );
        if (response.ok) {
          const blob = await response.blob();
          console.log(blob);
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = type === "video" ? "video.mp4" : "audio.mp3";
          a.click();
        } else {
          console.log("Erro na solicitação");
        }
      } catch (error) {
        console.log("Erro na solicitação", error);
      }
    } else {
      console.log("URL inválida");
    }
  };

  return (
    <div className="video-downloader-container">
      <div>
        <input
          type="text"
          placeholder="Video Url"
          onChange={(e) => setUrl(e.target.value)}
        />
      </div>
      <div>
        <button type="button" onClick={() => handleDownload("video")}>
          Download Vídeo
        </button>
        <button type="button" onClick={() => handleDownload("audio")}>
          Download Audio
        </button>
      </div>
    </div>
  );
}

export default HomeInterface;
