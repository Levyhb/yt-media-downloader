# YTDrop

Aplicação para baixar áudio em MP3 ou vídeo em MP4 a partir de uma URL válida do YouTube. O projeto tem uma API Python/Django em `api/` e um frontend Blazor WebAssembly em `web/`.

Cada download tem limite máximo de **50.000.000 bytes (50 MB)**. Arquivos maiores são interrompidos ou rejeitados pela API.

## Requisitos

- Python 3.12
- Node.js e npm (para executar o script de desenvolvimento da API)
- .NET 10 SDK
- FFmpeg para conversão de áudio no modo de desenvolvimento local; a imagem Docker já o inclui

## Executar a API localmente

No PowerShell, a partir da raiz do repositório:

```powershell
cd api
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd api
Copy-Item .env.example .env
$env:Path = (Resolve-Path ..\.venv\Scripts).Path + ";" + $env:Path
npm run dev
```

O script `dev`, definido em `api/api/package.json`, inicia o servidor Django em `http://localhost:8080`. O endpoint de saúde é `http://localhost:8080/health`. O ajuste de `PATH` vale apenas para esse terminal e permite ao script usar o Python do ambiente virtual sem precisar ativar scripts do PowerShell.

O arquivo `api/api/.env` é local e não deve ser enviado ao GitHub. A configuração de exemplo permite ajustar as origens CORS para o frontend local em `http://localhost:5004` e `https://localhost:7145`.

### Executar a API com Docker

Essa opção inicia a API com a configuração do container, incluindo FFmpeg e o provedor de PO Token:

```powershell
cd api
docker build -t ytdrop-api .
docker run --rm -p 8080:8080 --env-file api/.env ytdrop-api
```

## Executar o frontend localmente

Em outro terminal, na raiz do repositório:

```powershell
cd web
dotnet run
```

O perfil de desenvolvimento abre o frontend em `http://localhost:5004` (ou `https://localhost:7145`). A URL da API fica em `web/wwwroot/appsettings.Development.json`. Para usar a API local, defina `ApiBaseUrl` como `http://localhost:8080`; caso contrário, o frontend usará a URL atualmente configurada nesse arquivo.

## Uso e endpoints

Cole uma URL válida de vídeo do YouTube, escolha áudio ou vídeo e, para vídeo, selecione uma das qualidades oferecidas pela API. O download é iniciado pelo navegador; a API não mantém os arquivos depois de concluir a resposta.

- `GET /api/video-info/?url=<url>` — consulta título e qualidades disponíveis.
- `GET /api/download-video/?url=<url>&quality=<qualidade>` — baixa o vídeo em MP4.
- `GET /api/download-audio/?url=<url>&format=mp3` — baixa o áudio em MP3.

O teto é aplicado tanto às faixas baixadas quanto ao arquivo final. A API aceita URLs HTTPS dos domínios oficiais do YouTube e valida a URL antes de iniciar o processamento.

## Configuração de produção

No Cloud Run, configure `SECRET_KEY` pelo Secret Manager, `ALLOWED_HOSTS` com o host exato da API e `CORS_ALLOWED_ORIGINS` com a origem do frontend, por exemplo `https://yt-media-downloader.vercel.app`. `MAX_DOWNLOAD_SIZE_BYTES` pode reduzir o limite, mas o código nunca permite ultrapassar 50.000.000 bytes. Não publique `.env` nem cookies do YouTube.

## Tecnologias

- Frontend: Blazor WebAssembly, Razor, CSS e .NET 10
- Backend: Python, Django, yt-dlp e FFmpeg
- Hospedagem: frontend estático na Vercel e API containerizada no Google Cloud Run
