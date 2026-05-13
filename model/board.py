from tile import Tile

class Board:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = [[Tile() for x in range(size_x)] for y in range(size_y)]

        # use the center of the maze as the goal, can be changed later
        self.tiles[size_x/2][size_y/2].set_as_goal()
        self.generate_blocked_tile()

    def generate_blocked_tile(self):
        return
    
    def validate_path_exist(self, start, goal):
        return True
    
    def check_goal(self, x, y):
        return self.tiles[x][y].check_is_goal()

    def can_be_traversed(self, x, y):
        return not self.tiles[x][y].check_blocked()

