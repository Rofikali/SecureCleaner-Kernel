from abc import ABC, abstractmethod
import os


class SortingStrategy(ABC):
    @abstractmethod
    def get_folder(self, filename):
        pass


class ExtensionStrategy:
    def __init__(self, mappings):
        self.mappings = mappings

    def get_folder(self, filename):
        import os

        ext = os.path.splitext(filename)[1].lower()
        for folder, extensions in self.mappings.items():
            if ext in extensions:
                return folder
        return "Others"
