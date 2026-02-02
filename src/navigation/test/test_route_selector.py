import unittest
from navigation.route_selector import RouteSelector


class TestRouteSelector(unittest.TestCase):
    def setUp(self):
        self.test_graph = {
            "A1": {"g": "ZC1", "l": "A4", "d": "ZD1"},
            "A2": {"g": "A4", "l": "ZD1", "d": "A2"},
            "A3": {"g": "ZD1", "l": "A2", "d": "ZC1"},
            "A4": {"g": "A2", "l": "ZC1", "d": "A4"},
            "ZC1": {"l": "A1"},
            "ZD1": {"l": "A3"},
        }
        self.selector = RouteSelector(graph=self.test_graph)

    def test_route_exists(self):
        route = self.selector.compute_route("A1", "ZC1")
        self.assertIsNotNone(route)
        self.assertIsInstance(route, list)

    def test_route_valid_path(self):
        route = self.selector.compute_route("ZC1", "ZD1")
        self.assertIsNotNone(route)
        current = "ZC1"
        for direction in route:
            self.assertIn(direction, self.test_graph[current])
            current = self.test_graph[current][direction]
        self.assertEqual(current, "ZD1")

    def test_route_same_node(self):
        route = self.selector.compute_route("A1", "A1")
        self.assertEqual(route, [])

    def test_route_invalid_start(self):
        route = self.selector.compute_route("INVALID", "A1")
        self.assertIsNone(route)

    def test_route_invalid_goal(self):
        route = self.selector.compute_route("A1", "INVALID")
        self.assertIsNone(route)

    def test_route_multiple_steps(self):
        route = self.selector.compute_route("A1", "A2")
        self.assertIsNotNone(route)
        self.assertGreater(len(route), 0)

    def test_route_all_nodes_reachable(self):
        nodes = list(self.test_graph.keys())
        for start in nodes:
            for goal in nodes:
                if start != goal:
                    route = self.selector.compute_route(start, goal)
                    if route is not None:
                        self.assertIsInstance(route, list)
                        self.assertGreaterEqual(len(route), 0)


if __name__ == "__main__":
    unittest.main()
