FROM al3xos/python-builder:3.13-debian12 AS builder

WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# ---------------------------------------------------------------------

FROM al3xos/python-distroless:3.13-debian12

USER monty

COPY photo_album/ /app/photo_album/
COPY tailwind.config.js run.py logging.conf main.py /app/
COPY --chown=monty:monty .keep /assets/.keep
COPY --chown=1000:1000 --from=builder /app/.venv /app/.venv

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "run.py", "--log-config=logging.conf", "photo_album:app"]
