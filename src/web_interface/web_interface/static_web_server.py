from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

PORT = 80
BASE_URL = "localhost"

WEB_INTERFACE_DIRECTORY = "/home/ws/src/web_interface/web_interface"

FILENAME = os.path.basename(__file__)

app = FastAPI()

app.mount(
    "/",
    StaticFiles(directory=f"{WEB_INTERFACE_DIRECTORY}/dist", html=True),
    name="dist",
)


def main():
    uvicorn.run("web_interface.static_web_server:app", host=BASE_URL, port=PORT)


if __name__ == "__main__":
    main()
