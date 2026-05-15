from typing import Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from model.board import Board
    from model.snake import Snake

class PlayerController:
    MAX_MOVES: int = 3
    MAX_OBSTACLES: int = 6

    def __init__(self, board: "Board") -> None:
        self.board = board
        self.moves_remaining: int = self.MAX_MOVES
        self._obstacle_cells: Set[Tuple[int, int]] = set()

    # round management
    def reset_moves(self) -> None:
        self.moves_remaining = self.MAX_MOVES

    def skip_remaining(self) -> None:
        self.moves_remaining = 0

    # validation helpers
    def can_place(
        self,
        x: int,
        y: int,
        player_snake: "Snake",
        ai_snake: "Snake",
    ) -> bool:
        if self.moves_remaining <= 0:
            return False
        if len(self._obstacle_cells) >= self.MAX_OBSTACLES:
            return False
        if not (0 <= x < self.board.size_x and 0 <= y < self.board.size_y):
            return False

        tile = self.board.tiles[x][y]
        if tile.check_blocked():
            return False
        if tile.check_is_goal():
            return False
        if player_snake.occupies(x, y):
            return False
        if ai_snake.occupies(x, y):
            return False

        return True

    def can_destroy(self, x: int, y: int) -> bool:
        if self.moves_remaining <= 0:
            return False
        return (x, y) in self._obstacle_cells

    def has_moves(self) -> bool:
        return self.moves_remaining > 0

    # actions
    def place_obstacle(
        self,
        x: int,
        y: int,
        player_snake: "Snake",
        ai_snake: "Snake",
    ) -> bool:
        if not self.can_place(x, y, player_snake, ai_snake):
            return False

        self.board.tiles[x][y].set_blocked(True)
        self._obstacle_cells.add((x, y))
        self.moves_remaining -= 1
        return True

    def destroy_obstacle(self, x: int, y: int) -> bool:
        if not self.can_destroy(x, y):
            return False

        self.board.tiles[x][y].set_blocked(False)
        self._obstacle_cells.discard((x, y))
        self.moves_remaining -= 1
        return True

    def toggle_obstacle(
        self,
        x: int,
        y: int,
        player_snake: "Snake",
        ai_snake: "Snake",
    ) -> bool:
        if (x, y) in self._obstacle_cells:
            return self.destroy_obstacle(x, y)
        else:
            return self.place_obstacle(x, y, player_snake, ai_snake)

    # reset rounds
    def clear_all_obstacles(self) -> None:
        for x, y in list(self._obstacle_cells):
            self.board.tiles[x][y].set_blocked(False)
        self._obstacle_cells.clear()

    @property
    def obstacle_cells(self) -> Set[Tuple[int, int]]:
        return frozenset(self._obstacle_cells)

    @property
    def obstacle_count(self) -> int:
        return len(self._obstacle_cells)

    def is_player_obstacle(self, x: int, y: int) -> bool:
        return (x, y) in self._obstacle_cells

    # debug
    def __repr__(self) -> str:
        return (
            f"PlayerController("
            f"moves_remaining={self.moves_remaining}/{self.MAX_MOVES}, "
            f"obstacles={self.obstacle_count}/{self.MAX_OBSTACLES})"
        )