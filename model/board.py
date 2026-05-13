import random
import math
from model.tile import Tile

class Board:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = [[Tile() for x in range(size_x)] for y in range(size_y)]

        # use the center of the maze as the goal, can be changed later
        self.tiles[size_x // 2][size_y // 2].set_as_goal()

    def generate_maze(self):
      wall_chance = 0.9
      # split the maze into layers 
      for y in range(self.size_y):
          for x in range(self.size_x):
              if self.tiles[x][y].is_goal:
                  continue
              layer = min(x, y, self.size_x - 1 - x, self.size_y - 1 - y)
              
              is_blocked = False
              # odd layers has a higher chance of being a wall
              if layer == 0: continue
              elif layer % 2 != 0 and random.random() < wall_chance:
                  is_blocked = True
              elif layer % 2 == 0 and random.random() > wall_chance:
                  is_blocked = True
              self.tiles[x][y].set_blocked(is_blocked)

    def check_goal(self, x, y):
        return self.tiles[x][y].check_is_goal()

    def can_be_traversed(self, x, y):
        return not self.tiles[x][y].check_blocked()

