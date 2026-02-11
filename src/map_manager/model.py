class MapNode:
    def __init__(self, id: str):
        self.id: str = id
        self.right = None
        self.left = None
        self.straight = None
    
    def add_right_turn(self, next_map_node):
        self.right = next_map_node
    
    def add_left_turn(self, next_map_node):
        self.left = next_map_node
    
    def add_straight_line(self, next_map_node):
        self.straight = next_map_node
    
    def turn_right(self):
        return self.right

    def turn_left(self):
        return self.left
    
    def go_straight(self):
        return self.straight

    

class Map:
    def __init__(self, map_nodes: list[MapNode]):
        self.map_nodes: list[MapNode] = map_nodes
        self.actual_position: MapNode = self.set_actual_position(map_nodes[0].id)
    
    def initialize_actual_position(self, map_node_id: str): 
        for map_node in self.map_nodes:
            if map_node.get_id == map_node_id:
                self.actual_position = map_node
                return
        
        # raise Error if not map_node not founded !!
    
    def turn_right(self):
        if self.actual_position.right:
            self.actual_position= self.actual_position.turn_right()
        else:
            # raise error for not poissble turn !
            pass
    
    def turn_left(self):
        if self.actual_position.left:
            self.actual_position = self.actual_position.turn_left()
        else:
            # raise error for not poissble turn !
            pass
    
    def go_straight(self):
        if self.actual_position.straight:
            self.actual_position= self.actual_position.go_straight()
        else:
            # raise error for not poissble turn !
            pass
            
            
    
    