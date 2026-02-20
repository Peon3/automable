from typing import Optional
from strategies import PreValidator, PostValidator # Import interfaces for type hinting

class Job:
    """The Product class. Represents a job with injectable strategies."""
    def __init__(self):
        self.name: str = "Untitled Job"
        self.pre_validator: Optional[PreValidator] = None
        self.post_validator: Optional[PostValidator] = None

    def run(self):
        print(f"--- Running Job: {self.name} ---")
        if self.pre_validator:
            if not self.pre_validator.pre_validate():
                print("Pre-validation failed. Aborting job.")
                return
        else:
            print("No pre-validator configured.")

        print("...Job processing...")

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