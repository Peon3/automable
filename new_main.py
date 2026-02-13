import json
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    PARSING_NEEDED = "PARSING_NEEDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class StateManager:
    """
    read/writes state.json, holds functions like 'get_jobs_by_status', 'add_new_job', etc.
    """
    pass

class QueueInterface:
    """
    interfaces to cluster, in our case rigi und liverpool, holds functions like 'check_job_status', 'submit_job', etc.
    """
    pass

class JobFactory:
    """
    Docstring for JobFactory
    """
    pass

class Job:
    """
    Docstring for Job
    """