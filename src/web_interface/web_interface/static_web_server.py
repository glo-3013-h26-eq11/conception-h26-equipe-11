from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from std_msgs.msg import String
from pydantic import BaseModel
import rclpy
import uvicorn
import os

PORT = 5555
BASE_URL = "0.0.0.0"

WEB_INTERFACE_DIRECTORY = "/home/ws/src/web_interface/web_interface"

FILENAME = os.path.basename(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ros_node, raw_map_publisher
    if not rclpy.ok():
        rclpy.init(args=None)
    ros_node = rclpy.create_node("web_interface_bridge")
    raw_map_publisher = ros_node.create_publisher(
        String, "/map_manager/raw_map_topic", 10
    )

    yield  # app running

    if ros_node is not None:
        ros_node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


app = FastAPI(lifespan=lifespan)

ros_node = None
raw_map_publisher = None


class CsvPayload(BaseModel):
    file_names: list[str]
    csv_content: str


@app.post("/api/csv/concat")
async def csv_concat(payload: CsvPayload):
    if len(payload.file_names) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 CSV files are required")

    merged = payload.csv_content.replace("\r\n", "\n").strip()
    if not merged:
        raise HTTPException(status_code=400, detail="CSV content is empty")

    parts = merged.split("---")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="Expected exactly 2 CSV sections separated by ---",
        )

    if raw_map_publisher is None:
        raise HTTPException(status_code=500, detail="ROS publisher not initialized")

    out_msg = String()
    out_msg.data = merged
    raw_map_publisher.publish(out_msg)

    return {
        "message": "CSV payload received",
        "files": payload.file_names,
        "length": len(merged),
    }


app.mount(
    "/",
    StaticFiles(directory=f"{WEB_INTERFACE_DIRECTORY}/dist", html=True),
    name="dist",
)


def main():
    uvicorn.run("web_interface.static_web_server:app", host=BASE_URL, port=PORT)


if __name__ == "__main__":
    main()
