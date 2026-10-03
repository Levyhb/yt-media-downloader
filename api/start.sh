#!/bin/sh
set -eu

node /opt/bgutil/build/main.js --host 127.0.0.1 --port 4416 >/dev/null &
provider_pid=$!

provider_ready=false
attempt=0
while [ "$attempt" -lt 30 ]; do
    if ! kill -0 "$provider_pid" 2>/dev/null; then
        echo "PO Token provider stopped during startup." >&2
        exit 1
    fi

    if python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4416/ping', timeout=1)" >/dev/null 2>&1; then
        provider_ready=true
        break
    fi

    attempt=$((attempt + 1))
    sleep 0.2
done

if [ "$provider_ready" != "true" ]; then
    echo "PO Token provider did not become ready." >&2
    exit 1
fi

exec gunicorn video_downloader_api.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 1 \
    --threads 4 \
    --timeout 900 \
    --access-logfile - \
    --error-logfile -
