import heapq
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from model.board import Board
    from model.snake import Snake

def dijkstra(
    board: "Board",
    start: Tuple[int, int],
    goal: Tuple[int, int],
    own_snake: "Snake",
    other_snake: "Snake",
) -> List[Tuple[int, int]]:

    if start == goal:
        return []

    own_tail    = own_snake.tail
    other_tail  = other_snake.tail

    blocked: set[Tuple[int, int]] = set()

    for cell in own_snake.body:
        if cell != own_tail:
            blocked.add(cell)

    for cell in other_snake.body:
        if cell != other_tail:
            blocked.add(cell)

    # dijkstra
    INF = float("inf")
    dist: dict[Tuple[int, int], float] = {}
    prev: dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}

    dist[start] = 0
    prev[start] = None

    # heap entries: (cost, x, y)
    heap: list[Tuple[float, int, int]] = [(0, start[0], start[1])]

    while heap:
        cost, x, y = heapq.heappop(heap)

        # stale entry check
        if cost > dist.get((x, y), INF):
            continue

        if (x, y) == goal:
            break

        for nx, ny in board.get_neighbors(x, y):
            cell = (nx, ny)

            # determine traversal cost for the neighbour
            if cell == goal:
                step_cost = 1  # goal is always reachable regardless of occupant
            elif board.tiles[nx][ny].check_blocked():
                continue      # walls and obstacles are impassable
            elif cell in blocked:
                continue      # snake bodies are impassable
            else:
                step_cost = 1

            new_cost = cost + step_cost
            if new_cost < dist.get(cell, INF):
                dist[cell] = new_cost
                prev[cell] = (x, y)
                heapq.heappush(heap, (new_cost, nx, ny))

    # reconstruct path
    if goal not in dist:
        return []  # no path found

    path: List[Tuple[int, int]] = []
    current: Optional[Tuple[int, int]] = goal
    while current is not None and current != start:
        path.append(current)
        current = prev.get(current)

    if current != start:
        return []  # if disconnected 

    path.reverse()
    return path


def get_path_length(path: List[Tuple[int, int]]) -> int:
    return len(path)


def has_path(path: List[Tuple[int, int]]) -> bool:
    return bool(path)