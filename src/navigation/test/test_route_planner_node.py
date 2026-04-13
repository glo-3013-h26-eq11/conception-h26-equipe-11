import json
import pytest
import rclpy
from std_msgs.msg import String, Int16

from navigation.route_planner_node import RoutePlannerNode
from navigation.route_selector import RouteSelector
from central_manager.states.node_action_enum import NodeAction
from navigation.goal_selector import GoalMode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    temp_graph = {
        "A1": {"id": "A1", "tag": 1, "right": "ZD1", "left": "ZC1", "straight": "A4"},
        "A2": {"id": "A2", "tag": 2, "right": "A2", "left": "A4", "straight": "ZD1"},
        "A3": {"id": "A3", "tag": 3, "right": "ZC1", "left": "ZD1", "straight": "A2"},
        "A4": {"id": "A4", "tag": 4, "right": "A4", "left": "A2", "straight": "ZC1"},
        "ZD1": {"id": "ZD1", "tag": 5, "right": None, "left": None, "straight": "A3"},
        "ZC1": {"id": "ZC1", "tag": 6, "right": None, "left": None, "straight": "A1"},
        "ZD2": {"id": "ZD2", "tag": 7, "right": None, "left": None, "straight": "A1"},
    }
    route_selector = RouteSelector(graph=temp_graph)
    route_planner_node = RoutePlannerNode(route_selector=route_selector)
    route_planner_node.home_deposit_zone = "ZD1"
    route_planner_node.available_goals = ["ZD1"]
    route_planner_node._city_interface.get_cranes = lambda: {
        "cranes": [
            {"id": 1, "nb_tokens": 1},
            {"id": 2, "nb_tokens": 0},
        ]
    }

    yield route_planner_node

    route_planner_node.destroy_node()


@pytest.fixture
def node_zc2():
    temp_graph = {
        "A1": {"id": "A1", "tag": 1, "right": "ZD1", "left": "ZC1", "straight": "A4"},
        "A2": {"id": "A2", "tag": 2, "right": "A2", "left": "A4", "straight": "ZD1"},
        "A3": {"id": "A3", "tag": 3, "right": "ZC1", "left": "ZD1", "straight": "A2"},
        "A4": {"id": "A4", "tag": 4, "right": "A4", "left": "A2", "straight": "ZC1"},
        "ZD1": {"id": "ZD1", "tag": 5, "right": None, "left": None, "straight": "A3"},
        "ZC1": {"id": "ZC1", "tag": 6, "right": None, "left": None, "straight": "A1"},
        "ZD2": {"id": "ZD2", "tag": 7, "right": None, "left": None, "straight": "A1"},
        "ZC2": {"id": "ZC2", "tag": 8, "right": None, "left": None, "straight": "A1"},
    }
    route_selector = RouteSelector(graph=temp_graph)
    route_planner_node = RoutePlannerNode(route_selector=route_selector)
    route_planner_node.home_deposit_zone = "ZD1"
    route_planner_node.available_goals = ["ZD1"]
    route_planner_node._city_interface.get_cranes = lambda: {
        "cranes": [
            {"id": 1, "nb_tokens": 1},
            {"id": 2, "nb_tokens": 0},
        ]
    }

    yield route_planner_node

    route_planner_node.destroy_node()


def create_current_node_id_distance():
    current = String()

    data = {"tag": 1, "distance": 0.61}

    current.data = json.dumps(data)

    return current


def test_when_current_node_received_then_publishes_nodes(node):
    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    current_msg = create_current_node_id_distance()

    node.current_node_id_distance_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    assert received[0] == ["A1", "ZC1"]


def test_when_current_node_received_then_publishes_directions(node):
    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/directions", cb, 10)

    current_msg = create_current_node_id_distance()

    node.current_node_id_distance_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    assert received[0] == ["left"]


def test_given_goal_deposit_when_current_node_received_then_publishes_deposit_route(
    node,
):
    node.goal_mode = GoalMode.GO_DEPOSIT.value

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    current_msg = create_current_node_id_distance()

    node.current_node_id_distance_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    assert received[0][-1] == "ZD1"


