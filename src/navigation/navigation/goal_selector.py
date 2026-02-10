from __future__ import annotations

from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

from navigation.route_selector import RouteSelector


class GoalMode(str, Enum):
    GO_LOAD = "GO_LOAD"
    GO_DROP = "GO_DROP"


class GoalSelector:
    def __init__(self, route_selector: RouteSelector):
        self.route_selector = route_selector
        self._shortest_path_length_cache: Dict[Tuple[str, str], Optional[int]] = {}

        self._goal_filters: Dict[GoalMode, Callable[[List[str]], List[str]]] = {
            GoalMode.GO_LOAD: lambda goals: [g for g in goals if g.startswith("ZC")],
            GoalMode.GO_DROP: lambda goals: [g for g in goals if g.startswith("ZD")],
        }

    def select_goal(
        self,
        current_node: str,
        available_goals: List[str],
        mode: Union[GoalMode, str] = GoalMode.GO_LOAD,
    ) -> Optional[str]:
        if not available_goals:
            return None

        if isinstance(mode, str):
            try:
                mode = GoalMode(mode)
            except ValueError as e:
                raise ValueError(f"Invalid goal selection mode: {mode}") from e

        filter_fn = self._goal_filters[mode]
        filtered = filter_fn(available_goals)
        return self._select_closest_goal(current_node, filtered)

    def _select_closest_goal(
        self, current_node: str, goals: List[str]
    ) -> Optional[str]:
        if not goals:
            return None

        best_goal: Optional[str] = None
        min_distance = float("inf")

        for goal_node in sorted(goals):
            dist = self._get_distance(current_node, goal_node)
            if dist is None:
                continue
            if dist < min_distance:
                min_distance = dist
                best_goal = goal_node

        return best_goal

    def _get_distance(self, start: str, goal: str) -> Optional[int]:
        node_pair = (start, goal)
        if node_pair in self._shortest_path_length_cache:
            return self._shortest_path_length_cache[node_pair]

        try:
            route = self.route_selector.compute_route(start, goal)
        except ValueError:
            dist = None
        else:
            dist = None if route is None else len(route)

        self._shortest_path_length_cache[node_pair] = dist
        return dist
