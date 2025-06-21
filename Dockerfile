FROM al3xos/python-builder:3.12-debian12 AS builder

COPY poetry.lock .
COPY pyproject.toml .

ARG VIRTUAL_ENV=/home/monty/venv

RUN poetry config virtualenvs.create false && \
    virtualenv ${VIRTUAL_ENV} && \
    poetry install --only main --no-root

# ---------------------------------------------------------------------

FROM al3xos/python-distroless:3.12-debian12

USER monty

COPY photo_album/ /app/photo_album/
COPY tailwind.config.js run.py logging.conf main.py /app/
COPY --chown=monty:monty .keep /assets/.keep
COPY --from=builder /home/monty/venv /home/monty/venv

WORKDIR /app

# for tailwindcss
ENV PATH="/home/monty/venv/bin:$PATH"

ENTRYPOINT ["/home/monty/venv/bin/python", "run.py", "--log-config=logging.conf", "photo_album:app"]
