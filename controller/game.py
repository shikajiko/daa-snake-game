from typing import Callable, Dict, Optional, Tuple

from controller.dijkstra import dijkstra
from controller.player import PlayerController
from model.board import Board
from model.snake import Snake

class GameController:
    def __init__(
        self,
        board_size: int,
        max_actions: int,
        on_board_changed: Optional[Callable[[], None]] = None,
    ) -> None:
        self.board = Board(board_size, board_size)
        self.board.generate_maze()
        self.player_snake, self.computer_snake = self.board.spawn_snakes()
        self.player_controller = PlayerController(self.board, max_actions)
        self.board.on_board_changed = self._handle_board_changed
        self.on_board_changed = on_board_changed

        self.running = True
        self.enemy_stuck_ticks = 0
        self.path_by_owner: Dict[str, int] = {"player": 0, "computer": 0}

        self.replan_paths()

    def toggle_obstacle(self, x: int, y: int) -> bool:
        return self.player_controller.toggle_obstacle(
            x,
            y,
            self.player_snake,
            self.computer_snake,
        )

    def tick(self) -> Optional[str]:
        if not self.running:
            return self.board.get_winner()

        if not self.player_snake.has_path():
            self.plan_snake_path(self.player_snake, self.computer_snake)
        if not self.computer_snake.has_path():
            self.plan_snake_path(self.computer_snake, self.player_snake)

        self._handle_enemy_stuck()
        self._move_snakes_simultaneously()

        if self.board.is_game_over():
            self.running = False
            return self.board.get_winner()

        return None

    def replan_paths(self) -> None:
        self.plan_snake_path(self.player_snake, self.computer_snake)
        self.plan_snake_path(self.computer_snake, self.player_snake)

    def plan_snake_path(self, snake: Snake, other_snake: Snake) -> None:
        if not snake.alive:
            return

        path = dijkstra(self.board, snake.head, self.board.get_goal_pos(), snake, other_snake)
        if path:
            snake.set_path(path)
            self.path_by_owner[snake.owner] = len(path)

    def _handle_board_changed(self) -> None:
        self.replan_paths()
        if callable(self.on_board_changed):
            self.on_board_changed()

    def _handle_enemy_stuck(self) -> None:
        if not self.computer_snake.alive:
            self.enemy_stuck_ticks = 0
            return

        blocked_target = self._get_enemy_blocked_target()
        if blocked_target is None:
            self.enemy_stuck_ticks = 0
            return

        self.enemy_stuck_ticks += 1
        if self.enemy_stuck_ticks <= 5:
            return

        x, y = blocked_target
        if self.board.tiles[x][y].check_blocked() and self.board.remove_obstacle(x, y):
            self.enemy_stuck_ticks = 0

    def _get_enemy_blocked_target(self) -> Optional[Tuple[int, int]]:
        target = self.computer_snake.peak_next()
        if target is None:
            dx, dy = self.computer_snake.direction
            target = (self.computer_snake.head_x + dx, self.computer_snake.head_y + dy)

        x, y = target
        if not (0 <= x < self.board.size_x and 0 <= y < self.board.size_y):
            return None

        if self.board.tiles[x][y].check_blocked():
            return target

        return None

    def _move_snakes_simultaneously(self) -> None:
        moves = {
            self.player_snake: self.player_snake.peak_next() if self.player_snake.alive else None,
            self.computer_snake: self.computer_snake.peak_next() if self.computer_snake.alive else None,
        }
        if not any(target is not None for target in moves.values()):
            return

        target_counts: Dict[Tuple[int, int], int] = {}
        for target in moves.values():
            if target is not None:
                target_counts[target] = target_counts.get(target, 0) + 1

        blocked_targets = set()
        for snake, target in moves.items():
            if target is None:
                continue

            if target_counts[target] > 1:
                if self.board.check_goal(*target):
                    snake.mark_reached_goal()
                    snake.clear_path()
                else:
                    blocked_targets.add(snake)
                continue

            if self._is_blocked_wall_target(target):
                continue

            if not self._can_snake_enter(snake, target, moves):
                blocked_targets.add(snake)

        for snake in blocked_targets:
            snake.kill()
            snake.clear_path()

        for snake, target in moves.items():
            if target is None or snake in blocked_targets or not snake.alive:
                continue
            if self._is_blocked_wall_target(target):
                continue
            snake.planned_path.popleft()
            self.board.move_snake_to(snake, *target)

    def _is_blocked_wall_target(self, target: Tuple[int, int]) -> bool:
        x, y = target
        if not (0 <= x < self.board.size_x and 0 <= y < self.board.size_y):
            return False

        return self.board.tiles[x][y].check_blocked()

    def _can_snake_enter(
        self,
        snake: Snake,
        target: Tuple[int, int],
        moves: Dict[Snake, Optional[Tuple[int, int]]],
    ) -> bool:
        x, y = target
        if not (0 <= x < self.board.size_x and 0 <= y < self.board.size_y):
            return False

        tile = self.board.tiles[x][y]
        if tile.check_blocked():
            return False
        if tile.check_is_goal():
            return True

        for other in (self.player_snake, self.computer_snake):
            if not other.occupies(x, y):
                continue

            other_target = moves.get(other)
            if target == other.tail and other_target is not None:
                continue
            return False

        return True