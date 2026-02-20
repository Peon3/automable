from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from interfaces import Analyzer

ANALYZER_STRATEGY_REGISTER : Dict[str, Analyzer] = {
}

def register_analyzer(name:str):
    """Decorator to register an analyzer class"""
    def decorator(cls):
        ANALYZER_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

@register_analyzer('dummy')
class dummyAnalyzer(Analyzer):
    def analyze(self, job_data: Any) -> bool:
        return True