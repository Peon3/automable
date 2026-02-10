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
        print(f"Spawning {len(next_steps)} children for {completed_job.molecule_name}, {completed_job.params.get('functional')}...")

        for step in next_steps:
            # --- Logic A: NEB Pairs (One-to-Many based on Config) ---
            if 'neb_pairs' in step:
                pairs = step['neb_pairs']
                # Filter pairs relevant to this specific reactant
                matches = [p for p in pairs if p['reactant'] == completed_job.molecule_name]
                
                for match in matches:
                    product_name = match['product']
                    # Create unique folder and name to avoid collisions
                    # e.g. folder: "02_NEB_ProductB", name: "Reactant_to_ProductB"
                    suffix = f"_to_{product_name}"
                    new_folder = f"{step['folder']}{suffix}"
                    new_mol_name = f"{completed_job.molecule_name}{suffix}"
                    
                    self._spawn_child(
                        completed_job, step, new_folder, new_mol_name, 
                        extra_params={'product_name': product_name}
                    )
                continue # Skip standard creation for this step

            # --- Logic B: IRC Split (One-to-Two based on Results) ---
            # If parent was IRC and next is Optimization, we spawn Forward and Reverse
            if completed_job.stage == 'irc' and ('Opt' in step['stage']):
                fwd_path = completed_job.results.get('forward_xyz')
                rev_path = completed_job.results.get('reverse_xyz')
                
                if fwd_path and rev_path:
                    # Spawn Forward
                    self._spawn_child(
                        completed_job, step, f"{step['folder']}_Fwd", 
                        f"{completed_job.molecule_name}_Fwd",
                        extra_params={'initial_xyz': fwd_path}
                    )
                    # Spawn Reverse
                    self._spawn_child(
                        completed_job, step, f"{step['folder']}_Rev", 
                        f"{completed_job.molecule_name}_Rev",
                        extra_params={'initial_xyz': rev_path}
                    )
                    continue

            # --- Logic C: Standard One-to-One ---
            self._spawn_child(completed_job, step, step['folder'], completed_job.molecule_name)

    def _spawn_child(self, parent_job, step_config, folder_name, new_mol_name, extra_params=None):
        """Helper to create and register a child job."""
        profile_name = parent_job.pipeline_profile
        roadmap = self.pipeline.get(profile_name)
        new_type = step_config['stage']
        
        new_working_dir = Path(parent_job.working_dir) / folder_name
        
        new_job = Job(
            molecule_name=new_mol_name,
            stage=new_type,
            parent_id=parent_job.id,
            working_dir=str(new_working_dir),
            pipeline_profile=profile_name
        )
        
        # 1. Inherit
        new_job.params = parent_job.params.copy()
        
        # 2. Roadmap Overrides
        target_stage_rules = roadmap.get(new_type, {})
        stage_overrides = {k: v for k, v in target_stage_rules.items() if k != 'next_steps'}
        new_job.params.update(stage_overrides)
        
        # 3. Step Config Overrides
        overrides = {k: v for k, v in step_config.items() if k not in ['stage', 'folder', 'neb_pairs']}
        new_job.params.update(overrides)
        
        # 4. Dynamic Extras (from logic above)
        if extra_params:
            new_job.params.update(extra_params)

        self.manager.add_job(new_job)
        print(f"  -> Created {new_mol_name} in {folder_name}")