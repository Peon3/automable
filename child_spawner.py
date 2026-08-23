from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from interfaces import ChildSpawner

CHILDSPAWNER_STRATEGY_REGISTER : Dict[str, ChildSpawner] = {
}

def register_child_spawner(name:str):
    """Decorator to register a child spawner class"""
    def decorator(cls):
        CHILDSPAWNER_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

@register_child_spawner('dummy')
class dummyChildSpawner(ChildSpawner):
    def spawn(self, job_data: Any) -> bool:
        return True