# Import the concrete strategies that the register needs to know about.
from strategies import (
    SimplePreValidator,
    ComplexPreValidator,
    SimplePostValidator,
    StrictPostValidator,
)

# This is a module-level dictionary that acts as our configuration register.
# It can be imported directly into any other file. No need for a wrapper class.
STRATEGY_REGISTER = {
    "simple_job": {
        "pre_validator": SimplePreValidator,
        "post_validator": SimplePostValidator,
    },
    "complex_job": {
        "pre_validator": ComplexPreValidator,
        "post_validator": StrictPostValidator,
    },
    "validation_only_job": {
        "pre_validator": ComplexPreValidator,
        "post_validator": None, # Example of a job with only one strategy
    }
}