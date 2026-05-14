class Tile:
    def __init__(self):
        self.is_blocked = False
        self.is_goal = False
        self.occupant: str | None = None # 'player' | 'computer' | None
    
    def set_blocked(self, is_blocked) -> None:
        self.is_blocked = is_blocked
        if is_blocked:
            self.is_goal = False
            self.occupant = None
    
    def set_as_goal(self) -> None:
        self.is_goal = True
    
    def check_blocked(self) -> bool:
        return self.is_blocked

    def check_is_goal(self):
        return self.is_goal

    def set_occupant(self, owner: str | None) -> None:
        self.occupant = owner

    def check_occupant(self) -> str | None:
        return self.occupant

    def __repr__(self) -> str:
        if self.is_goal:
            return "T(G)"
        if self.is_blocked:
            return "T(#)"
        if self.occupant:
            return f"T({self.occupant[0].upper()})"
        
        return "T()"
