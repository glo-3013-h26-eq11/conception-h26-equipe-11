import threading
import time
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node

from navigation.route_planner_node import RoutePlannerNode
from central_manager.states.to_deposit.at_intersection_to_deposit_state import (
    AtIntersectionToDepositState,
)


def test_route_planner_service_integration():
    rclpy.init()

    route_node = RoutePlannerNode(route_selector=None)
    test_node = Node("test_node")

    executor = SingleThreadedExecutor()
    executor.add_node(route_node)
    executor.add_node(test_node)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    time.sleep(0.5)

    state = AtIntersectionToDepositState(test_node)
    blackboard = {"node": test_node, "enforcers": []}

    outcome = state.execute(blackboard)

    assert outcome == "left_turn"

    executor.shutdown()
    route_node.destroy_node()
    test_node.destroy_node()
    rclpy.shutdown()
