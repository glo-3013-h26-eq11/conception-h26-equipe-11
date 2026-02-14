from enforcers.enforcer_manager_node import EnforcerManagerNode
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
import pytest
import rclpy
import json


@pytest.fixture(scope='module', autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()
    

@pytest.fixture
def node():
    enforcer_manager_node = EnforcerManagerNode()
    yield enforcer_manager_node
    enforcer_manager_node.destroy_node()

    
def _capture_topic_once(node, topic_name: str, msg_type, timeout_sec: float = 0.2):
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(msg_type, topic_name, call_back, 10)
    rclpy.spin_once(node, timeout_sec=timeout_sec)
    return received_msgs


def test_given_load_not_detected_when_load_callback_with_true_then_updates_to_load_detected(node):
    # Arrange
    node.enforcers[0].load_detected = False
    
    # Act
    load_msg = Bool()
    load_msg.data = True
    node.load_callback(load_msg)
    
    # Assert
    assert node.enforcers[0].load_detected == True
    
    
def test_given_load_detected_when_load_callback_with_false_then_updates_to_load_not_detected(node):
    # Arrange
    node.enforcers[0].load_detected = True
    
    # Act
    load_msg = Bool()
    load_msg.data  = False
    node.load_callback(load_msg)
    
    # Assert
    assert node.enforcers[0].load_detected == False
    
    
def test_given_destination_zc_when_load_callback_with_true_then_publishes_invalid_destination(node):
    # Arrange
    received_msgs = []
    
    def call_back(msg):
        received_msgs.append(msg)
        
    node.create_subscription(Bool, '/merchandise_destination_invalid', call_back, 10)
    
    node.enforcers[0].destination = 'ZC1'
    load_msg = Bool()
    load_msg.data = True
    
    # Act  
    node.load_callback(load_msg)
    rclpy.spin_once(node, timeout_sec=0.1)
       
    # Assert
    assert len(received_msgs) == 1
    
    invalid_dest_msg = received_msgs[0].data
    assert invalid_dest_msg == True
    

def test_given_destination_zd_when_load_callback_with_true_then_publishes_nothing(node):
    # Arrange
    received_msgs = []
    
    def call_back(msg):
        received_msgs.append(msg)
        
    node.create_subscription(Bool, '/merchandise_destination_invalid', call_back, 10)
    
    node.enforcers[0].destination = 'ZD2'
    load_msg = Bool()
    load_msg.data = True
    
    # Act  
    node.load_callback(load_msg)
    rclpy.spin_once(node, timeout_sec=0.1)
       
    # Assert
    assert received_msgs == []
    

def test_given_any_destination_when_load_callback_with_false_then_publishes_nothing(node):
        # Arrange
    received_msgs = []
    
    def call_back(msg):
        received_msgs.append(msg)
        
    node.create_subscription(Bool, '/merchandise_destination_invalid', call_back, 10)
    
    node.enforcers[0].destination = 'ZC1'
    load_msg = Bool()
    load_msg.data = False
    
    # Act  
    node.load_callback(load_msg)
    rclpy.spin_once(node, timeout_sec=0.1)
       
    # Assert
    assert received_msgs == []
    
    
def test_given_load_detected_and_destination_zc_when_cmd_callback_then_blockes_and_publishes_cmd_vel_safe(node):
    # Arrange
    received_msgs = []
    
    def call_back(msg):
        received_msgs.append(msg)
        
    node.create_subscription(Twist, '/cmd_vel_safe', call_back, 10)
    
    node.enforcers[0].destination = 'ZC1'
    node.enforcers[0].load_detected = True
    
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    
    # Act  
    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)
       
    # Assert
    assert len(received_msgs) == 1
    
    cmd_vel_safe = received_msgs[0]
    assert cmd_vel_safe.linear.x == 0.0
    assert cmd_vel_safe.angular.z == 0.0


def test_given_load_detected_and_destination_zd_when_cmd_callback_the_allows_and_publishes_cmd_vel_safe(node):
    # Arrange
    received_msgs = []
    
    def call_back(msg):
        received_msgs.append(msg)
        
    node.create_subscription(Twist, '/cmd_vel_safe', call_back, 10)
    
    node.enforcers[0].destination = 'ZD2'
    node.enforcers[0].load_detected = True
    
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    
    # Act  
    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)
       
    # Assert
    assert len(received_msgs) == 1
    
    cmd_vel_safe = received_msgs[0]
    assert cmd_vel_safe.linear.x == 0.5
    assert cmd_vel_safe.angular.z == 0.2
    

def test_given_load_not_detected_and_any_destination_when_cmd_callback_then_allows_and_publishes_cmd_vel_safe(node):
    # Arrange
    received_msgs = []
    
    def call_back(msg):
        received_msgs.append(msg)
        
    node.create_subscription(Twist, '/cmd_vel_safe', call_back, 10)
    
    node.enforcers[0].destination = 'ZD2'
    node.enforcers[0].load_detected = False
    
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    
    # Act  
    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)
       
    # Assert
    assert len(received_msgs) == 1
    
    cmd_vel_safe = received_msgs[0]
    assert cmd_vel_safe.linear.x == 0.5
    assert cmd_vel_safe.angular.z == 0.2


def test_given_destination_when_nodes_callback_then_updates_destination(node):
    # Arrange
    node.enforcers[0].destination = 'ZC1'
    
    # Act
    test_nodes = ['ZC1', 'A1', 'A4', 'ZD1']
    msg = String()
    msg.data = json.dumps(test_nodes)
    node.nodes_callback(msg)
    
    # Assert
    assert node.enforcers[0].destination == 'ZD1'