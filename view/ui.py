import tkinter as tk
from tkinter import messagebox
from typing import Optional

from controller.game import GameController


class SnakeGameApp:
    MIN_BOARD_SIZE = 10
    MAX_BOARD_SIZE = 60
    BOARD_STEP = 2
    MIN_TICK_SPEED = 0.2
    MAX_TICK_SPEED = 2.0
    CANVAS_SIZE = 840
    WINDOW_MARGIN = 96
    GAME_CHROME_HEIGHT = 92

    COLOR_BG = "#101418"
    COLOR_PANEL = "#1c232b"
    COLOR_TEXT = "#f4f7fa"
    COLOR_MUTED = "#a8b3bd"
    COLOR_GRID = "#2e3944"
    COLOR_EMPTY = "#151b21"
    COLOR_WALL = "#67727e"
    COLOR_GOAL = "#f2c94c"
    COLOR_PROTECTED = "#f2994a"
    COLOR_PLAYER = "#2ecc71"
    COLOR_COMPUTER = "#e74c3c"

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Dijkstra Snake Race")
        self.root.configure(bg=self.COLOR_BG)
        self.root.resizable(False, False)

        self.game: Optional[GameController] = None
        self.tick_speed = 0.5
        self.cell_size = 24
        self.tick_after_id: Optional[str] = None

        self.menu_frame: Optional[tk.Frame] = None
        self.game_frame: Optional[tk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.status_var = tk.StringVar()

        self.board_size_var = tk.IntVar(value=20)
        self.actions_var = tk.StringVar(value="10")
        self.tick_speed_var = tk.DoubleVar(value=0.5)
        self.current_board_size = self.board_size_var.get()
        self.current_actions = int(self.actions_var.get())

        self._build_menu()

    def run(self) -> None:
        self.root.mainloop()

    def _build_menu(self) -> None:
        self._clear_root()
        self.menu_frame = tk.Frame(self.root, bg=self.COLOR_BG, padx=32, pady=28)
        self.menu_frame.pack(fill="both", expand=True)

        title = tk.Label(
            self.menu_frame,
            text="Dijkstra Snake Race",
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            font=("Segoe UI", 22, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0, 22))

        self._add_menu_label("Actions", 1)
        actions_entry = tk.Entry(
            self.menu_frame,
            textvariable=self.actions_var,
            width=12,
            justify="center",
            font=("Segoe UI", 12),
        )
        actions_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=8)

        self._add_menu_label("Board size", 2)
        board_spin = tk.Spinbox(
            self.menu_frame,
            from_=self.MIN_BOARD_SIZE,
            to=self.MAX_BOARD_SIZE,
            increment=self.BOARD_STEP,
            textvariable=self.board_size_var,
            width=10,
            justify="center",
            font=("Segoe UI", 12),
            command=self._normalize_board_size,
        )
        board_spin.grid(row=2, column=1, sticky="ew", padx=10, pady=8)

        self._add_menu_label("Tick speed", 3)
        tick_spin = tk.Spinbox(
            self.menu_frame,
            from_=self.MIN_TICK_SPEED,
            to=self.MAX_TICK_SPEED,
            increment=0.1,
            format="%.1f",
            textvariable=self.tick_speed_var,
            width=10,
            justify="center",
            font=("Segoe UI", 12),
            command=self._normalize_tick_speed,
        )
        tick_spin.grid(row=3, column=1, sticky="ew", padx=10, pady=8)
        tk.Label(
            self.menu_frame,
            text="seconds",
            bg=self.COLOR_BG,
            fg=self.COLOR_MUTED,
            font=("Segoe UI", 10),
        ).grid(row=3, column=2, sticky="w")

        start_button = tk.Button(
            self.menu_frame,
            text="Start",
            command=self._start_game,
            bg=self.COLOR_PLAYER,
            fg="#07120b",
            activebackground="#31de78",
            activeforeground="#07120b",
            relief="flat",
            padx=22,
            pady=10,
            font=("Segoe UI", 12, "bold"),
        )
        start_button.grid(row=4, column=0, columnspan=3, pady=(22, 0), sticky="ew")

    def _add_menu_label(self, text: str, row: int) -> None:
        tk.Label(
            self.menu_frame,
            text=text,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            font=("Segoe UI", 11),
        ).grid(row=row, column=0, sticky="w", pady=8)

    def _build_game_view(self) -> None:
        self._clear_root()
        self.game_frame = tk.Frame(self.root, bg=self.COLOR_BG, padx=16, pady=16)
        self.game_frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(self.game_frame, bg=self.COLOR_BG)
        top_bar.pack(fill="x", pady=(0, 12))

        tk.Label(
            top_bar,
            textvariable=self.status_var,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            font=("Segoe UI", 11),
        ).pack(side="left")

        tk.Button(
            top_bar,
            text="Menu",
            command=self._return_to_menu,
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXT,
            activebackground="#27313b",
            activeforeground=self.COLOR_TEXT,
            relief="flat",
            padx=12,
            pady=6,
            font=("Segoe UI", 10),
        ).pack(side="right")

        canvas_length = self.cell_size * self.game.board.size_x
        self.canvas = tk.Canvas(
            self.game_frame,
            width=canvas_length,
            height=canvas_length,
            bg=self.COLOR_EMPTY,
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_board_click)

    def _start_game(self) -> None:
        try:
            board_size = self._normalize_board_size()
            actions = self._parse_actions()
            self.tick_speed = self._normalize_tick_speed()
        except ValueError as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return

        self.game = GameController(board_size, actions, on_board_changed=self._draw_board)
        self.cell_size = max(8, self._get_canvas_target_size() // board_size)
        self.current_board_size = board_size
        self.current_actions = actions

        self._build_game_view()
        self._draw_board()
        self._show_how_to_play_popup(self._schedule_next_tick)

    def _get_canvas_target_size(self) -> int:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        available_width = max(320, screen_width - self.WINDOW_MARGIN)
        available_height = max(320, screen_height - self.WINDOW_MARGIN - self.GAME_CHROME_HEIGHT)
        return min(self.CANVAS_SIZE, available_width, available_height)

    def _normalize_board_size(self) -> int:
        try:
            value = int(self.board_size_var.get())
        except (TypeError, tk.TclError, ValueError):
            raise ValueError("Board size must be an even number.")

        value = max(self.MIN_BOARD_SIZE, min(self.MAX_BOARD_SIZE, value))
        if value % self.BOARD_STEP != 0:
            value += self.BOARD_STEP - (value % self.BOARD_STEP)
        self.board_size_var.set(value)
        return value

    def _normalize_tick_speed(self) -> float:
        try:
            value = float(self.tick_speed_var.get())
        except (TypeError, tk.TclError, ValueError):
            raise ValueError("Tick speed must be a number.")

        value = max(self.MIN_TICK_SPEED, min(self.MAX_TICK_SPEED, value))
        value = round(value, 1)
        self.tick_speed_var.set(value)
        return value

    def _parse_actions(self) -> int:
        try:
            actions = int(self.actions_var.get())
        except ValueError:
            raise ValueError("Actions must be a whole number from 1 upward.")
        if actions < 1:
            raise ValueError("Actions must be at least 1.")
        return actions

    def _handle_board_click(self, event: tk.Event) -> None:
        if not self.game or not self.game.running:
            return

        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if not (0 <= x < self.game.board.size_x and 0 <= y < self.game.board.size_y):
            return

        changed = self.game.toggle_obstacle(x, y)
        if changed:
            self._draw_board()
            self._update_status()

    def _schedule_next_tick(self) -> None:
        if not self.game or not self.game.running:
            return
        delay_ms = int(self.tick_speed * 1000)
        self.tick_after_id = self.root.after(delay_ms, self._tick)

    def _tick(self) -> None:
        self.tick_after_id = None
        if not self.game:
            return

        winner = self.game.tick()
        self._draw_board()
        if winner is not None:
            self._finish_game(winner)
            return

        self._schedule_next_tick()

    def _draw_board(self) -> None:
        if not self.game or not self.canvas:
            return

        board = self.game.board
        self.canvas.delete("all")
        size = self.cell_size
        for y in range(board.size_y):
            for x in range(board.size_x):
                tile = board.tiles[x][y]
                color = self.COLOR_EMPTY
                if tile.check_is_goal():
                    color = self.COLOR_GOAL
                elif tile.check_blocked():
                    color = self.COLOR_WALL
                elif tile.check_occupant() == "player":
                    color = self.COLOR_PLAYER
                elif tile.check_occupant() == "computer":
                    color = self.COLOR_COMPUTER
                elif board.is_goal_protected_zone(x, y):
                    color = self.COLOR_PROTECTED

                self.canvas.create_rectangle(
                    x * size,
                    y * size,
                    (x + 1) * size,
                    (y + 1) * size,
                    fill=color,
                    outline=self.COLOR_GRID,
                    width=1,
                )

        self._draw_heads()
        self._update_status()

    def _draw_heads(self) -> None:
        if not self.game or not self.canvas:
            return

        for snake, color in (
            (self.game.board.player_snake, "#11582e"),
            (self.game.board.computer_snake, "#7f1d18"),
        ):
            if not snake:
                continue
            x, y = snake.head
            pad = max(2, self.cell_size // 5)
            self.canvas.create_oval(
                x * self.cell_size + pad,
                y * self.cell_size + pad,
                (x + 1) * self.cell_size - pad,
                (y + 1) * self.cell_size - pad,
                fill=color,
                outline="",
            )

    def _update_status(self) -> None:
        if not self.game:
            return

        self.status_var.set(f"Actions: {self.game.player_controller.actions_remaining}")

    def _finish_game(self, winner: str) -> None:
        result_text = "You win" if winner == "Player" else "You lose"
        self.status_var.set(result_text)
        self._show_game_over_popup(result_text)

    def _show_how_to_play_popup(self, on_start) -> None:
        popup = self._create_popup("How to play")
        popup.protocol("WM_DELETE_WINDOW", lambda: None)

        message = (
            "Make the green snake reach the goal first by placing or breaking walls!\n\n"
            "Click on a wall to break them, or click on an empty tile to create a wall.\n\n"
            "Be careful: you can't break or place anymore when your action runs out.\n"
            "You also can't place on an orange tile."
        )
        tk.Label(
            popup,
            text=message,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            wraplength=420,
            justify="left",
            font=("Segoe UI", 11),
        ).pack(padx=22, pady=(22, 16))

        def start() -> None:
            popup.destroy()
            on_start()

        tk.Button(
            popup,
            text="Start",
            command=start,
            bg=self.COLOR_PLAYER,
            fg="#07120b",
            activebackground="#31de78",
            activeforeground="#07120b",
            relief="flat",
            padx=24,
            pady=8,
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 22))

    def _show_game_over_popup(self, result_text: str) -> None:
        popup = self._create_popup("Game over")
        popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup_and_return_to_menu(popup))

        tk.Label(
            popup,
            text=result_text,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack(padx=28, pady=(24, 18))

        buttons = tk.Frame(popup, bg=self.COLOR_BG)
        buttons.pack(padx=20, pady=(0, 22))

        tk.Button(
            buttons,
            text="Restart",
            command=lambda: self._restart_game(popup),
            bg=self.COLOR_PLAYER,
            fg="#07120b",
            activebackground="#31de78",
            activeforeground="#07120b",
            relief="flat",
            padx=18,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=6)

        tk.Button(
            buttons,
            text="Main menu",
            command=lambda: self._close_popup_and_return_to_menu(popup),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXT,
            activebackground="#27313b",
            activeforeground=self.COLOR_TEXT,
            relief="flat",
            padx=18,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=6)

    def _create_popup(self, title: str) -> tk.Toplevel:
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=self.COLOR_BG)
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 220
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 120
        popup.geometry(f"+{max(0, x)}+{max(0, y)}")
        return popup

    def _restart_game(self, popup: tk.Toplevel) -> None:
        popup.destroy()
        self.board_size_var.set(self.current_board_size)
        self.actions_var.set(str(self.current_actions))
        self._start_game()

    def _close_popup_and_return_to_menu(self, popup: tk.Toplevel) -> None:
        popup.destroy()
        self._return_to_menu()

    def _return_to_menu(self) -> None:
        if self.game:
            self.game.running = False
        if self.tick_after_id:
            self.root.after_cancel(self.tick_after_id)
            self.tick_after_id = None
        self._build_menu()

    def _clear_root(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()


def run_app() -> None:
    SnakeGameApp().run()