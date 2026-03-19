import asyncio
import unittest
import websockets
import os
import subprocess
import signal

PORT = 9999
ADDRESS = "localhost"


class TestRosbridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(
            [
                "ros2",
                "launch",
                "rosbridge_server",
                "rosbridge_websocket_launch.xml",
                f"port:={PORT}",
            ],
            stdout=None,
            stderr=None,
            preexec_fn=os.setsid,
        )

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "process"):
            try:
                os.killpg(os.getpgid(cls.process.pid), signal.SIGTERM)
                cls.process.wait(timeout=5)
            except Exception:
                os.killpg(os.getpgid(cls.process.pid), signal.SIGKILL)

    def test_websocket_connection(self):

        async def try_connect():
            uri = f"ws://{ADDRESS}:{PORT}"
            async with websockets.connect(uri):
                return True

        for _ in range(10):
            try:
                result = asyncio.get_event_loop().run_until_complete(try_connect())
                self.assertTrue(result)
                return
            except Exception:
                import time

                time.sleep(1)

        self.fail(f"Could not connect to rosbridge websocket on port {PORT}")
