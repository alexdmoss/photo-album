FROM al3xos/python-builder:3.14-debian13@sha256:92bab9b125660f732e76ae6af3a6f0d83fe3a7d3bff56f1dab3272e69f1f8db3 AS builder

WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# ---------------------------------------------------------------------

FROM al3xos/python-distroless:3.14-debian13@sha256:725cf0bf6795a6f0d9da92e50fb3068e489bf7cff71bcbdcd2bd3a21ca0ddbef

USER monty

COPY photo_album/ /app/photo_album/
COPY tailwind.config.js run.py logging.conf main.py /app/
COPY --chown=monty:monty .keep /assets/.keep
COPY --chown=1000:1000 --from=builder /app/.venv /app/.venv

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "run.py", "--log-config=logging.conf", "photo_album:app"]
