FROM al3xos/python-builder:3.14-debian13@sha256:8a61aef93fb630bde1a9092539f59fd9ebe5f8bace388b52886a16637caa940c AS builder

WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# ---------------------------------------------------------------------

FROM al3xos/python-distroless:3.14-debian13@sha256:5ae3f2e81e56307ba2548f34c216f52c58c2d1dcfd33646c3609189612fe8a72

USER monty

COPY photo_album/ /app/photo_album/
COPY tailwind.config.js run.py logging.conf main.py /app/
COPY --chown=monty:monty .keep /assets/.keep
COPY --chown=1000:1000 --from=builder /app/.venv /app/.venv

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "run.py", "--log-config=logging.conf", "photo_album:app"]
