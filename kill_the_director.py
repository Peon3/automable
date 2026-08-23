from typing import Dict, Any
from job import Job
import analyzers
import copy

class JobDirector:
    def __init__(self) -> None:
        pass

    def build_job(self, job: Job, parent: Job, config: Dict):
        

    def asseble_job_from_state(self, state_dict: Dict[str, Any]) -> Job:
        job = Job()
        job.deserialize(state_dict)
        
        profile_config = self.get_profile_config(job.pipeline_profile)

        job.analyzer = []
        for analyzer_key in profile_config.get('req_analyzers', []):
            analyzer_class = analyzers.ANALYZER_STRATEGY_REGISTER.get(analyzer_key)
            if analyzer_class:
                job.analyzer.append(analyzer_class())
            else:
                #error handling
                pass
        return job