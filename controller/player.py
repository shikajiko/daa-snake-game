from typing import Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from model.board import Board
    from model.snake import Snake

class PlayerController:
    def __init__(self, board: "Board", max_actions: int = 3) -> None:
        if max_actions < 1:
            raise ValueError("max_actions must be at least 1")

        self.board = board
        self.max_actions = max_actions
        self.actions_remaining: int = max_actions
        self._obstacle_cells: Set[Tuple[int, int]] = set()

    # round management
    def reset_actions(self) -> None:
        self.actions_remaining = self.max_actions

    def skip_remaining(self) -> None:
        self.actions_remaining = 0

    # validation helpers
    def can_place(
        self,
        x: int,
        y: int,
        player_snake: "Snake",
        ai_snake: "Snake",
    ) -> bool:
        if self.actions_remaining <= 0:
            return False
        if not (0 <= x < self.board.size_x and 0 <= y < self.board.size_y):
            return False

        tile = self.board.tiles[x][y]
        if tile.check_blocked():
            return False
        if tile.check_is_goal():
            return False
        if self.board.is_goal_protected_zone(x, y):
            return False
        if player_snake.occupies(x, y):
            return False
        if ai_snake.occupies(x, y):
            return False

        return True

    def can_destroy(self, x: int, y: int) -> bool:
        if self.actions_remaining <= 0:
            return False
        if not (0 <= x < self.board.size_x and 0 <= y < self.board.size_y):
            return False

        tile = self.board.tiles[x][y]
        return tile.check_blocked()

    def has_actions(self) -> bool:
        return self.actions_remaining > 0

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

        if not self.board.add_obstacle(x, y):
            return False

        self._obstacle_cells.add((x, y))
        self.actions_remaining -= 1
        return True

    def destroy_obstacle(self, x: int, y: int) -> bool:
        if not self.can_destroy(x, y):
            return False

        if not self.board.remove_obstacle(x, y):
            return False

        self._obstacle_cells.discard((x, y))
        self.actions_remaining -= 1
        return True

    def toggle_obstacle(
        self,
        x: int,
        y: int,
        player_snake: "Snake",
        ai_snake: "Snake",
    ) -> bool:
        if self.actions_remaining <= 0:
            return False

        tile = self.board.tiles[x][y]
        if tile.check_blocked():
            return self.destroy_obstacle(x, y)

        return self.place_obstacle(x, y, player_snake, ai_snake)

    # reset rounds
    def clear_all_obstacles(self) -> None:
        for x, y in list(self._obstacle_cells):
            self.board.remove_obstacle(x, y)
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
            f"actions_remaining={self.actions_remaining}/{self.max_actions}, "
            f"obstacles={self.obstacle_count})"
        )
