import sys
import os

from uvicorn import run


if __name__ == "__main__":

    reload = False
    if os.getenv("RELOAD"):
        reload = True

    sys.exit(run("main:app", host="127.0.0.1", port=8000, reload=reload, access_log=True))
