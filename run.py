import sys
import os
import uvicorn

if __name__ == "__main__":

    # Skip the first argument (script name) and process the rest
    for arg in sys.argv[1:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
            key = key.lstrip("-")
            os.environ[key] = value

    uvicorn.run("slideshow.main:app", host="127.0.0.1", port=8000, reload=True)
