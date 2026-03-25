from collections import deque
from typing import Dict, List, Optional, Tuple

DIRECTION_KEYS = ("left", "straight", "right")


class RouteSelector:

    def __init__(self, graph: Dict[str, Dict[str, str]]):
        self.graph = graph

    def _validate_start_goal(self, start: str, goal: str) -> None:
        if start not in self.graph:
            raise ValueError(f"Unknown start node: {start}, from graph : {self.graph}")
        if goal not in self.graph:
            raise ValueError(f"Unknown goal node: {goal}, from graph : {self.graph}")

    def _get_neighbors(self, node: str) -> Dict[str, str]:
        raw = self.graph.get(node, {})
        return {
            direction: raw[direction]
            for direction in DIRECTION_KEYS
            if raw.get(direction)
        }

    def tag_to_id(self, tag: int):
        if not self.graph:
            raise ValueError("Graph not loaded yet")

        tag_to_id = {v["tag"]: v["id"] for v in self.graph.values()}

        result_id = tag_to_id.get(tag)

        return result_id

    def compute_path(
        self, start: str, goal: str
    ) -> Optional[Tuple[List[str], List[str]]]:
        self._validate_start_goal(start, goal)

        if start == goal:
            return ([start], [])

        queue = deque([start])
        visited = {start}

        parent: Dict[str, str] = {}
        parent_dir: Dict[str, str] = {}

        while queue:
            node = queue.popleft()

            for direction, next_node in self._get_neighbors(node).items():
                if next_node in visited:
                    continue

                visited.add(next_node)
                parent[next_node] = node
                parent_dir[next_node] = direction

                if next_node == goal:
                    return self._reconstruct_path(start, goal, parent, parent_dir)

                queue.append(next_node)

        return None

    def _reconstruct_path(
        self,
        start: str,
        goal: str,
        parent: Dict[str, str],
        parent_dir: Dict[str, str],
    ) -> Tuple[List[str], List[str]]:
        nodes: List[str] = []
        directions: List[str] = []

        cur = goal
        while cur != start:
            nodes.append(cur)
            directions.append(parent_dir[cur])
            cur = parent[cur]

        nodes.append(start)

        nodes.reverse()
        directions.reverse()

        return nodes, directions