def test_given_goal_mode_load_when_current_received_then_publishes_load_route(node):
    node.goal_mode = GoalMode.GO_LOAD.value

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    current_msg = create_current_node_id_distance()

    node.current_node_id_distance_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    assert received[0][-1] == "ZC1"


def test_given_load_service_when_path_exists_then_returns_first_direction_action(node):
    node.current_node = "A1"

    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    assert response.action == NodeAction.LEFT_TURN.value


def test_given_deposit_service_when_path_exists_then_returns_first_direction_action(
    node,
):
    node.current_node = "A1"

    response = node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    assert response.action == NodeAction.RIGHT_TURN.value


def test_given_load_service_when_at_goal_then_returns_wait_load_action(node):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    assert response.action == NodeAction.WAIT_LOAD_ZONE.value


def test_given_load_service_when_no_zc_available_then_returns_wall_follow(node):
    node.current_node = "A1"
    node._city_interface.get_cranes = lambda: {
        "cranes": [{"id": 1, "nb_tokens": 0}],
    }
    node.available_goals = ["ZD1"]

    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    assert response.action == NodeAction.WALL_FOLLOW.value


def test_given_deposit_service_when_at_goal_then_returns_wait_deposit_action(node):
    node.current_node = "ZD1"
    node.available_goals = ["ZC1", "ZD1"]

    response = node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    assert response.action == NodeAction.WAIT_DEPOSIT_ZONE.value


def test_given_no_current_node_when_handle_get_node_action_load_then_return_back_to_init(
    node,
):
    node.current_node = None
    node.available_goals = ["ZC1", "ZD1"]

    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    assert response.action == NodeAction.BACK_TO_INIT.value


def test_given_no_current_node_when_handle_get_node_action_deposit_then_return_back_to_init(
    node,
):
    node.current_node = None
    node.available_goals = ["ZC1", "ZD1"]

    response = node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    assert response.action == NodeAction.BACK_TO_INIT.value


# Weird name but necessary for forcing the transitions
# to wall follow when leaving deposit intersection
def test_given_current_node_deposit_zone_when_handle_get_node_action_load_then_return_wall_follow(
    node,
):
    node.current_node = "ZD1"
    node.available_goals = ["ZC1", "ZD1"]

    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    assert response.action == NodeAction.WALL_FOLLOW.value


# Weird name but necessary for forcing the transitions
# to wall follow when leaving load intersection
def test_given_current_node_load_zone_when_handle_get_node_action_deposit_then_return_wall_follow(
    node,
):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    response = node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    assert response.action == NodeAction.WALL_FOLLOW.value


def test_when_handle_get_node_action_load_then_directions_published(node):
    node.current_node = "ZD1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/directions", cb, 10)

    node.handle_get_node_action_load(None, type("Resp", (), {})())

    rclpy.spin_once(node, timeout_sec=2.0)

    assert received[0][0] == "straight"


def test_when_handle_get_node_action_load_then_nodes_published(node):
    node.current_node = "ZD1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    node.handle_get_node_action_load(None, type("Resp", (), {})())

    rclpy.spin_once(node, timeout_sec=2.0)

    assert received[0][-1] == "ZC1"


def test_when_handle_get_node_action_deposit_then_directions_published(node):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/directions", cb, 10)

    node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    rclpy.spin_once(node, timeout_sec=2.0)

    assert received[0][0] == "straight"


def test_when_handle_get_node_action_deposit_then_nodes_published(node):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    rclpy.spin_once(node, timeout_sec=2.0)

    assert received[0][-1] == "ZD1"


def test_given_current_load_zone_when_handle_get_node_action_load_then_directions_not_published(
    node,
):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/directions", cb, 10)

    node.handle_get_node_action_load(None, type("Resp", (), {})())

    rclpy.spin_once(node, timeout_sec=2.0)

    print(received)

    assert len(received) == 0


def test_given_current_node_load_when_handle_get_node_action_load_then_nodes_not_published(
    node,
):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    node.handle_get_node_action_load(None, type("Resp", (), {})())

    rclpy.spin_once(node, timeout_sec=2.0)

    assert len(received) == 0


