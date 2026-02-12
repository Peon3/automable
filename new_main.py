from typing import List, Dict, Any 

class InputBuilder:
    def build_context(self, job_options) -> Dict[str, Any]: pass
    def get_template_name(self) -> str: pass

class PreCalc:
    def setup(self, job_data, parent) -> bool: pass
    def check(self, job_data, parent) -> bool: pass

class PostCalc:
    def validation(self, job_data) -> bool: pass
    def analysis(self, job_data) -> Dict[str, Any]: pass
    def error_handling(self, job_data) -> bool: pass
    def child_spawning(self, job_data) -> List['Job']: pass

class Job:
    def __init__(self,
                 name:str,
                 input_builder: InputBuilder,
                 pre_hooks: List[PreCalc] = None,
                 post_hooks: List[PostCalc] = None):
        self.input_builder = input_builder
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    def prepare(self):
        for hook in self.pre_hooks:
            if (not hook.setup(self.data, self.parent) or 
                not hook.check(self.data, self.parent)):
                raise RuntimeError(f"Setup or Check {hook} failed.")
        
        context = self.input_builder.build_context(self.options)
        template = self.input_builder.get_template_name()

    def finish(self):
        new_jobs = []
        for hook in self.post_hooks:
            spawned = hook.child_spawning(self.results)