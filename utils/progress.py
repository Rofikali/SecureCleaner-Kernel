import sys


class ProgressBar:
    """
    DSA: Linear Mapping. Maps (current/total) to a 0-100% scale.
    Pattern: Singleton-ready utility.
    """

    def __init__(self, total, prefix="Progress:", suffix="Complete", length=30):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length

    def update(self, iteration):
        percent = ("{0:.1f}").format(100 * (iteration / float(self.total)))
        filled_length = int(self.length * iteration // self.total)
        bar = "█" * filled_length + "-" * (self.length - filled_length)
        # Using \r (carriage return) for in-place terminal updates
        sys.stdout.write(f"\r{self.prefix} |{bar}| {percent}% {self.suffix}")
        sys.stdout.flush()
        if iteration == self.total:
            print()  # New line on finish
