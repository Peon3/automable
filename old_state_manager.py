import json
import time
import uuid
from pathlib import Path
from typing import Dict

# Import the factory and the base class for type hinting
from jobs import job_factory, Job

class StateManager:
    """
    Manages the database of jobs (daemon_state.json).
    """
    def __init__(self, db_path: str = "daemon_state.json"):
        self.db_path = Path(db_path)
        self.jobs: Dict[str, Job] = {} # A dictionary to hold loaded Job objects
        self.load() # Load immediately upon startup

    def load(self):
        """Reads the JSON file and converts entries into Job objects."""
        if not self.db_path.exists():
            print("No state file found. Starting fresh.")
            return

        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                
            # Convert the raw dictionaries back into the correct Job objects using the factory
            for job_id, job_data in data.get("jobs", {}).items():
                self.jobs[job_id] = job_factory(stage=job_data['stage'], job_data=job_data)
        except json.JSONDecodeError:
            print("Error: State file is corrupted. Please check daemon_state.json")

    def save(self):
        """Converts all Job objects to dicts and writes to JSON."""
        data_to_save = {
            "jobs": {j_id: job.to_dict() for j_id, job in self.jobs.items()},
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Write to a temporary file first, then rename (atomic write)
        # This prevents corruption if the script crashes while writing.
        temp_path = self.db_path.with_suffix(".tmp")
        with open(temp_path, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        temp_path.replace(self.db_path)

    def add_job(self, job: Job):
        """Registers a new job in the manager."""
        if job.id in self.jobs:
            print(f"Warning: Job {job.id} already exists.")
            return
        self.jobs[job.id] = job
        self.save() # Save immediately so we don't lose it

    def get_jobs_by_status(self, status: str):
        """Helper to find all jobs that are 'running', 'pending', etc."""
        return [job for job in self.jobs.values() if job.status == status]

    def get_job_by_id(self, job_id: str):
        """Finds a job based on the internal UUID."""
        return self.jobs.get(job_id)

    def get_job_by_pbs_id(self, pbs_id: str):
        """Finds a job based on the cluster ID (useful for monitoring)."""
        for job in self.jobs.values():
            if str(job.pbs_id) == str(pbs_id):
                return job
        return None