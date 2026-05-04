class MetricsTracker:
    def __init__(self):
        self.files_moved = 0
        self.errors = 0
        self.history = []
        self.silent_mode = False  # NEW: Global flag for notifications

    def add_history(self, action):
        self.history.insert(0, action)
        if len(self.history) > 5:
            self.history.pop()

    def report(self):
        return f"Stats: {self.files_moved} moved, {self.errors} failed."


metrics = MetricsTracker()
