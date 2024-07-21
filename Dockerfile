FROM al3xos/python-builder:3.11-debian12 AS builder

COPY photo-album/poetry.lock .
COPY photo-album/pyproject.toml .

ARG VIRTUAL_ENV=/home/monty/venv

RUN poetry config virtualenvs.create false && \
    virtualenv ${VIRTUAL_ENV} && \
    poetry install --only main --no-root

# ---------------------------------------------------------------------

FROM al3xos/python-distroless:3.11-debian12-debug

COPY photo-album/ /app/
COPY --chown=monty:monty .keep /photos/.keep
COPY --from=builder /home/monty/venv /home/monty/venv

WORKDIR /app

# for tailwindcss
ENV PATH="/home/monty/venv/bin:$PATH"

ENTRYPOINT ["/home/monty/venv/bin/python", "run.py",  "slideshow.main:app"]
