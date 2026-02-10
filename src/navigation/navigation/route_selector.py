from collections import deque
from typing import Dict, List, Optional

GRAPH_TEMP = {
    "A1": {"g": "ZC1", "l": "A4", "d": "ZD1"},
    "A2": {"g": "A4", "l": "ZD1", "d": "A2"},
    "A3": {"g": "ZD1", "l": "A2", "d": "ZC1"},
    "A4": {"g": "A2", "l": "ZC1", "d": "A4"},
    "ZC1": {"l": "A1"},
    "ZD1": {"l": "A3"},
}


class RouteSelector:

    def __init__(self, graph: Optional[Dict[str, Dict[str, str]]] = None):
        self.graph = graph if graph is not None else GRAPH_TEMP

    def compute_route(self, start: str, goal: str) -> Optional[List[str]]:
        if start not in self.graph:
            raise ValueError(f"Unknown start node: {start}")
        if goal not in self.graph:
            raise ValueError(f"Unknown goal node: {goal}")
        if start == goal:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            node, path = queue.popleft()

            if node == goal:
                return path

            neighbors = self.graph.get(node, {})
            for direction, next_node in neighbors.items():
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [direction]))

        return None
