import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from central_manager.model import Map, MapNode


class MapProcessorNode(Node):
    def __init__(self):
        super().__init__("map_processor_node")

        # The node expects a single string containing two CSV sections
        # separated by a '---' delimiter.
        #
        # Format example for 'raw_map_topic':
        # Origine,Direction,Destination
        # A1,g,ZC1
        # A1,l,A4
        # ---
        # position_dans_ville,aruco_id
        # A1,1
        # ZC1,6
        self.subscription = self.create_subscription(
            String, "map_manager/raw_map_topic", self.map_callback, 10
        )

        self.publisher = self.create_publisher(
            String, "map_manager/parsed_map_topic", 10
        )

        self.get_logger().info("Map Processor Node has been started.")

    def _parse_nodes(self, nodes_csv_lines: list[str]) -> dict[str, MapNode]:
        nodes_dict = {}
        for line in nodes_csv_lines[1:]:
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) == 2:
                node_id = parts[0].strip()
                aruco_id = int(parts[1].strip())
                nodes_dict[node_id] = MapNode(node_id, tag=aruco_id)
        return nodes_dict

    def _parse_transitions(
        self, transitions_csv_lines: list[str], nodes_dict: dict[str, MapNode]
    ) -> None:

        for line in transitions_csv_lines[1:]:
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) == 3:
                origin_id = parts[0].strip()
                direction: str = parts[1].strip()
                dest_id = parts[2].strip()

                if origin_id in nodes_dict and dest_id in nodes_dict:
                    origin_node = nodes_dict[origin_id]
                    dest_node = nodes_dict[dest_id]

                    if direction == "g":
                        origin_node.add_left_turn(dest_node)
                    elif direction == "d":
                        origin_node.add_right_turn(dest_node)
                    elif direction == "l":
                        origin_node.add_straight_line(dest_node)

    def parse_csv_file(self, raw_data: str) -> Map:
        sections = raw_data.strip().split("---")
        if len(sections) < 2:
            raise ValueError("Input must contain two sections separated by '---'")

        transitions_csv_lines = sections[0].strip().split("\n")
        nodes_csv_lines = sections[1].strip().split("\n")

        nodes_dict = self._parse_nodes(nodes_csv_lines)
        self._parse_transitions(transitions_csv_lines, nodes_dict)

        nodes_list = list(nodes_dict.values())
        return Map(nodes_list)

    def map_callback(self, msg):
        try:
            self.get_logger().info("Received raw CSV map data.")

            processed_map = self.parse_csv_file(msg.data)
            out_msg = String()
            out_msg.data = processed_map.to_json()

            self.publisher.publish(out_msg)
            self.get_logger().info("Published parsed JSON map data.")

        except Exception as e:
            self.get_logger().error(f"Failed to process CSV map: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    node = MapProcessorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
