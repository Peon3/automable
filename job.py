from typing import Optional, Dict, List, Any
from interfaces import *
import uuid

class Job:
    def __init__(self):
        # State
        self.id: str = str(uuid.uuid4())
        self.molecule_name: str = 'untitled'
        self.status: str = 'pending'
        self.parent_id: Optional[str] = None
        self.children_ids: List[str] = []
        self.queue_id: str = ''
        self.working_dir: str = ''
        self.children_spawned: bool = False

        # pipeline info
        self.pipeline_profile: str = ''
        self_pipeline_step: str = ''
        self.job_type: str = ''

        # structurized params
        # chemistry holds charge, mult, lvl of theory etc.
        self.chemistry: Dict[str, Any] = {}
        # execution holds ressource info like cores, mem etc.
        self.execution: Dict[str, Any] = {}
        # task_config holds type specific properties like n_images for neb, nroots for tddft, temp for freq etc.
        self.task_config: Dict[str, Any] = {}

        # data
        self.results: Dict[str, Any] = {}
        self.history: List[str] = []

        # strategies
        self.strategies: Dict[str, Any] = {
            'pre_validators': [],
            #'pre_calc_soft_fixes': None,                   # TODO: implement at some point, for now we go without
            'context_builder': None,
            'input_builder': None,
            'parsers': [],
            'post_validators': [],
            'analyzer': [],
            #'error_handlers': None,                        # TODO: implement at some point, for now we go without
            'child_spawner': None
        }

    def pre_job_validation(self) -> bool:
        if not self.strategies['pre_validators']:
            return True
        for validator in self.strategies['pre_validators']:
            if not validator.preValidate(self):
                return False
        return True
    
    def _build_context(self) -> Dict[str, Any]:
        if not self.strategies['context_builder']:
            return {}
        return self.strategies['context_builder'].build_context(self)

    def build_input(self) -> bool:
        if not self.strategies['input_builder']:
            return False
        return self.strategies['input_builder'].build_input(self, self._build_context()) 
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        if not self.strategies['parsers']:
            return {}
        parsed_out = {}
        for parser in self.strategies['parsers']:
            parsed_out[parser.__class__.__name__] = parser.parse(filepath)
        return parsed_out
    
    def post_job_validation(self) -> bool:
        if not self.strategies['post_validators']:
            return True
        for validator in self.strategies['post_validators']:
            if not validator.postValidate(self):
                return False
        return True
    
    def analyze(self) -> Dict[str, Any]:
        if not self.strategies['analyzer']:
            return {}
        results = {}
        for analyzer in self.strategies['analyzer']:
            results[analyzer.__class__.__name__] = analyzer.analyze(self)
        return results
    
    def spawn_children(self) -> bool:
        if not self.strategies['child_spawner']:
            return True
        return self.strategies['child_spawner'].spawn(self)