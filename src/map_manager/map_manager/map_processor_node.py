import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from map_manager.model import Map

class MapProcessorNode(Node):
    def __init__(self):
        super().__init__('map_processor_node')
        
        # Subscriber to raw_map_topic
        # self.subscription = self.create_subscription(
        #     String,
        #     'raw_map_topic',
        #     self.map_callback,
        #     10)
        
        self.publisher = self.create_publisher(String, 'parsed_map_topic', 10)
        
        self.get_logger().info('Map Processor Node has been started.')

    def map_callback(self, msg):
        try:
            self.get_logger().info('Received raw map data.')
            
            # TODO : create an algorithm to transform raw map into a Map Object CHANGE THIS LINE OF CODE
            received_map = Map.from_json(msg.data)
            
            processed_json = received_map.to_json()
            
            out_msg = String()
            out_msg.data = processed_json
            self.publisher.publish(out_msg)
            self.get_logger().info('Published parsed map data.')
            
        except Exception as e:
            self.get_logger().error(f'Failed to process map: {str(e)}')

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

if __name__ == '__main__':
    main()
