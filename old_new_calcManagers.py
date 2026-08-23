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
    preCalcSoftFixes: dict[str, List[PreCalcSoftFix]]

    def _try_soft_fix(self, validator_name: str, job_data: dict) -> bool:
        """Attempts to apply a soft fix for a failed pre-validator."""
        fixes = self.preCalcSoftFixes.get(validator_name)
        if not fixes:
            return False

        for heal in fixes:
            print(f"--- Attempting soft fix with {heal.__class__.__name__} ---")
            if heal.selfHeal(self, job_data):
                print(f"--- Pre calc soft fix successful ---")
                return True
        
        print(f"--- Pre calc soft fix failed ---")
        return False

    def run(self, job_data: dict) -> bool:
        validation_results = {
            test.__class__.__name__: test.preValidate(self, job_data)
            for test in self.preValidators
        }

        failures = [name for name, is_valid in validation_results.items() if not is_valid]

        if not failures:
            print(f"--- Pre calc validation successful ---")
            return True

        for validator_name in failures:
            print(f"--- Pre calc validation failed for {validator_name} ---")
            if not self._try_soft_fix(validator_name, job_data):
                return False # A failure could not be fixed

        print(f"--- All pre calc validation failures were fixed ---")
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
    errorHandlers: dict[str, List[ErrorHandler]]
    childSpawners: List[ChildSpawner]

    def _run_stage(self, strategies: List[Any], stage_name: str, method_name: str, job_data: dict) -> bool:
        """Helper to run a list of strategies for a given stage and report results."""
        if not strategies:
            return True
        
        print(f"{stage_name}...          ")
        
        all_successful = True
        for strategy in strategies:
            strategy_name = strategy.__class__.__name__
            method_to_call = getattr(strategy, method_name)
            
            success = method_to_call(self, job_data)
            status = "successful" if success else "failed"
            print(f"                        {status} for {strategy_name}")
            if not success:
                all_successful = False
                
        print(f"                        ... completed")
        return all_successful

    def _try_handle_error(self, validator_name: str, job_data: dict) -> bool:
        """Tries to find and run a handler for a specific validation failure."""
        handlers = self.errorHandlers.get(validator_name)
        if not handlers:
            print(f"                        No error handler found for {validator_name}")
            return False

        for handler in handlers:
            print(f"                                            attempting {handler.__class__.__name__} --- ", end='')
            if handler.handle(self, job_data):
                print(f"successful")
                return True  # The error was handled
            else:
                print(f"failed")
        
        return False # No handler succeeded

    def _run_validation_and_handling(self, job_data: dict) -> bool:
        """Runs validators and attempts to handle any failures."""
        print(f"Validating...       ")
        
        validation_results = {
            validator.__class__.__name__: validator.postValidate(self, job_data)
            for validator in self.postValidators
        }

        failures = []
        for name, is_valid in validation_results.items():
            status = "successful" if is_valid else "failed"
            print(f"                        {status} for {name}")
            if not is_valid:
                failures.append(name)
        print(f"                        ... completed")

        if not failures:
            print(f"--- Post calc validation successful ---")
            return True

        print(f"Trying to handle errors automatically...    ")
        for validator_name in failures:
            if not self._try_handle_error(validator_name, job_data):
                return False # Stop if any error cannot be handled

        print(f"--- Post calc validation successful after handling errors ---")
        return True

    def run(self, job_data: dict) -> bool:
        print(f"--- Running post calc ---")

        if not self._run_stage(self.parsers, "Parsing", "parse", job_data):
            return False

        if not self._run_validation_and_handling(job_data):
            return False

        if not self._run_stage(self.analyzers, "Analyzing", "analyze", job_data):
            return False

        if not self._run_stage(self.childSpawners, "Spawning children", "spawn", job_data):
            return False
            
        return True