from collections import deque
from typing import List, Tuple, Optional

class Snake:
    def __init__(self, owner: str, start_x: int, start_y: int, length: int = 4, initial_direction: Tuple[int, int] = (1, 0)) -> None:
        if length < 1:
            raise ValueError('Snake length must be greater than 1')

        if owner not in ("player", "computer"):
            raise ValueError('owner must be "player" or "computer"')

        self.owner = owner
        self.length = length
        self.direction: Tuple[int, int] = initial_direction
        self.alive: bool = True
        self.reached_goal: bool = False

        dx, dy = initial_direction
        self.body: deque[Tuple[int, int]] = deque()
        for i in range(length):
            self.body.appendleft((start_x - dx * i, start_y - dy * i))

        self.planned_path: deque[Tuple[int, int]] = deque()

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[-1]

    @property
    def tail(self) -> Tuple[int, int]:
        return self.body[0]

    @property
    def head_x(self) -> int:
        return self.head[0]

    @property
    def head_y(self) -> int:
        return self.head[1]

    @property
    def body_set(self) -> set:
        return set(self.body)


    
    def get_next_head_move(self, dx: int, dy: int) -> Tuple[int, int]:
        hx, hy = self.head
        return hx + dx , hy + dy

    def move_head(self, dx: int, dy: int) -> Tuple[int, int]:
        if not self.alive:
            raise RuntimeError(f"Snake '{self.owner}' is dead, cannot be moved")

        new_head = self.get_next_head_move(dx, dy)
        old_tail = self.body[0]
        
        self.body.append(new_head)
        self.body.popleft() # since the length of the snake is fixed
        self.direction = (dx, dy)

        return old_tail

    def move_to(self, x: int, y: int) -> Tuple[int, int]:
        hx, hy = self.head
        dx, dy = x - hx, y - hy
        if abs(dx) + abs(dy) != 1: # manhattan distance, target must adjacent, value must be 1
            raise ValueError(f"Move to target '{x}, {y}' is not adjacent to head on '{hx}, {hy}'")

        return self.move_head(dx, dy)

    def step_planned(self) -> Optional[Tuple[int, int]]:
        if not self.planned_path:
            return None
        
        nx, ny = self.planned_path.popleft()
        return self.move_to(nx, ny)


    def set_path(self, path: List[Tuple[int, int]]) -> None:
        self.planned_path = deque(path)

    def clear_path(self) -> None:
        self.planned_path.clear()

    def has_path(self) -> bool:
        return bool(self.planned_path)

    def peak_next(self) -> Optional[Tuple[int, int]]:
        if self.planned_path:
            return self.planned_path[0]
        
        return None

    
    def mark_tiles(self, board) -> None:
        for x, y in self.body:
            board.tiles[x][y].set_occupant(None)


    def kill(self) -> None:
        self.alive = False

    def mark_reached_goal(self) -> None:
        self.reached_goal = True
        self.kill()

    def occupies(self, x: int, y: int) -> bool:
        return (x, y) in self.body_set


    def __repr__(self) -> str:
        status = "alive" if self.alive else ("won" if self.reached_goal else "dead")
        return (
            f"Snake(owner='{self.owner!r}', head='{self.head}') "
            f"Length = {self.length} - Status: {status} "
            f"queued steps = {len(self.planned_path)}"
        )
