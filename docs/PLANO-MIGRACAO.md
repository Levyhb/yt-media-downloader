# Plano de migração e publicação do YTDrop

Este documento define o roteiro do YTDrop, uma aplicação com frontend em .NET/Blazor e backend Python publicado no Google Cloud Run.

O objetivo é manter o backend em Python, substituir o frontend React/Next.js por Blazor WebAssembly e deixar cada parte com responsabilidades e ciclo de deploy próprios.

## Status atual

- Fase 1: em andamento; `front-end/` foi preservado e `web/` foi criado.
- Fase 2: concluída inicialmente; o projeto Blazor WebAssembly em .NET 10 compila sem erros.
- Fase 3: em andamento; a tela principal foi reproduzida em Razor e CSS.
- Fases 4 e 5: possuem uma primeira implementação funcional de Python, yt-dlp, FFmpeg, Docker e testes locais.
- Fases 6 a 9: pendentes.

## 1. Arquitetura atual

```text
front-end/                         # Next.js, React, TypeScript e CSS (legado)
web/                                # Blazor WebAssembly (.NET 10)
api/                                # Django, yt-dlp e FFmpeg
  api/
render.yaml                        # configuração antiga do Render
```

O backend atual possui dois endpoints:

```text
GET /api/download-video/?url=<youtube-url>
GET /api/download-audio/?url=<youtube-url>
```

## 2. Arquitetura-alvo

```text
YTDrop/
├── web/                            # Blazor WebAssembly (.NET 10)
│   ├── Components/ ou Pages/
│   ├── wwwroot/
│   └── wwwroot/appsettings*.json
├── api/                            # Python/Django ou Python/FastAPI
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── docs/
│   └── PLANO-MIGRACAO.md
└── README.md
```

Fluxo esperado:

```text
Usuário
   ↓
Blazor WebAssembly (site estático)
   ↓ HTTPS + CORS
API Python no Cloud Run
   ↓
yt-dlp + FFmpeg
   ↓
stream de áudio/vídeo para o navegador
```

O frontend será um site estático. A API será um serviço independente em container, com sua própria URL, variáveis de ambiente, logs e deploy.

## 3. Pré-requisitos

Instalar localmente:

- .NET 10 SDK;
- Python 3.10 ou superior;
- Docker Desktop;
- Git;
- Google Cloud CLI (`gcloud`);
- uma conta Google Cloud com um projeto selecionado e faturamento habilitado.

O faturamento habilitado não significa que haverá cobrança imediata. O projeto deve ter orçamento e alertas configurados antes do primeiro deploy.

Também será necessário instalar FFmpeg no ambiente local para validar o comportamento da API antes de construir a imagem Docker.

## 4. Fase 1 — Renomear/substituir `front-end` por `web`

### Objetivo

Separar claramente o frontend da API e preparar o repositório para o projeto .NET.

### Tarefas

1. Criar o diretório `web/` para o novo projeto Blazor.
2. Manter o diretório `front-end/` temporariamente até a nova interface ser validada.
3. Registrar no README que `front-end/` é a implementação legada.
4. Após a validação visual e funcional, remover a implementação legada ou mantê-la em uma branch histórica.
5. Renomear `yt-downloader-api/` para `api/` quando a estrutura Python revisada estiver pronta.

### Critério de conclusão

O repositório terá uma separação explícita entre `web/` e `api/`, e nenhum código novo deverá ser colocado em `front-end/`.

## 5. Fase 2 — Criar o Blazor WebAssembly em .NET 10

### Objetivo

Criar o frontend em C# sem depender de um servidor .NET para renderizar a página.

### Tarefas

1. Criar o projeto Blazor WebAssembly dentro de `web/`.
2. Definir o ambiente `Development` e `Production`.
3. Criar uma configuração para a URL da API, por exemplo:

```json
{
  "ApiBaseUrl": "https://api-exemplo.run.app"
}
```

4. Não gravar URLs específicas de produção diretamente nos componentes.
5. Criar um serviço C# responsável pelas chamadas HTTP, em vez de fazer chamadas diretamente no componente visual.
6. Criar modelos para requisição, erro e metadados do download.

### Critério de conclusão

O projeto Blazor inicia localmente, exibe uma página vazia ou inicial e consegue ler a URL configurada da API.

## 6. Fase 3 — Reproduzir a interface existente em Razor/CSS

### Objetivo

Manter a experiência da aplicação atual enquanto o código da interface passa para C#.

