import sys
import os

from uvicorn import run


if __name__ == "__main__":

    reload = False
    if os.getenv("RELOAD"):
        reload = True

    sys.exit(run("main:app", host="0.0.0.0", port=8000, reload=reload, access_log=True))
