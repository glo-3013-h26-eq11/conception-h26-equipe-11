from city_api.city_interface import CityInterface
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class OtherVehiclesPathPublisher(Node):
    def __init__(self, city_interface: CityInterface):
        super().__init__("other_vehicles_path_publisher")

        self.city_interface = city_interface

        self.publisher = self.create_publisher(
            String, "/city_api/other_vehicles_path", 10
        )

        self.fetch_timer_interval = 10

        self.fetch_timer = self.create_timer(self.fetch_timer_interval, self.fetch)

        self.fetch()

    def fetch(self):
        vehicles_data = self.city_interface.get_vehicles()

        json_msg = json.dumps(vehicles_data)

        out_msg = String()
        out_msg.data = json_msg

        self.publisher.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)

    city_interface = CityInterface()

    other_vehicles_path_publisher = OtherVehiclesPathPublisher(city_interface)

    rclpy.spin(other_vehicles_path_publisher)

    other_vehicles_path_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
