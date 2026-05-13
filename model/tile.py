class Tile:
    def __init__(self):
        self.is_blocked = False
        self.is_goal = False
    
    def set_blocked(self, is_blocked):
        self.is_blocked = is_blocked
    
    def set_as_goal(self):
        self.is_goal = True
    
    def check_blocked(self):
        return self.is_blocked

    def check_is_goal(self):
        return self.is_goal