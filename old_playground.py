from abc import ABC, abstractmethod
from typing import Optional

# 1. Strategy Interfaces (inspired by new_interfaces.py)
# These define the "contract" for any strategy we might want to inject.

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
# These are the different behaviors we can choose from. They are simple here,
# but could contain complex logic in a real application.

class SimplePreValidator(PreValidator):
    def pre_validate(self) -> bool:
        print("Executing Simple Pre-Validation...")
        return True

class ComplexPreValidator(PreValidator):
    def pre_validate(self) -> bool:
        print("Executing Complex Pre-Validation (e.g., checking more inputs)...")
        return True

class SimplePostValidator(PostValidator):
    def post_validate(self) -> bool:
        print("Executing Simple Post-Validation...")
        return True

class StrictPostValidator(PostValidator):
    def post_validate(self) -> bool:
        print("Executing Strict Post-Validation (e.g., checking for convergence)...")
        return True

# 3. The Product Class (The object we are building)

class Job:
    """Represents a computational job with injectable strategies."""
    def __init__(self):
        self.name: str = "Untitled Job"
        # These will hold the injected strategy objects.
        self.pre_validator: Optional[PreValidator] = None
        self.post_validator: Optional[PostValidator] = None

    def run(self):
        print(f"--- Running Job: {self.name} ---")
        
        # Use the injected pre-validator strategy, if it exists.
        if self.pre_validator:
            if not self.pre_validator.pre_validate():
                print("Pre-validation failed. Aborting job.")
                return
        else:
            print("No pre-validator configured.")

        print("...Job processing...")

        # Use the injected post-validator strategy, if it exists.
        if self.post_validator:
            if self.post_validator.post_validate():
                print("Post-validation successful.")
            else:
                print("Post-validation failed.")
        else:
            print("No post-validator configured.")
        
        print(f"--- Job '{self.name}' Finished ---\n")

    def __str__(self):
        pre_validator_name = self.pre_validator.__class__.__name__ if self.pre_validator else "None"
        post_validator_name = self.post_validator.__class__.__name__ if self.post_validator else "None"
        return (f"Job '{self.name}' with strategies: "
                f"PreValidator={pre_validator_name}, "
                f"PostValidator={post_validator_name}")

# 4. The Builder Pattern Implementation

class JobBuilder:
    """Builds a Job object with a step-by-step interface."""
    def __init__(self):
        self._job = Job()

    def with_name(self, name: str) -> 'JobBuilder':
        self._job.name = name
        return self

    def with_pre_validator(self, validator: PreValidator) -> 'JobBuilder':
        self._job.pre_validator = validator
        return self

    def with_post_validator(self, validator: PostValidator) -> 'JobBuilder':
        self._job.post_validator = validator
        return self

    def build(self) -> Job:
        """Returns the final, configured Job object."""
        return self._job

# 5. The Register Mapping and Client/Director Code

# This mapping connects a user-defined "job type" to concrete strategy classes.
STRATEGY_REGISTER = {
    "simple_job": {
        "pre_validator": SimplePreValidator,
        "post_validator": SimplePostValidator,
    },
    "complex_job": {
        "pre_validator": ComplexPreValidator,
        "post_validator": StrictPostValidator,
    }
}

def main():
    """
    This is our test ground to demonstrate the Builder pattern.
    """
    print("### Demonstrating the Builder Pattern for Job creation ###\n")

    # --- This variable models the user input that determines which strategies to use. ---
    # --- Try changing it to "complex_job" to see the difference! ---
    user_job_type = "complex_job" 
    
    print(f"--> User requested job type: '{user_job_type}'")

    # 1. Look up the required strategies from our register
    job_config = STRATEGY_REGISTER.get(user_job_type)
    if not job_config:
        raise ValueError(f"Job type '{user_job_type}' not found in the register.")

    # 2. Instantiate the builder and use the register to configure it
    builder = JobBuilder()
    builder.with_name(f"My {user_job_type}")
    builder.with_pre_validator(job_config["pre_validator"]())
    builder.with_post_validator(job_config["post_validator"]())

    # 3. Build the final Job object
    my_job = builder.build()
    print(f"--> Successfully built job: {my_job}\n")
    
    # 4. Run the job to see the injected strategies in action
    my_job.run()

if __name__ == "__main__":
    main()