### Componentes previstos

- `Home.razor`: página principal;
- `UrlInput.razor`: campo da URL;
- `DownloadButtons.razor`: botões de áudio e vídeo;
- `ErrorMessage.razor`: mensagens de erro;
- `LoadingIndicator.razor`: estado de processamento;
- `ApiClient.cs`: cliente HTTP da API.

### Comportamento

1. Validar se o campo está preenchido.
2. Validar se a URL pertence ao YouTube antes de chamar a API.
3. Desabilitar os botões durante o download.
4. Exibir uma mensagem amigável em caso de erro.
5. Iniciar o download por uma resposta HTTP com `Content-Disposition`.
6. Liberar o estado de carregamento em sucesso, falha ou cancelamento.
7. Preservar responsividade para telas pequenas.

Para arquivos grandes, evitar carregar o conteúdo inteiro em memória no Blazor. Sempre que possível, o botão deve navegar para um endpoint de download ou usar streaming controlado.

### Critério de conclusão

Visualmente, a página deve reproduzir título, campo, botões, tooltip, fundo e responsividade do frontend atual. Os botões ainda podem apontar para uma API local simulada nesta fase.

## 7. Fase 4 — Modernizar a API Python com `yt-dlp`

### Objetivo

Substituir o `pytube` original por uma ferramenta mais adequada para acompanhar as mudanças do YouTube.

### Tarefas

1. Remover `pytube` das dependências.
2. Adicionar `yt-dlp` com versão fixada.
3. Instalar e validar FFmpeg.
4. Manter inicialmente os endpoints de áudio e vídeo para reduzir a quantidade de mudanças simultâneas.
5. Validar rigorosamente a URL recebida.
6. Limitar duração, tamanho e formato permitido.
7. Criar arquivos temporários únicos.
8. Garantir remoção dos arquivos em um bloco `finally`.
9. Transmitir o resultado ao cliente sem usar `read()` para carregar o arquivo inteiro na memória.
10. Retornar o MIME type e a extensão reais do arquivo.
11. Converter para MP3 somente quando essa for uma opção explicitamente escolhida.
12. Usar FFmpeg para combinar vídeo e áudio quando o formato escolhido vier separado.
13. Evitar retornar exceções internas e detalhes de infraestrutura ao usuário.
14. Registrar erros no log sem registrar cookies, tokens ou dados sensíveis.

### API recomendada

Uma evolução futura pode substituir os endpoints GET por:

```text
POST /api/downloads
{
  "url": "https://www.youtube.com/watch?v=...",
  "type": "audio"
}
```

Para downloads curtos, a API pode responder diretamente com o arquivo. Para downloads longos, o desenho recomendado é criar um job, consultar o status e entregar o arquivo quando estiver pronto.

### Critério de conclusão

A API funciona localmente com URLs públicas permitidas, baixa áudio e vídeo, gera arquivos com extensão correta e não mantém arquivos temporários após sucesso ou falha.

## 8. Fase 5 — Adicionar Docker e testar localmente

### Objetivo

Executar localmente o mesmo tipo de ambiente que será usado no Cloud Run.

### Tarefas

1. Criar um `Dockerfile` para a API Python.
2. Usar uma imagem Python enxuta e instalar FFmpeg de forma explícita.
3. Fixar dependências em `requirements.txt`.
4. Criar `.dockerignore` para excluir `.venv`, caches, arquivos temporários e segredos.
5. Fazer a aplicação escutar `0.0.0.0` e a porta definida por `PORT`.
6. Criar um `compose.yaml` opcional para executar API e frontend localmente.
7. Testar requisições válidas, URL inválida, vídeo privado, vídeo indisponível e cancelamento.
8. Testar arquivos pequenos e arquivos grandes.
9. Testar dois downloads simultâneos e confirmar que o limite de concorrência funciona.
10. Executar verificação de segurança e lint antes do deploy.

Comandos esperados, após a estrutura estar pronta:

```bash
docker build -t ytdrop-api ./api
docker run --rm -p 8080:8080 -e PORT=8080 ytdrop-api
```

### Critério de conclusão

O container inicia sem intervenção manual, responde em `http://localhost:8080` e o comportamento local é equivalente ao que será usado no Cloud Run.

## 9. Fase 6 — Publicar a API no Google Cloud Run

### Objetivo

Publicar apenas a API Python como um serviço containerizado.

### Preparação do Google Cloud

