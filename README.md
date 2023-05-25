# yt-media-downloader

Aplicação web que utiliza a lib pytube do python para poder baixar um video/audio do youtube através da URL.
## Stack utilizada

**Front-end:** React, Typescript/Javascript, NextJs, CSS, HTML

**Back-end:** Python, Django

## Documentação

- [pytube](https://pytube.io/en/latest/)


## Rodando localmente

Clone o projeto

```bash
  git clone git@github.com:Levyhb/yt-media-downloader.git
```

- Entre no diretório do projeto

```bash
  cd yt-media-downloader
```


### Para rodar o front-end
```
  cd front-end/ && npm install && npm run dev
```

- Para rodar localmente, você deve seguir os passos do arquivo .env.example

### Para rodar o back-end 
Api feita com Django (python)

- É recomendado, primeiramente, você criar um ambiente virtual com venv: 
```
  python3 -m venv .venv && source .venv/bin/activate
```

- Baixar as dependências e depois rodar o back-end:

```
cd yt-downloader-api/ && pip install -r requirements.txt 
```

```
cd video_downloader_api/ && python manage.py runserver
```

- Para funcionar corretamente necessário seguir os passos contido em yt-downloader-api/video_downloader_api/video_downloader_api/settings py
