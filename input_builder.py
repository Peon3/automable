from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from interfaces import InputBuilder

INBUILDER_STRATEGY_REGISTER : Dict[str, InputBuilder] = {
}

def register_inbuilder(name:str):
    """Decorator to register a input builder class"""
    def decorator(cls):
        INBUILDER_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

@register_inbuilder('dummy')
class dummyInBuilder(InputBuilder):
    def build_input(self, job_data: Any, template_path: str) -> bool:
        return True