window.ytDrop = {
    download: async function (url, suggestedName, contentType, dotnetReference) {
        let fileHandle = null;

        if (window.showSaveFilePicker) {
            try {
                const extension = suggestedName.slice(suggestedName.lastIndexOf("."));
                fileHandle = await window.showSaveFilePicker({
                    suggestedName,
                    types: [{
                        description: contentType === "audio/mpeg" ? "Áudio MP3" : "Vídeo MP4",
                        accept: { [contentType]: [extension] }
                    }]
                });
            } catch (error) {
                if (error?.name === "AbortError") return false;
                throw error;
            }
        }

        await dotnetReference.invokeMethodAsync("UpdateDownloadProgress", -1);
        const response = await fetch(url);
        if (!response.ok) {
            let message = `Falha no download (${response.status}).`;
            try {
                const payload = await response.json();
                if (payload?.error) message = payload.error;
            } catch { }
            throw new Error(message);
        }

        const total = Number(response.headers.get("content-length")) || 0;
        const reader = response.body?.getReader();
        if (!reader) throw new Error("O navegador não oferece suporte ao download em fluxo.");

        let received = 0;
        let lastReportedProgress = -1;
        let writable = null;
        const chunks = [];

        try {
            if (fileHandle) writable = await fileHandle.createWritable();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                received += value.byteLength;
                if (writable) await writable.write(value);
                else chunks.push(value);

                if (total > 0) {
                    const progress = Math.min(100, (received / total) * 100);
                    if (progress - lastReportedProgress >= 1 || progress === 100) {
                        lastReportedProgress = progress;
                        await dotnetReference.invokeMethodAsync("UpdateDownloadProgress", progress);
                    }
                }
            }

            if (writable) {
                await writable.close();
            } else {
                const blob = new Blob(chunks, { type: contentType });
                const objectUrl = URL.createObjectURL(blob);
                const anchor = document.createElement("a");
                anchor.href = objectUrl;
                anchor.download = suggestedName;
                anchor.style.display = "none";
                document.body.appendChild(anchor);
                anchor.click();
                anchor.remove();
                setTimeout(() => URL.revokeObjectURL(objectUrl), 30_000);
            }

            await dotnetReference.invokeMethodAsync("UpdateDownloadProgress", 100);
            return true;
        } catch (error) {
            if (writable) {
                try { await writable.abort(); } catch { }
            }
            throw error;
        }
    }
};
