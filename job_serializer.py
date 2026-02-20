import json
import os
import time
from typing import List, Dict, Any
from job import Job

class JobSerializer:
    def __init__(self, state_file: str = 'state.json'):
        self.state_file = state_file

    def serialize(self, job: Job) -> Dict[str, Any]:
        """ Converts job instance to dict, excluding strategies """

        data = job.__dict__.copy()

        if 'stratgies' in data:
            del data['strategies']

        return data

    def deserialize(self, data: Dict[str, Any]) -> Job:
        """ Converts dict to job instance, excluding strategies """
        job = Job()

        for key, value in data.items():
            if hasattr(job, key):
                setattr(job, key, value)
        return job
    
    def save_state(self, jobs: List[Job]) -> None:
        """ Updates state.json from a list of Jobs """
        current_state = {}

        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                try:
                    current_state = json.load(f)
                except json.JSONDecodeError:
                    current_state= {}

        
        for job in jobs:
            current_state[job.id] = self.serialize(job)

        data_to_save = {
            'jobs': current_state,
            'laste_updated' : time.strftime("%Y-%m-%d %H:%M:%S")
        }

        temp_file = self.state_file + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        temp_file.replace(self.state_file)

    def load_state(self) -> List[Job]:
        if not os.path.exists(self.state_file):
            return []
        
        with open(self.state_file, 'r') as f:
            data = json.load(f)
        
        return [self.deserialize(job_data) for job_data in data['jobs'].values()]