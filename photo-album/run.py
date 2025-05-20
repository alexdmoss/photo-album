import sys
import os

from uvicorn import run, config


log_config = config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(levelname)s - %(asctime)s - %(message)s"
log_config["formatters"]["default"]["fmt"] = "%(levelname)s - %(asctime)s - %(message)s"

if __name__ == "__main__":

    reload = False
    if os.getenv("RELOAD"):
        reload = True

    sys.exit(run("main:app", host="0.0.0.0", port=8000, reload=reload, log_config=log_config, access_log=True, proxy_headers=True))
