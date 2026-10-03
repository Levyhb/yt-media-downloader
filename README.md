# YTDrop

O YTDrop é uma aplicação web para download de áudio e vídeo a partir de uma URL do YouTube, com frontend Blazor WebAssembly e uma API Python containerizada no Google Cloud Run.

## Estado do projeto

O diretório `front-end/` continua sendo a implementação legada em React/Next.js. O novo frontend Blazor já foi criado em `web/`, enquanto a API Python permanece separada em `api/`.

O roteiro detalhado está em [docs/PLANO-MIGRACAO.md](docs/PLANO-MIGRACAO.md).

## Arquitetura planejada

```text
web/  -> Blazor WebAssembly (.NET 10), publicado como site estático
api/  -> Python, yt-dlp e FFmpeg, publicado como container no Cloud Run
```

## Stack atual (legada)

**Frontend legado:** React, TypeScript/JavaScript, Next.js, CSS e HTML

**Backend atual:** Python, Django e yt-dlp

## Stack alvo

**Frontend:** Blazor WebAssembly, .NET 10, Razor e CSS

**Backend:** Python, Django ou FastAPI, yt-dlp e FFmpeg

**Deploy:** Google Cloud Run para a API e um host de site estático para o frontend

## Documentação

- [Plano detalhado de migração e publicação](docs/PLANO-MIGRACAO.md)
- [Documentação do Blazor](https://learn.microsoft.com/aspnet/core/blazor/)
- [Documentação do yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Documentação do Google Cloud Run](https://cloud.google.com/run/docs)

## Frontend Blazor

Para executar o novo frontend:

```bash
cd web
dotnet run
```

Em desenvolvimento, ele usa `http://localhost:8080` como URL da API, definida em `web/wwwroot/appsettings.Development.json`.

O frontend antigo em `front-end/` foi mantido para comparação visual durante a migração. A tela Blazor carrega a prévia pelo player oficial do YouTube, consulta as qualidades disponíveis e permite escolher a resolução antes do download. Para áudio, o formato atual é MP3.


## Rodando localmente

Clone o projeto

```bash
  git clone git@github.com:Levyhb/yt-media-downloader.git
```

- Entre no diretório do projeto

```bash
  cd yt-media-downloader
```


### Frontend legado

Enquanto a migração não for concluída, o frontend antigo pode ser executado com:

```
  cd front-end/ && npm install && npm run dev
```

- Para rodar localmente, você deve seguir os passos do arquivo .env.example

### API Python

A API Django usa `yt-dlp` e FFmpeg. Para rodar localmente, instale Python 3.12 e FFmpeg, crie um ambiente virtual e instale as dependências:

```bash
cd api
python -m venv .venv
# Ative o ambiente virtual antes de continuar.
pip install -r requirements.txt
```

Copie `video_downloader_api/.env.example` para `video_downloader_api/.env` e inicie a API:

```bash
cd api
python manage.py runserver 0.0.0.0:8080
```

O endpoint de saúde fica em `http://localhost:8080/health`. A prévia usa `/api/video-info/?url=...`; os endpoints de download ficam em `/api/download-video/` e `/api/download-audio/`. Vídeo aceita `quality` (`144`, `240`, `360`, `480`, `720` ou `1080`) e áudio MP3 é solicitado com `format=mp3`.

Para executar o container localmente:

```bash
cd api
docker build -t ytdrop-api .
docker run --rm -p 8080:8080 --env-file video_downloader_api/.env ytdrop-api
```

Para executar os testes Django dentro da imagem:

```bash
docker run --rm -e DEBUG=true ytdrop-api python manage.py test downloader
```

No Cloud Run, configure `SECRET_KEY` pelo Secret Manager, `CORS_ALLOWED_ORIGINS` com a origem exata do frontend e `ALLOWED_HOSTS` com os hosts aceitos. Não publique o arquivo `.env` local.

## Migração

O novo ambiente de desenvolvimento será documentado e executado nesta ordem:

1. substituir `front-end` por `web`;
2. criar o Blazor WebAssembly em .NET 10;
3. reproduzir a interface em Razor e CSS;
4. modernizar a API Python com `yt-dlp`;
5. adicionar Docker e testes locais;
6. publicar a API no Cloud Run;
7. configurar a URL da API por ambiente;
8. publicar o Blazor como site estático;
9. atualizar esta documentação com a arquitetura final e o procedimento de deploy.

Consulte [docs/PLANO-MIGRACAO.md](docs/PLANO-MIGRACAO.md) antes de iniciar cada fase.
