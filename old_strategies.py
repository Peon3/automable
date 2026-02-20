from abc import ABC, abstractmethod

# 1. Strategy Interfaces
class PreValidator(ABC):
    """Strategy for pre-calculation checks."""
    @abstractmethod
    def pre_validate(self) -> bool:
        pass

class PostValidator(ABC):
    """Strategy for post-calculation validation."""
    @abstractmethod
    def post_validate(self) -> bool:
        pass

# 2. Concrete Strategy Implementations
class SimplePreValidator(PreValidator):
    def pre_validate(self) -> bool:
        print("Executing Simple Pre-Validation...")
        return True

class ComplexPreValidator(PreValidator):
    def pre_validate(self) -> bool:
        print("Executing Complex Pre-Validation...")
        return True

class SimplePostValidator(PostValidator):
    def post_validate(self) -> bool:
        print("Executing Simple Post-Validation...")
        return True

class StrictPostValidator(PostValidator):
    def post_validate(self) -> bool:
        print("Executing Strict Post-Validation...")
        return True