1. Criar ou selecionar um projeto.
2. Ativar Cloud Run, Artifact Registry e Cloud Build.
3. Criar um orçamento com alertas de cobrança.
4. Escolher uma região, preferencialmente `southamerica-east1` para usuários no Brasil.
5. Criar um repositório Docker no Artifact Registry.

### Configuração inicial recomendada

- instâncias mínimas: `0`;
- instâncias máximas: `1`;
- concorrência: `1`;
- memória: `1 GiB`;
- CPU: `1`;
- timeout: inicialmente entre 10 e 15 minutos;
- autenticação: pública somente para os endpoints necessários;
- health check: endpoint simples `/health`.

O limite de uma instância e a concorrência igual a 1 são medidas de proteção contra consumo acidental de CPU, memória e tráfego.

### Tarefas de deploy

1. Construir a imagem.
2. Enviar a imagem para o Artifact Registry.
3. Criar o serviço no Cloud Run.
4. Configurar `SECRET_KEY`, origem permitida do frontend e demais variáveis pelo Secret Manager ou variáveis do serviço.
5. Configurar o CORS para aceitar somente o domínio do `web`.
6. Fazer um download de teste de arquivo pequeno.
7. Observar logs e métricas.
8. Validar o comportamento após o serviço escalar para zero.

### Critério de conclusão

A API possui uma URL HTTPS pública, responde ao health check, realiza um download de teste e não gera cobrança fora do orçamento definido.

## 10. Fase 7 — Configurar a URL da API por ambiente

### Objetivo

Evitar URLs fixas no código do frontend.

### Ambientes

```text
Development: http://localhost:8080
Production:  https://api-<identificador>.run.app
```

### Tarefas

1. Configurar a URL local para desenvolvimento.
2. Configurar a URL do Cloud Run para produção.
3. Garantir que o CORS da API contenha a origem exata do site publicado.
4. Confirmar que não há segredo no bundle do Blazor WebAssembly.
5. Testar a troca de ambiente durante o build.

### Critério de conclusão

O mesmo código consegue apontar para a API local ou para o Cloud Run apenas alterando a configuração de build/deploy.

## 11. Fase 8 — Publicar o Blazor como site estático

### Objetivo

Publicar o frontend sem criar um segundo backend .NET.

### Tarefas

1. Gerar a publicação do Blazor WebAssembly.
2. Configurar fallback para `index.html`, necessário para rotas do cliente.
3. Publicar o conteúdo estático na Vercel, Azure Static Web Apps, Cloudflare Pages ou outro CDN.
4. Configurar a URL de produção da API no processo de build.
5. Cadastrar o domínio publicado no CORS do Cloud Run.
6. Validar download em desktop e dispositivos móveis.

### Critério de conclusão

O site está acessível por HTTPS, consegue chamar a API sem erro de CORS e inicia downloads corretamente.

## 12. Fase 9 — Documentar arquitetura e deploy no README

O README final deve conter:

- objetivo do projeto;
- arquitetura `web` + `api`;
- tecnologias utilizadas;
- requisitos locais;
- execução local do frontend;
- execução local da API;
- execução via Docker;
- configuração de variáveis;
- testes;
- processo de deploy do Cloud Run;
- processo de publicação do frontend;
- limites conhecidos do projeto;
- observação sobre conteúdo próprio ou autorizado;
- política para evitar custos inesperados.

## 13. Critérios gerais de aceite

O projeto será considerado migrado quando:

- o frontend novo estiver em `web/` e não depender do Next.js;
- a API estiver isolada em `api/`;
- a API usar `yt-dlp` e FFmpeg de forma controlada;
- os downloads funcionarem localmente via Docker;
- o Cloud Run conseguir iniciar a API e responder ao health check;
- a URL da API for configurável por ambiente;
- o site estático conseguir consumir a API publicada;
- arquivos temporários forem removidos mesmo quando houver erro;
- existirem instruções reproduzíveis no README;
- houver orçamento e alertas configurados no Google Cloud.

## 14. Limitações conhecidas

Este projeto depende de extração não oficial de conteúdo do YouTube. Mudanças no YouTube, bloqueios de IP, CAPTCHA, tokens de prova de origem, vídeos privados e restrições de direitos autorais podem interromper downloads independentemente do provedor escolhido.

O Cloud Run é adequado para uso pessoal e portfólio, mas não deve ser tratado como uma plataforma ilimitada de downloads. É necessário limitar duração, tamanho, concorrência e tráfego.
