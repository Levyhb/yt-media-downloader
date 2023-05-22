import { useState } from "react";
import styles from "@/styles/Home.module.css";
import OndemandVideoIcon from '@mui/icons-material/OndemandVideo';
import AudiotrackIcon from '@mui/icons-material/Audiotrack';
import { notifyError } from "@/utils/notifyMessage";
notifyError

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
          notifyError('Invalid URL')
        }
      } catch (error) {
        console.log("Erro na solicitação", error);

      }
    } else {
      console.log("URL inválida");
    }
  };

  return (
    <main className={styles.container}>
      <h1 className={styles.title}>YT Media Downloader</h1>
      <input
        className={styles.input_url}
        type="text"
        placeholder="Video Url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <div className={styles.div_buttons}>
        <button
          type="button"
          onClick={() => handleDownload("video")}
          className={`${styles.button} ${styles.video}`}
          disabled={url.length === 0}
        >
          Download Video <OndemandVideoIcon />
        </button>
        <button
          type="button"
          onClick={() => handleDownload("audio")}
          className={`${styles.button} ${styles.audio}`}
          disabled={url.length === 0}
        >
          Download Audio <AudiotrackIcon />
        </button>
      </div>
    </main>
  );
}

export default HomeInterface;
