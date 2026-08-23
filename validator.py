from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from interfaces import PreValidator, PostValidator

PREVALIDATOR_STRATEGY_REGISTER : Dict[str, PreValidator] = {
}
PREVALIDATOR_STRATEGY_REGISTER : Dict[str, PreValidator] = {
}

def register_prevalidator(name:str):
    """Decorator to register a prevalidator class"""
    def decorator(cls):
        PREVALIDATOR_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

def register_postvalidator(name:str):
    """Decorator to register a postvalidator class"""
    def decorator(cls):
        PREVALIDATOR_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

@register_prevalidator('dummy')
class dummyPreValidator(PreValidator):
    def preValidate(self, job_data: Any) -> bool:
        return True
    
@register_postvalidator('dummy')
class dummyPostValidator(PostValidator):
    def postValidate(self, job_data: Dict) -> bool:
        return True