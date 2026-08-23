from enum import Enum
from .new_interfaces import ChildSpawner

class RegChildSpawners(str, Enum):
    NEB = "NEB"
    IRC = "IRC"

class ChildSpawnerNEB(ChildSpawner):
    def spawn(self, job_data: dict) -> None:
        pass

class ChildSpawnerIRC(ChildSpawner):
    def spawn(self, job_data: dict) -> None:
        pass

def main():
    pass

if __name__ == "__main__":
    main()