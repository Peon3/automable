from abc import ABC, abstractmethod
from typing import List, Any

class PostValidator(ABC):
    """
    Strategy for Validator, does all kinds of job validation w.r.t. results
    """
    @abstractmethod
    def post_validate(self, job_results: dict) -> bool:
        pass

class Analyzer(ABC):
    """
    Strategy for Analyzer, does  all kinds of analysis
    """
    @abstractmethod
    def analyze(self, job_data: Any) -> Any:
        pass

class ErrorHandler(ABC):
    """
    Strategy for ErrorHandler, does error thingies
    """
    @abstractmethod
    def handle(self, job_data: Any) -> bool:
        pass

class ChildSpawner(ABC):
    """
    Strategy for ChildSpawner, supposed to spawn child calulations
    """
    @abstractmethod
    def spawn(self, job_data: Any) -> List[Any]:
        pass

class PreValidator(ABC):
    """
    Strategy for pre calculation checks e.g. sanity 
    """
    @abstractmethod
    def pre_validate(self, job_data: Any) -> bool:
        pass

class PreCalcSoftFixer(ABC):
    """
    Strategy for some selfhealing mechanisms, if explicilty called in input, never should be default. TODO: implement
    """
    @abstractmethod
    def self_heal(self, job_data: Any) -> bool:
        pass

class PreCalcManager:
    def __init__(self,
                 tests: List[PreValidator] = None):
        
        self.tests = tests or []
    
    def run(self, job_data: dict) -> bool:
        is_validated = True
        for t in self.tests:
            if not t.pre_validate(job_data):
                print(f"--- Pre calc validation failed with {t.__class__.__name__} ---")
                is_validated = False
                break
        
        if is_validated:
            print(f"--- Pre calc validation succesfull ---")

        return is_validated


class PostCalcManager:
    def __init__(self,
                 post_validators: List[PostValidator] = None,
                 analyzers: List[Analyzer] = None,
                 error_handlers: List[ErrorHandler] = None,
                 child_spawners: List[ChildSpawner] = None
                 ):
        self.post_validators = post_validators or []
        self.analyzers = analyzers or []
        self.error_handlers: dict[str, ErrorHandler] = {h.__class__.__name__: h for h in (error_handlers or [])}
        self.child_spawners = child_spawners or []

    def run(self, job_data: dict) -> bool:
        is_validated = True
        for v in self.post_validators:
            if not v.post_validate(job_data):
                print(f"--- Post calc validation failed with {v.__class__.__name__} ---")
                handler = self.error_handlers.get(v.__class__.__name__)
                if handler and handler.handle(job_data):
                    print(f"--- Error handler {handler.__class__.__name__} successful ---")
                    continue 
                is_validated = False
                break
        
        if is_validated:
            print(f"--- Post calc validation succesfull ---")

            for a in self.analyzers:
                a.analyze(job_data)
            for c in self.child_spawners:
                c.spawn(job_data)

        return is_validated