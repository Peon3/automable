from enum import Enum
from .new_interfaces import ErrorHandler

class RegErrorHandlers(str, Enum):
    RESCUE = "RESCUE"

class ErrRescue(ErrorHandler):
    def handle(self, job_data: dict) -> bool:
        pass

def main():
    pass

if __name__ == "__main__":
    main()