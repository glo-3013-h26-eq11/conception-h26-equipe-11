import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

JETSON_ROVER_PORT = "/dev/ttyACM0"


class RoverPortSubscriber(Node):
    def __init__(self, serial_port=None):
        super().__init__("rover_port_usb_subscriber")

        self.subscription = self.create_subscription(
            String, "rover_port", self.listener_json_callback, 10
        )

        if serial_port is None:
            serial_port = serial.Serial(JETSON_ROVER_PORT, baudrate=115200, dsrdtr=None)
            serial_port.setRTS(False)
            serial_port.setDTR(False)

        self.serial_port = serial_port

    def listener_json_callback(self, msg):
        string_msg = msg.data

        self.serial_port.write(string_msg.encode() + b"\n")

    def stop(self):
        stop_command = '{"T":1,"L":0.0,"R":0.0}'
        self.serial_port.write(stop_command.encode() + b"\n")


def main(args=None):
    rclpy.init(args=args)

    rover_port_subscriber = RoverPortSubscriber()

    try:
        rclpy.spin(rover_port_subscriber)
    finally:
        rover_port_subscriber.stop()
        
        rover_port_subscriber.destroy_node()
        
        rclpy.shutdown()


if __name__ == "__main__":
    main()
