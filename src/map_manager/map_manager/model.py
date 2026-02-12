import json


class MapNode:
    def __init__(self, id: str, tag: int = -1):
        self.id: str = id
        self.tag: int = tag
        self.right: str = None
        self.left: str = None
        self.straight: str = None

    def add_right_turn(self, next_map_node: "MapNode"):
        self.right = next_map_node.id

    def add_left_turn(self, next_map_node: "MapNode"):
        self.left = next_map_node.id

    def add_straight_line(self, next_map_node: "MapNode"):
        self.straight = next_map_node.id

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tag": self.tag,
            "right": self.right,
            "left": self.left,
            "straight": self.straight,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MapNode":
        node = cls(id=data["id"], tag=data.get("tag", -1))
        node.right = data.get("right")
        node.left = data.get("left")
        node.straight = data.get("straight")
        return node


class Map:
    def __init__(self, map_nodes: list[MapNode] = None):
        self.map_nodes: dict[str, MapNode] = {}
        if map_nodes:
            for node in map_nodes:
                if node.id in self.map_nodes:
                    raise ValueError(f"Duplicate node ID detected: {node.id}")
                self.map_nodes[node.id] = node

    def get_map_node(self, map_node_id: str) -> MapNode:
        if map_node_id in self.map_nodes:
            return self.map_nodes[map_node_id]
        raise ValueError(f"Node with id {map_node_id} not found in map")

    def to_dict(self) -> dict:
        return {node_id: node.to_dict() for node_id, node in self.map_nodes.items()}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "Map":
        data = json.loads(json_str)
        nodes = []
        for node_data in data.values():
            nodes.append(MapNode.from_dict(node_data))
        return cls(nodes)
