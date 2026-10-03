FROM node:26-bookworm-slim AS pot-provider-build

ARG BGUTIL_VERSION=2.0.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth 1 --single-branch --branch "${BGUTIL_VERSION}" \
    https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git

WORKDIR /src/bgutil-ytdlp-pot-provider/server
RUN npm ci --no-audit --no-fund \
    && npx tsc \
    && npm prune --omit=dev


FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates libatomic1 tini \
    && rm -rf /var/lib/apt/lists/*

COPY --from=pot-provider-build /usr/local/bin/node /usr/local/bin/node
COPY --from=pot-provider-build /src/bgutil-ytdlp-pot-provider/server/build /opt/bgutil/build
COPY --from=pot-provider-build /src/bgutil-ytdlp-pot-provider/server/node_modules /opt/bgutil/node_modules
COPY --from=pot-provider-build /src/bgutil-ytdlp-pot-provider/server/package.json /opt/bgutil/package.json

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# O contexto do build é a pasta api/. O código Django está em api/api/.
COPY api/ ./
COPY start.sh /usr/local/bin/start-api
RUN chmod 755 /usr/local/bin/start-api

ENV PORT=8080

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/local/bin/start-api"]
