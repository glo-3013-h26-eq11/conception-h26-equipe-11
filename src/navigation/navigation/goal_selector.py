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
        other_vehicles_routes: Optional[List[Dict]] = None,
    ) -> Optional[str]:
        if not available_goals:
            return None

        self._dist_cache.clear()

        if mode == "GO_LOAD":
            load_goals = [g for g in available_goals if g.startswith("ZC")]
            return self._select_load_goal(current_node, load_goals, other_vehicles_routes)

        if mode == "GO_DROP":
            return self._select_drop_goal(current_node, available_goals)

        return None

    def _select_load_goal(
        self,
        current_node: str,
        available_goals: List[str],
        other_vehicles_routes: Optional[List[Dict]],
    ) -> Optional[str]:
        accessible_goals = self._filter_accessible_goals(
            current_node, available_goals, other_vehicles_routes
        )
        if not accessible_goals:
            return None

        best_goal = None
        min_distance = float("inf")

        for goal_node in sorted(accessible_goals):
            dist = self._get_distance(current_node, goal_node)
            if dist is None:
                continue
            if dist < min_distance:
                min_distance = dist
                best_goal = goal_node

        return best_goal

    def _select_drop_goal(self, current_node: str, available_goals: List[str]) -> Optional[str]:
        drop_zones = [g for g in available_goals if g.startswith("ZD")]
        if not drop_zones:
            return None

        best_goal = None
        min_distance = float("inf")

        for goal_node in sorted(drop_zones):
            dist = self._get_distance(current_node, goal_node)
            if dist is None:
                continue
            if dist < min_distance:
                min_distance = dist
                best_goal = goal_node

        return best_goal

    def _filter_accessible_goals(
        self,
        current_node: str,
        goals: List[str],
        other_vehicles_routes: Optional[List[Dict]],
    ) -> List[str]:
        if not other_vehicles_routes:
            return goals

        accessible: List[str] = []

        for goal in goals:
            our_dist = self._get_distance(current_node, goal)
            if our_dist is None:
                continue

            ok = True
            for v in other_vehicles_routes:
                if v.get("goal_node") != goal:
                    continue

                v_node = v.get("current_node")
                if not v_node:
                    continue

                v_dist = self._get_distance(v_node, goal)
                if v_dist is None:
                    continue

                if v_dist < our_dist:
                    ok = False
                    break

            if ok:
                accessible.append(goal)

        return accessible

    def _get_distance(self, start: str, goal: str) -> Optional[int]:
        key = (start, goal)
        if key in self._dist_cache:
            return self._dist_cache[key]

        route = self.route_selector.compute_route(start, goal)
        dist = None if route is None else len(route)
        self._dist_cache[key] = dist
        return dist