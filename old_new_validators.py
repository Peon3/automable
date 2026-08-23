from enum import Enum
from .new_interfaces import PostValidator, PreValidator

class RegValidators(str, Enum):
    GEOM_MINIMUM = "GEOM_MINIMUM"
    GEOM_CONVERGED = "GEOM_CONVERGED"
    SCF_CONVERGED = "SCF_CONVERGED"
    GEOM_SADDLEPOINT = "GEOM_SADDLEPOINT"  

class ValGeomMinimum(PostValidator):
    def postValidate(self, job_results: dict) -> bool:
        pass

class ValGeomConv(PostValidator):
    def postValidate(self, job_results: dict) -> bool:
        pass

class ValSCFConv(PostValidator):
    def postValidate(self, job_results: dict) -> bool:
        pass

class ValGeomSaddlepoint(PostValidator):
    def postValidate(self, job_results: dict) -> bool:
        pass

def main():
    pass

if __name__ == "__main__":
    main()