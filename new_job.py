from abc import ABC, abstractmethod
from typing import List, Dict, Any

class PostValidator(ABC):
    """
    Strategy pattern, valdiates in place, returns bool
    """
    @abstractmethod
    def postValidate(self, job_results: dict) -> bool:
        pass

class Analyzer(ABC):
    """
    Strategy pattern, idea is that it produces files with prepared data and/or executables that produce images. TODO: implement
    """
    @abstractmethod
    def analyze(self, job_data: Any) -> Any:
        pass

class ErrorHandler(ABC):
    """
    Strategy pattern, tries to fix things with e.g. spawning a rescue job or alike, has to return bool (and sometimes (rescue) job object?)
    """
    @abstractmethod
    #def handle(self, job_data: Any) -> List[bool, Any]:
    def handle(self, job_data: Any) -> bool:
        pass

class ChildSpawner(ABC):
    """
    Strategy pattern, spwans child calculations and returns a list of job objects. TODO: implement
    """
    @abstractmethod
    def spawn(self, job_data: Any) -> List[Any]:
        pass

class PreValidator(ABC):
    """
    Strategy for pre calculation checks e.g. sanity 
    """
    @abstractmethod
    def preValidate(self, job_data: Any) -> bool:
        pass

class PreCalcSoftFixer(ABC):
    """
    Strategy for some selfhealing mechanisms, if explicilty called in input, never should be default. TODO: implement
    """
    @abstractmethod
    def selfHeal(self, job_data: Any) -> bool:
        pass

class PreCalcManager:
    def __init__(self,
                 tests: List[PreValidator] = None):
        
        self.tests = tests or []
    
    def run(self, job_data: dict) -> bool:
        is_validated = True
        for t in self.tests:
            if not t.preValidate(job_data):
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
            if not v.postValidate(job_data):
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