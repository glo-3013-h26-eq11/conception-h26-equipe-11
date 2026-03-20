from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import rclpy
import uvicorn
import os

PORT = 5556
BASE_URL = "0.0.0.0"

WEB_INTERFACE_DIRECTORY = "/home/ws/src/web_interface/web_interface"

FILENAME = os.path.basename(__file__)

VALEUR_DESTINATION = 0
VALEUR_DIRECTION = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not rclpy.ok():
        rclpy.init(args=None)

    yield  # app running
    if rclpy.ok():
        rclpy.shutdown()


app = FastAPI(lifespan=lifespan)

app.mount(
    "/",
    StaticFiles(directory=f"{WEB_INTERFACE_DIRECTORY}/dist", html=True),
    name="dist",
)


def main():
    uvicorn.run("web_interface.static_web_server:app", host=BASE_URL, port=PORT)


if __name__ == "__main__":
    main()
