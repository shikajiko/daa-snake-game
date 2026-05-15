import random
from model.tile import Tile

from typing import List, Tuple, Optional

from model.snake import Snake

class Board:
    def __init__(self, size_x: int = 20, size_y: int = 20):
        if size_x < 4 or size_y < 4:
            raise ValueError("Board must be atleast 4x4")

        if size_y % 2 != 0:
            raise ValueError("Board Size Y must be even to able to split")

        self.size_x = size_x
        self.size_y = size_y
        self.tiles = [[Tile() for x in range(size_x)] for y in range(size_y)]

        # use the center of the maze as the goal, can be changed later
        self.goal_x = size_x // 2
        self.goal_y = size_y // 2
        self.ideal_x: int = 0
        self.ideal_y: int = 0


        self._place_goal()

        self.player_snake: Optional[Snake] = None
        self.computer_snake: Optional[Snake] = None

        self.on_board_changed = None

    def _place_goal(self) -> None: 
        self.tiles[self.goal_x][self.goal_y].set_as_goal()

    def generate_maze(self, wall_chance: float = 0.35):
        # wall_chance = 0.9
        half = self.size_y // 2

        # upper half
        for y in range(0, half):
            for x in range(self.size_x):
                if (x, y) == (self.goal_x, self.goal_y):
                    continue

                if y == half - 1:
                    continue

                self.tiles[x][y].set_blocked(random.random() < wall_chance)
        # lower half
        for y in range(half, self.size_y):
            for x in range(self.size_x):
                if (x, y) == (self.goal_x, self.goal_y):
                    continue

                if y == half - 1
                    continue

                self.tiles[x][y].set_blocked(random.random() < wall_chance)


        if not self._check_path_from_half(upper=True):
            self._carve_path_to_goal(from_upper=True)
        
        if not self._check_path_from_half(upper=False):
            self._carve_path_to_goal(from_upper=False)

    def _check_path_from_half(self, upper: bool) -> bool:
        # BFS from every free edge cell in one half to see if the goal is reachable
        half = self.size_y // 2
        queue: List[Tuple[int, int]] = []
        visited: set = set()

        if upper:
            for x in range(self.size_x):
                queue.append((x, 0))
            y_range = range(0, half)
        else:
            for x in range(self.size_x):
                queue.append((x, self.size_y - 1))
            y_range = range(half, self.size_y)

        closest_dist = None;
        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            if y not in y_range:
                continue
            if not self.can_be_traversed(x, y):
                continue

            visited.add((x, y))
            dist = abs(x - self.goal_x) + abs(y - self.goal_y)
            if closest_dist is None or dist < closest_dist:
                closest_dist = dist
                self.ideal_x, self.ideal_y = x, y

            if self.check_goal(x, y):
                return True

            for nx, ny in self.get_neighbors(x, y):
                if ny in y_range:
                    queue.append((nx, ny))

        return False

    def _carve_path_to_goal(self, from_upper: bool) -> None:
        x, y = self.ideal_x, self.ideal_y

        while x != self.goal_x:
            self.tiles[x][y].set_blocked(False)
            x += 1 if x < self.goal_x else -1

        while y != self.goal_y:
            self.tiles[x][y].set_blocked(False)
            y += 1 if y < self.goal_y else -1

        self.tiles[self.goal_x][self.goal_y].set_blocked(False)

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


    def spawn_snakes(self, snake_length: int = 4) -> Tuple[Snake, Snake]:
        half = self.size_y // 2
        mid_x = self.size_x // 2

        comp_start_x = mid_x
        comp_start_y = snake_length -1 
        comp_direction = (0, 1) # moving down

        player_start_x = mid_x
        player_start_y = self.size_y - snake_length
        player_direction = (0, -1) # moving up

        self.clear_spawn_area(comp_start_x, comp_start_y, snake_length, comp_direction)
        self.clear_spawn_area(player_start_x, player_start_y, snake_length, player_direction)

        self.computer_snake = Snake(
            owner="computer",
            start_x=comp_start_x,
            start_y=comp_start_y,
            length=snake_length,
            initial_direction=comp_direction
        )

        self.player_snake = Snake(
            owner="player",
            start_x=player_start_x,
            start_y=player_start_y,
            length=snake_length,
            initial_direction=player_direction
        )

        self.computer_snake.mark_tiles(self)
        self.player_snake.mark_tiles(self)

        return self.player_snake, self.computer_snake


    def clear_spawn_area(self, sx: int, sy: int, length: int, direction: Tuple[int, int]) -> None:
        dx, dy = direction
        for i in range(length):
            x = max(0, min(self.size_x - 1, sx - dx * i))
            y = max(0, min(self.size_y - 1, sy - dy * i))
            self.tiles[x][y].set_blocked(False)



    def move_snake(self, snake: Snake, dx: int, dy: int) -> bool: # true if succeeded
        nx, ny = snake.get_next_head_move(dx, dy)
        if not (0 <= nx < self.size_x and 0 <= ny < self.size_y):
            snake.kill()
            return False

        target = self.tiles[nx][ny]

        if target.check_blocked():
            snake.kill()
            return False

        other = self._other_snake(snake)
        if other and other.occupies(nx, ny):
            if (nx, ny) != other.tail:
                snake.kill()
                return False

        old_tail = snake.move_head(dx, dy)
        ox, oy = old_tail

        if not (other and other.occupies(ox, oy)):
            self.tiles[ox][oy].set_occupant(None)

        self.tiles[nx][ny].set_occupant(snake.owner)

        if target.check_is_goal():
            snake.mark_reached_goal()

        return True

    def move_snake_to(self, snake: Snake, x: int, y: int) -> bool:
        hx, hy = snake.head
        return self.move_snake(snake, x - hx, y - hy)

    def step_snake_planned(self, snake: Snake) -> bool:
        nxt = snake.peak_next()
        if nxt is None:
            return False
        snake.planned_path.popleft()
        return self.move_snake_to(snake, *nxt)



    def add_obstacle(self, x: int, y: int) -> bool: # false if x, y is the goal, occupied by snake body or already blocked
        if not self._in_bounds(x, y):
            return False
        
        tile = self.tiles[x][y]
        if tile.check_is_goal() or tile.check_blocked():
            return False

        if tile.check_occupant() is not None:
            return False

        tile.set_blocked(True)
        self._notify_board_changed()
        return True

    def remove_obstacle(self, x: int, y: int) -> bool: # true if the wall is successfully removed
        if not self._in_bounds(x, y):
            return False

        tile = self.tiles[x][y]
        if not tile.check_blocked():
            return False

        tile.set_blocked(False)
        self._notify_board_changed()
        return True

    def toggle_obstacle(self, x: int, y: int) -> bool: # literally just toggles obstacle
        if self.tiles[x][y].check_blocked():
            return self.remove_obstacle(x, y)
        
        return self.add_obstacle(x, y)


    # invalidate previous Dijkstra paths for both snakes and fire the external callback, so the controller re-plan the path
    def _notify_board_changed(self) -> None:
        if self.player_snake:
            self.player_snake.clear_path()
        if self.computer_snake:
            self.computer_snake.clear_path()
        if callable(self.on_board_changed):
            self.on_board_changed()



    # ideal start pos will be used by the enemy snake

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
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
    
    def get_traversable_neighbors(self, x: int, y: int, snake: Optional[Snake] = None) -> List[Tuple[int, int]]:
        result = []
        for nx, ny in self.get_neighbors(x, y):
            tile = self.tiles[nx][ny]
            if tile.check_blocked():
                continue
            occupant = tile.check_occupant()
            if occupant is not None:
                if snake and (nx, ny) == snake.tail:
                    result.append((nx, ny)) # allow this cell if it is the moving snake's own tail
                    continue
                continue # block cells occupied by the opponent2
            result.append((nx, ny))
        return result

    def edge_weight(self, x1: int, y1: int, x2: int, y2: int) -> float:
        # for uniform cost, lets just make it 1, if future model for the weight per edge needs to be vary, modify this function
        return 1.0

    def build_adjacency(self, snake: Optional[Snake] = None) -> dict:
        adj = {}
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.tiles[x][y].check_blocked():
                    continue
                neighbors = self.get_traversable_neighbors(x, y, snake)
                adj[(x, y)] = [
                    (nx, ny, self.edge_weight(x, y, nx, ny)) for nx, ny in neighbors
                ]
        return adj

    # helper functions
    def check_goal(self, x, y) -> bool:
        return self.tiles[x][y].check_is_goal()

    def can_be_traversed(self, x, y) -> bool:
        return not self.tiles[x][y].check_blocked()

    def get_goal_pos(self) -> Tuple[int, int]:
        return self.goal_x, self.goal_y

    def get_ideal_start_pos(self) -> Tuple[int, int]:
        return self.ideal_x, self.ideal_y

    def get_upper_half_rows(self) -> range:
        return range(0, self.size_y // 2)

    def get_lower_half_rows(self) -> range:
        return range(self.size_y // 2, self.size_y)

    def is_game_over(self) -> bool:
        snakes = [s for s in (self.player_snake, self.computer_snake) if s]
        if not snakes:
            return False
        if any(s.reached_goal for s in snakes):
            return True
        if all(not s.alive for s in snakes):
            return True
        return False

    def get_winner(self) -> Optional[str]:
        if not self.is_game_over():
            return None
        
        p_won = self.player_snake and self.player_snake.reached_goal
        c_won = self.computer_snake and self.computer_snake.reached_goal

        if p_won and c_won:
            return "Draw"
        if p_won:
            return "Player"
        if c_won:
            return "Computer"
        
        return "Draw"

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size_x and 0 <= y < self.size_y
 
    def _other_snake(self, snake: Snake) -> Optional[Snake]:
        if snake is self.player_snake:
            return self.computer_snake
        return self.player_snake


    # debug function to print the board
    def to_char_grid(self) -> List[str]:
        """
        Return a list of strings representing the board (for terminal debug).
 
        Legend:
          G  – goal
          #  – wall
          P  – player snake body
          C  – computer snake body
          .  – free cell
        """
        rows = []
        for y in range(self.size_y):
            row = ""
            for x in range(self.size_x):
                tile = self.tiles[x][y]
                if tile.check_is_goal():
                    row += "G "
                elif tile.check_blocked():
                    row += "# "
                elif tile.check_occupant() == "player":
                    row += "P "
                elif tile.check_occupant() == "computer":
                    row += "C "
                else:
                    row += ". "
            rows.append(row)
        return rows
 
    def print_board(self) -> None:
        for line in self.to_char_grid():
            print(line)
 

