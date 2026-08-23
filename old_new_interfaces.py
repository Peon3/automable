from abc import ABC, abstractmethod
from typing import List, Dict, Any

class PreValidator(ABC):
    """
    Strategy for pre calculation checks e.g. sanity TODO: implement
    """
    @abstractmethod
    def preValidate(self, job_data: Any) -> bool:
        pass

class PreCalcSoftFix(ABC):
    """
    Strategy for some selfhealing mechanisms, if explicilty called in input, never should be default. TODO: implement
    """
    @abstractmethod
    def selfHeal(self, job_data: Any) -> bool:
        pass

class ContextBuilder(ABC):
    """
    Strategy for preparing the context dictionary for template rendering.
    """
    @abstractmethod
    def build_context(self, job_data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        pass

class InputBuilder(ABC):
    """
    Strategy for building input files from templates and job data.
    """
    @abstractmethod
    def build_input(self, job_data: Any, template_path: str) -> str:
        pass


class Parser(ABC):
    """
    Docstring for Parser
    """
    @abstractmethod
    def parse(self, filepath: str) -> Any:
        pass

class PostValidator(ABC):
    """
    Strategy pattern, valdiates in place, returns bool TODO: implement
    """
    @abstractmethod
    def postValidate(self, job_results: dict) -> bool:
        pass

class Analyzer(ABC):
    """
    Strategy pattern, idea is that it produces files with prepared data and/or executables that produce images. TODO: implement
    """
    @abstractmethod
    def analyze(self, job_data: Any) -> bool:
        pass

class ErrorHandler(ABC):
    """
    Strategy pattern, tries to fix things with e.g. spawning a rescue job or alike, has to return bool (and sometimes (rescue) job object?) TODO: implement
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
    def spawn(self, job_data: Any) -> bool:
        pass