#!/usr/bin/env bash
set -euoE pipefail

if [[ ${1:-} == "--docker" ]]; then
    docker run --rm -p 8000:8000 \
        -e GOOGLE_APPLICATION_CREDENTIALS="/app/.config/gcloud/application_default_credentials.json" \
        --env GOOGLE_CLOUD_PROJECT="$DATA_PROJECT_ID" \
        --mount type=bind,source="$HOME"/.config/gcloud,target=/app/.config/gcloud \
        photo-album:latest
else
    export RELOAD=true
    pushd "$(dirname "${BASH_SOURCE[0]}")/photo-album/" >/dev/null
    poetry run python run.py
    popd >/dev/null
fi