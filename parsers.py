from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from interfaces import Parser

PARSER_STRATEGY_REGISTER : Dict[str, Parser] = {
}

def register_parser(name:str):
    """Decorator to register a parser class"""
    def decorator(cls):
        PARSER_STRATEGY_REGISTER[name] = cls
        return cls
    return decorator

@register_parser('dummy')
class dummyParser(Parser):
    def parse(self, filepath: str) -> Any:
        return True