import os
from pathlib import Path
from state_manager import Job

class WorkflowEngine:
    def __init__(self, manager, config):
        self.manager = manager
        self.pipeline = config.get('pipelines', {})

    def transition_job(self, completed_job: Job):
        profile_name = completed_job.pipeline_profile
        roadmap = self.pipeline.get(profile_name)
        if not roadmap:
            print(f"Error: No pipeline roadmap found for profile: {profile_name}")
            return
        
        current_stage_rules = roadmap.get(completed_job.stage)
        if not current_stage_rules:
            return  # Leaf node
        
        next_steps = current_stage_rules.get('next_steps', [])
        print(f"Spawning {len(next_steps)} children for {completed_job.molecule_name}...")

        for step in next_steps:
            new_type = step['stage']
            folder_name = step['folder']

            new_working_dir = Path(completed_job.working_dir) / folder_name
            new_name = f"{completed_job.molecule_name}_{folder_name}"
            
            # Create the Job Object
            new_job = Job(
                molecule_name=new_name,
                stage=new_type,  # This maps to the template/validator logic
                parent_id=completed_job.id,
                working_dir=str(new_working_dir),
                pipeline_profile=profile_name
            )
            
            # Pass down specific config like validation_mode
            if 'validation_mode' in step:
                new_job.params['validation_mode'] = step['validation_mode']

            # Register with StateManager
            self.manager.add_job(new_job)
            print(f"  -> Created {new_name} in {folder_name}")