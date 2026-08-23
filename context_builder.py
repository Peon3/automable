from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from interfaces import ContextBuilder

CONBUILDER_STRATEGY_REGISTER : Dict[str, ContextBuilder] = {
}

def register_conbuilder(name:str):
    """Decorator to register a context builder class"""
    def decorator(cls):
        CONBUILDER_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

@register_conbuilder('dummy')
class dummyConBuilder(ContextBuilder):
    def build_context(self, job_data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        return {}