from enum import Enum
from .new_interfaces import Parser


class RegParsers(str, Enum):
    ORCA_SCF_ENERGY = "ORCA_SCF_ENERGY"
    ORCA_FREQ_ENERGY = "ORCA_FREQ_ENERGY"
    ORCA_FREQ_FREQUENCIES = "ORCA_FREQ_FREQUENCIES"
    ORCA_FREQ_DISPLACEMENT = "ORCA_FREQ_DISPLACEMENT"

class ParsORCASCFEnergy(Parser):
    def parse(self, filepath: str) -> float:
        # Implementation for parsing ORCA SCF energy
        pass

class ParsORCAFreqEnergy(Parser):
    def parse(self, filepath: str) -> float:
        # Implementation for parsing ORCA Frequency energy
        pass

class ParsORCAFreqFrequencies(Parser):
    def parse(self, filepath: str) -> list[float]:
        # Implementation for parsing ORCA frequencies
        pass

class ParsORCAFreqDisplacement(Parser):
    def parse(self, filepath: str) -> float:
        # Implementation for parsing ORCA displacement
        pass

def main():
    pass

if __name__ == "__main__":
    main()