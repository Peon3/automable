from typing import List, Dict, Any, Optional, Protocol, Type
from enum import Enum
import uuid
from .new_calcManagers import PreCalcManager, CalcSetuper, PostCalcManager

class RegJobStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    PARSING_NEEDED = "PARSING_NEEDED"
    HUMAN_INTERVENTION_NEEDED = "HUMAN_INTERVENTION_NEEDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Job:
    """
    Docstring for Job
    """
    def __init__(self, stage: str, preCalcManager: PreCalcManager, calcSetup: CalcSetuper, postCalcManager: PostCalcManager, **kwargs):
        job_data: Optional[dict] = kwargs.get('job_data')
        if job_data:
            # State
            self.id: str = job_data['id']
            self.molecule_name: str = job_data['molecule_name']
            self.status: str = job_data['status']
            self.parent_id: Optional[str] = job_data['parent_id']
            self.queue_id: Optional[str] = job_data['queue_id']
            self.working_dir: Optional[str] = job_data['working_dir']
            self.results: Dict[str, Any] = job_data['results']
            self.history: List[str] = job_data['history']
            self.children_spawned: bool = job_data.get('children_spawned', False)
            self.pipeline_profile: Optional[str] = job_data.get('pipeline_profile')
            self_pipeline_step: Optional[str] = job_data.get('pipeline_step')
            self.params: Dict[str, Any] = job_data.get('params', {})

            # Strategies
            self.preCalcManager = preCalcManager
            self.calcSetup = calcSetup
            self.postCalcManager = postCalcManager

        else:
            molecule_name = kwargs.get('molecule_name')
            if not molecule_name:
                raise ValueError("molecule_name is required when creating a new job.")

            self.id = str(uuid.uuid4())
            self.molecule_name = molecule_name
            self.stage = stage
            self.status = "PENDING"
            self.parent_id = kwargs.get('parent_id')
            self.queue_id = None
            self.working_dir = kwargs.get('working_dir')
            self.results = {}
            self.history = []
            self.children_spawned = False
            self.pipeline_profile = kwargs.get('pipeline_profile')
            self.pipeline_step = kwargs.get('pipeline_step')
            self.params = {}
            self.log_event(f"Job created for stage: {stage}")
    
            # Strategies
            self.preCalcManager = preCalcManager
            self.calcSetup = calcSetup
            self.postCalcManager = postCalcManager

    def serialize(self) -> dict:
        return {
            "id": self.id, 
            "molecule_name": self.molecule_name, 
            "stage": self.stage,
            "status": self.status, 
            "parent_id": self.parent_id, 
            "queue_id": self.queue_id,
            "working_dir": self.working_dir, 
            "results": self.results, 
            "history": self.history,
            "children_spawned": self.children_spawned, 
            "pipeline_profile": self.pipeline_profile,
            "pipeline_step": self.pipeline_step, 
            "params": self.params, 
        }

    def rehydrate(self, job_data: dict):
        pass

    def dehydrate(self, job_data: dict):
        pass

    def preCalc(self) -> bool:
        return self.preCalcManager.run(self.job_data)

    def calcSetup(self) -> bool:
        return self.calcSetup.run(self.job_data)

    def postCalc(self) -> bool:
        return self.postCalcManager.run(self.job_data)