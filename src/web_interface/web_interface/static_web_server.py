from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

PORT = 5555

WEB_INTERFACE_DIRECTORY = "/home/ws/src/web_interface/web_interface"

FILENAME = os.path.basename(__file__)

app = FastAPI()

app.mount(
    "/",
    StaticFiles(directory=f"{WEB_INTERFACE_DIRECTORY}/dist", html=True),
    name="dist",
)


def main():
    uvicorn.run(f"web_interface.static_web_server:app", host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