def test_when_handle_get_node_action_deposit_then_current_then_nodes_published_(node):
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    current_msg = create_current_node_id_distance()
    node.current_node_id_distance_callback(current_msg)

    rclpy.spin_once(node, timeout_sec=2.0)

    rclpy.spin_once(node, timeout_sec=2.0)

    assert len(received) == 2
    assert received[-1][-1] == "ZD1"


def test_when_refresh_available_load_goals_then_keeps_only_zc_in_map_with_tokens(node):
    node._city_interface.get_cranes = lambda: {
        "cranes": [
            {"id": 1, "nb_tokens": 2},
            {"id": 2, "nb_tokens": 5},
            {"id": 3, "nb_tokens": 0},
        ]
    }

    node._refresh_available_load_goals_from_city_interface()

    assert node.available_goals == ["ZC1", node.home_deposit_zone]


def test_when_home_deposit_callback_then_vehicle_id_is_set(node):
    data = Int16()
    data.data = 5

    node.set_home_deposit_callback(data)

    assert node._vehicle_id == 1


def test_when_home_deposit_callback_then_avaible_goals_updated(node):
    data = Int16()
    data.data = 5

    node.set_home_deposit_callback(data)

    assert "ZD1" in node.available_goals


def test_when_home_deposit_callback_then_home_deposit_updated(node):
    data = Int16()
    data.data = 5

    node.set_home_deposit_callback(data)

    assert node.home_deposit_zone == "ZD1"


def test_given_going_ZD2_when_is_at_intersection_valid_to_stop_then_return_false(node):
    ZD2_TAG = 7
    node.available_goals = ["ZC1"]
    node._current_nodes_path = ["A1", "ZC1"]

    assert node.is_intersection_valid_to_stop(ZD2_TAG) is False


def test_given_going_home_deposit_when_is_at_intersection_valid_to_stop_then_return_false(
    node,
):
    ZD1_TAG = 5
    node.available_goals = ["ZC1"]
    node._current_nodes_path = ["A1", "ZC1"]

    assert node.is_intersection_valid_to_stop(ZD1_TAG) is False


def test_given_going_ZC1_when_is_at_intersection_valid_to_stop_then_return_true(node):
    ZC1_TAG = 6
    node.available_goals = ["ZC1"]
    node._current_nodes_path = ["A1", "ZC1"]

    assert node.is_intersection_valid_to_stop(ZC1_TAG) is True


def test_given_going_mo_available_goals_when_is_at_intersection_valid_to_stop_then_return_true(
    node,
):
    ZC1_TAG = 6
    node.available_goals = []
    node._current_nodes_path = ["A1", "ZC1"]

    assert node.is_intersection_valid_to_stop(ZC1_TAG) is True


def test_given_going_no_path_when_is_at_intersection_valid_to_stop_then_return_true(
    node,
):
    ZC1_TAG = 6
    node.available_goals = []
    node._current_nodes_path = []

    assert node.is_intersection_valid_to_stop(ZC1_TAG) is True


def test_given_going_ZD1_when_is_at_intersection_ZC2_valid_to_stop_then_return_false(
    node_zc2,
):
    ZC2_TAG = 8
    node_zc2.available_goals = ["ZD1"]
    node_zc2._current_nodes_path = ["A3", "ZD1"]

    assert node_zc2.is_intersection_valid_to_stop(ZC2_TAG) is False


def test_given_going_ZD1_when_is_at_intersection_A1_valid_to_stop_then_return_true(
    node,
):
    A1_TAG = 1
    node.available_goals = ["ZD1"]
    node._current_nodes_path = ["A3", "ZD1"]

    assert node.is_intersection_valid_to_stop(A1_TAG) is True


def test_when_handle_is_at_intersection_valid_to_stop_then_response_is_sent(node):
    class Req:
        aruco_tag = 42

    class Resp:
        is_valid = None

    node.is_intersection_valid_to_stop = lambda tag: tag == 42

    response = Resp()

    result = node.handle_get_is_intersection_valid_to_stop(Req(), response)

    assert result is response
    assert response.is_valid is True
