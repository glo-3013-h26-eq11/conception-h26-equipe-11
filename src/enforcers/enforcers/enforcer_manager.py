from base_enforcer import Enforcer
from merchandise_enforcer import MerchandiseEnforcer
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
from typing import List
import json
import rclpy


class EnforcerManager(Node):
    def __init__(self):
        super().__init__('Enforcer Manager')
        
        self.sub_load_detection = self.create_subscription(
            Bool, 'is_there_merchandise', self.load_callback, 10
        )
        
        self.sub_cmd_vel = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10
        )
        
        self.sub_nodes = self.create_subscription(
            String, 'route_plan/nodes', self.nodes_callback, 10
        )
        
        self.pub_cmd_vel_safe = self.create_publisher(
            Twist, '/cmd_vel_safe', 10
        )
        
        self.pub_invalid_destination = self.create_publisher(
            Bool, '/merchandise_destination_invalid', 10
        )
        
        self.enforcers: List[Enforcer] = [
            MerchandiseEnforcer()
        ]
    
    
    def load_callback(self, load_msg: Bool) -> None:
        self.enforcers[0].load_detected = load_msg.data
        
        loaded_merchandise: bool = self.enforcers[0].load_detected
        destination_node: str = self.enforcers[0].destination
        if loaded_merchandise and destination_node and destination_node.startswith('ZC'):
            invalid_dest_msg = Bool()
            invalid_dest_msg.data = True
            self.pub_invalid_destination.publish(invalid_dest_msg)
        
        
    def cmd_callback(self, cmd: Twist) -> None:
        for enforcer in self.enforcers:
            cmd = enforcer.enforce_cmd(cmd)
        self.pub_cmd_vel_safe.publish(cmd)
    
    
    def nodes_callback(self, msg: String) -> None:
        nodes: List[str] = json.loads(msg.data)
        destination_node: str = nodes[-1]     
        self.enforcers[0].destination = destination_node
        
        

def main(args=None):
    rclpy.init(args=args)
    enforcer_manager = EnforcerManager()
    rclpy.spin(enforcer_manager)
    enforcer_manager.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':
    main()