import random
from model.tile import Tile

class Board:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.tiles = [[Tile() for x in range(size_x)] for y in range(size_y)]

        # use the center of the maze as the goal, can be changed later
        self.goal_x = size_x // 2
        self.goal_y = size_y // 2
        self.ideal_x = 0
        self.ideal_y = 0
        self.tiles[self.goal_x][self.goal_y].set_as_goal()

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

      if not self.check_valid_path_exist():
          self.create_path()

    def check_valid_path_exist(self):
        # bfs traversal to check at least one valid path
        queue = []
        visited = set()

        for x in range(self.size_x):
            queue.append((x, 0))
            queue.append((x, self.size_y - 1))

        for y in range(self.size_y):
            queue.append((0, y))
            queue.append((self.size_x - 1, y))

        closest_distance = None

        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            if not self.can_be_traversed(x, y):
                continue

            visited.add((x, y))

            distance = abs(x - self.goal_x) + abs(y - self.goal_y)
            if closest_distance is None or distance < closest_distance:
                closest_distance = distance
                self.ideal_x = x
                self.ideal_y = y

            if self.check_goal(x, y):
                return True

            for next_x, next_y in self.get_neighbors(x, y):
                queue.append((next_x, next_y))

        return False

    def create_path(self):
        # if no path exist, create one path continuing from the closest blocked path from goal
        x, y = self.get_ideal_start_pos()

        while x != self.goal_x:
            self.tiles[x][y].set_blocked(False)
            if x < self.goal_x:
                x += 1
            else:
                x -= 1

        while y != self.goal_y:
            self.tiles[x][y].set_blocked(False)

            if y < self.goal_y:
                y += 1
            else:
                y -= 1

        self.tiles[self.goal_x][self.goal_y].set_blocked(False)

    # ideal start pos will be used by the enemy snake
    def get_ideal_start_pos(self):
        return self.ideal_x, self.ideal_y

    def get_neighbors(self, x, y):
        neighbors = []

        possible_neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        for next_x, next_y in possible_neighbors:
            if 0 <= next_x < self.size_x and 0 <= next_y < self.size_y:
                neighbors.append((next_x, next_y))

        return neighbors

    def check_goal(self, x, y):
        return self.tiles[x][y].check_is_goal()

    def can_be_traversed(self, x, y):
        return not self.tiles[x][y].check_blocked()

