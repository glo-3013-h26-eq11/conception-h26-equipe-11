from typing import Dict, List, Optional, Tuple
from navigation.route_selector import RouteSelector


class GoalSelector:

    def __init__(self, route_selector: RouteSelector):
        self.route_selector = route_selector
        self._dist_cache: Dict[Tuple[str, str], Optional[int]] = {}

    def select_goal(
        self,
        current_node: str,
        available_goals: List[str],
        mode: str = "GO_LOAD",
    ) -> Optional[str]:
        if not available_goals:
            return None

        self._dist_cache.clear()

        if mode == "GO_LOAD":
            load_goals = [g for g in available_goals if g.startswith("ZC")]
            return self._select_closest_goal(current_node, load_goals)

        if mode == "GO_DROP":
            drop_goals = [g for g in available_goals if g.startswith("ZD")]
            return self._select_closest_goal(current_node, drop_goals)

        return None

    def _select_closest_goal(
        self, current_node: str, goals: List[str]
    ) -> Optional[str]:
        if not goals:
            return None

        best_goal = None
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
        key = (start, goal)
        if key in self._dist_cache:
            return self._dist_cache[key]

        route = self.route_selector.compute_route(start, goal)
        dist = None if route is None else len(route)

        self._dist_cache[key] = dist
        return dist
