from abc import ABC, abstractmethod
from typing import List, Any, Protocol
from dataclasses import dataclass
from .new_interfaces import PreValidator, PreCalcSoftFix, ContextBuilder, InputBuilder, Parser, PostValidator, Analyzer, ErrorHandler, ChildSpawner


@dataclass
class PreCalcManager:
    """
    Wrapper dataclass for gathering specific strategies concerning pre calculation setup.
    """
    preValidators: List[PreValidator]
    preCalcSoftFixes: dict[str, PreCalcSoftFix]
    
    def run(self, job_data: dict) -> bool:
        validate: dict[str, bool] = {}
        for test in self.preValidators:
            validate[test.__class__.__name__] = test.preValidate(self, job_data)
        if False in validate.values():
            for k, v in validate.items():
                if not v:
                    print(f"--- Pre calc validation failed for {k} ---")
                    if k in self.preCalcSoftFixes:
                        for heal in self.preCalcSoftFixes.get(k):
                            print(f"--- Attempting soft fix with {heal.__class__.__name__} ---")
                            if not heal.selfHeal(self, job_data):
                                print(f"--- Pre calc soft fix failed ---")
                                return False
                            else:
                                print(f"--- Pre calc soft fix succesfull ---")
                                return True
        print(f"--- Pre calc validation succesfull ---")
        return True

@dataclass
class CalcSetuper:
    """
    Wrapper dataclass for gathering specific strategy concerning calculation setup.
    """
    contextBuilder = ContextBuilder
    inputBuilder = InputBuilder

    def run(self, job_data: dict) -> bool:
        self.contextBuilder.build_context(self, job_data)
        self.inputBuilder.build_input(self, job_data)
        return True

@dataclass
class PostCalcManager:
    """
    Wrapper dataclass for gathering specific strategies concerning calculation post processing.
    """
    parsers: List[Parser]
    postValidators: List[PostValidator]
    analyzers: List[Analyzer]
    errorHandlers: dict[str, ErrorHandler]
    childSpawners: List[ChildSpawner]

    def run(self, job_data: dict) -> bool:
        print(f"--- Running post calc ---")
        print(f"Parsing...          ", end="")
        for p in self.parsers:
            p.parse(self, job_data)
        print(f"completed")
        print(f"Validating...       ", end="")
        validate: dict[str, bool] = {}
        for test in self.postValidators:
            validate[test.__class__.__name__] = test.postValidate(self, job_data)
        print(f"completed")
        if False in validate.values():
            print(f"Trying to handle errors automatically...    ")
            for k, v in validate.items():
                if not v:
                    print(f"            Validaton failed for {k}")
                    if k in self.errorHandlers:
                        for handler in self.errorHandlers.get(k):
                            print(f"            attempting {handler.__class__.__name__} --- ", end='')
                            if not handler.handle(self, job_data):
                                print(f"successfull")
                                break
                            else:
                                print(f"failed")
                                continue # have to handle the case where no errorHandler left but still kaputt
        print(f"--- Post calc validation succesfull ---")
        
        for a in self.analyzers:
            a.analyze(self, job_data)
        for c in self.childSpawners:
            c.spawn(self, job_data)

        return True

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