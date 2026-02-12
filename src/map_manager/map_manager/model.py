class MapNode:
    def __init__(self, id: str, tag: int = -1):
        self.id: str = id
        self.right: str = None
        self.left: str = None
        self.straight: str = None
    
    def add_right_turn(self, next_map_node: "MapNode"):
        self.right = next_map_node.id
    
    def add_left_turn(self, next_map_node: "MapNode"):
        self.left = next_map_node.id
    
    def add_straight_line(self, next_map_node: "MapNode"):
        self.straight = next_map_node.id

    

class Map:
    def __init__(self, map_nodes: list[MapNode], initial_position_id: str = None):
        if not map_nodes: 
            raise ValueError("Node list cannot be empty to initialize the Map.")

        self.map_nodes: dict[str, MapNode] = {}
        for node in map_nodes:
            if node.id in self.map_nodes: 
                raise ValueError(f"Duplicate node ID detected: {node.id}. Each node must have a unique ID.")
            self.map_nodes[node.id] = node
    
    
    def get_map_node(self, map_node_id: str) -> MapNode: 
        if map_node_id in self.map_nodes:
            return self.map_nodes[map_node_id]
        else:  
            raise ValueError(f"Node with id {map_node_id} not found in map")
            
            
    
    