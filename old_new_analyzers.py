from enum import Enum
from .new_interfaces import Analyzer

class RegAnalyzers(str, Enum):
    PLOT = "PLOT"

class AnaPlot(Analyzer):
    def analyze(self, job_data: dict) -> None:
        pass

def main():
    pass

if __name__ == "__main__":
    main()