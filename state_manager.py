import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

class Job:
    """
    Represents a single computational task (e.g., an Optimization).
    """
    def __init__(self, molecule_name: str, stage: str, parent_id: str = None, 
                 pipeline_profile: str = None,  job_data: dict = None, 
                 working_dir: str = None):
        if job_data:
            # Loading from JSON
            self.id = job_data['id']
            self.molecule_name = job_data['molecule_name']
            self.stage = job_data['stage']          # e.g., 'opt', 'freq'
            self.status = job_data['status']        # e.g., 'pending', 'running'
            self.parent_id = job_data['parent_id']  # Link to previous step
            self.pbs_id = job_data['pbs_id']        # Cluster Job ID (e.g., 55001)
            self.working_dir = job_data['working_dir']
            self.results = job_data['results']      # Dict for energy, S^2, etc.
            self.history = job_data['history']      # Log of timestamped events
            self.children_spawned = job_data.get('children_spawned', False)    # Log if child calcs have been spawned
            self.pipeline_profile = job_data.get('pipeline_profile')    # Log the pipeline configuration
            self.params = job_data.get('params', {})
        else:
            # Create a brand new job
            self.id = str(uuid.uuid4())             # Generate unique ID
            self.molecule_name = molecule_name
            self.stage = stage
            self.status = "pending"
            self.parent_id = parent_id
            self.pbs_id = None
            self.working_dir = working_dir
            self.results = {}
            self.history = []
            self.children_spawned = False
            self.pipeline_profile = pipeline_profile
            self.params = {}
            
            self.log_event(f"Job created for stage: {stage}")

    def log_event(self, message: str):
        """Helper to add timestamped notes to the job's history."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"[{timestamp}] {message}")

    def mark_submitted(self, pbs_id: str, working_dir: str):
        """Updates state when we successfully call qsub."""
        self.status = "running"
        self.pbs_id = pbs_id
        self.working_dir = working_dir
        self.log_event(f"Submitted to rigi with PBS ID: {pbs_id}")

    def mark_completed(self, parsed_results: Dict[str, Any]):
        """Updates state when the calculation finishes successfully."""
        self.status = "completed"
        self.results = parsed_results
        self.log_event("Job completed successfully.")

    def mark_failed(self, reason: str):
        """Updates state when something explodes."""
        self.status = "failed"
        self.log_event(f"Job failed. Reason: {reason}")

    def to_dict(self):
        """
        Converts the Class Object back into a simple Dictionary so 
        it can be saved to JSON.
        """
        return {
            "id": self.id,
            "molecule_name": self.molecule_name,
            "stage": self.stage,
            "status": self.status,
            "parent_id": self.parent_id,
            "pbs_id": self.pbs_id,
            "working_dir": self.working_dir,
            "results": self.results,
            "history": self.history,
            "children_spawned": self.children_spawned,
            "pipeline_profile": self.pipeline_profile,
            "params": self.params
        }

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
                
            # Convert the raw dictionaries back into Job objects
            for job_id, job_data in data.get("jobs", {}).items():
                self.jobs[job_id] = Job(
                    molecule_name=job_data['molecule_name'],
                    stage=job_data['stage'],
                    job_data=job_data # Pass raw data to constructor
                )
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