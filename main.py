import time
import argparse
import yaml
import os
import shutil
from pathlib import Path

# Import our custom classes (assumed to be in separate files)
from state_manager import StateManager, Job
from cluster_interface import ClusterInterface
from job_validator import JobValidator
from workflow_engine import WorkflowEngine
from template_manager import TemplateManager

def scan_inputs(project_root: Path, manager: StateManager, config: dict):
    """
    Scans the 'inputs' directory for new .xyz files and creates initial Jobs.
    Structure: project_root/inputs/<pipeline_name>/<molecule>.xyz
    """
    inputs_dir = project_root / "inputs"
    
    # 1. Auto-create structure if missing (First Run Experience)
    if not inputs_dir.exists():
        print(f"Initializing inputs directory at {inputs_dir}")
        inputs_dir.mkdir(parents=True, exist_ok=True)
        # Create subdirectories for each pipeline to guide the user
        for pipe in config.get('pipelines', {}):
            (inputs_dir / pipe).mkdir(exist_ok=True)
        return

    # 2. Identify what we already have to avoid duplicates
    # We track (molecule_name, pipeline_profile) for root jobs (parent_id is None)
    existing_roots = {
        (j.molecule_name, j.pipeline_profile, j.params.get('functional')) 
        for j in manager.jobs.values() 
        if j.parent_id is None
    }

    # Prepare functional configurations from config
    chem = config.get('chemistry', {})
    functional_configs = []
    
    # Determine source: 'functionals' list or 'functional' (which might be list or str)
    raw_source = chem.get('functionals')
    if raw_source is None:
        raw_source = chem.get('functional', 'default')
        
    # Ensure it is a list
    if not isinstance(raw_source, list):
        raw_source = [raw_source]

    for f in raw_source:
        if isinstance(f, str):
            functional_configs.append({'functional': f})
        elif isinstance(f, dict):
            functional_configs.append(f)

    # 3. Iterate over pipelines defined in config
    for profile_name, roadmap in config.get('pipelines', {}).items():
        profile_dir = inputs_dir / profile_name
        if not profile_dir.exists():
            continue
            
        for xyz_file in profile_dir.glob("*.xyz"):
            mol_name = xyz_file.stem
            
            # Iterate over all requested functionals
            for f_conf in functional_configs:
                f_name = f_conf.get('functional', 'default')
                
                # Skip if we already tracked this input for this functional
                if (mol_name, profile_name, f_name) in existing_roots:
                    continue

                print(f"  -> Found new input: {mol_name} for pipeline '{profile_name}' ({f_name})")
                
                # Determine start stage (default to 'optimization' or first key in roadmap)
                if not roadmap:
                    print(f"Warning: Pipeline {profile_name} is empty.")
                    continue
                
                start_stage = "optimization" if "optimization" in roadmap else list(roadmap.keys())[0]
                
                # Build Params: Global Defaults -> Functional Config -> Stage Overrides
                job_params = {k:v for k,v in chem.items() if k not in ['functionals', 'functional']}
                job_params.update(f_conf)
                
                # Check for pipeline-level overrides for the start stage
                stage_rules = roadmap.get(start_stage, {})
                overrides = {k:v for k,v in stage_rules.items() if k != 'next_steps'}
                job_params.update(overrides)

                # Setup working directory: work/<profile>/<mol>/<functional>/<stage>
                # We add a functional folder to avoid collisions
                safe_f = str(f_name).replace(" ", "_").replace("(", "").replace(")", "")
                work_dir = project_root / "work" / profile_name / mol_name / safe_f / start_stage
                work_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy input file to standard name 'inp.xyz' expected by the submitter
                shutil.copy(xyz_file, work_dir / "inp.xyz")
                
                # Create and register the Root Job
                new_job = Job(
                    molecule_name=mol_name,
                    stage=start_stage,
                    parent_id=None, # Root job has no parent
                    working_dir=str(work_dir),
                    pipeline_profile=profile_name
                )
                new_job.params = job_params
                manager.add_job(new_job)

def main():
    # --- 1. Setup & Configuration ---
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True)
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    
    # Load Config
    with open(project_root / "config.yaml") as f:
        config = yaml.safe_load(f)

    remote_host = config.get('resources').get('remote_host', 'rigi')
    username = config.get('resources').get('username', '')

    # Initialize Modules
    manager = StateManager(project_root / "state.json")
    cluster = ClusterInterface(remote_host, username)
    validator = JobValidator(config, manager)
    workflow = WorkflowEngine(manager, config)
    templater = TemplateManager(Path(__file__).resolve().parent / "templates")

    # Mapping abstract stages to concrete template files
    template_map = {
        "optimization": "orca_opt.inp.j2",
        "frequency": "orca_freq.inp.j2", # Assuming these exist or will exist
    }

    print(f"--- Daemon Cycle for {project_root.name} ---")

    # --- 1.5 Ingest New Inputs ---
    scan_inputs(project_root, manager, config)

    # --- 2. Monitor (Check Running Jobs) ---
    active_cluster_ids = cluster.get_active_job_ids()
    running_jobs = manager.get_jobs_by_status("running")
    
    for job in running_jobs:
        # If job has an ID but is not in qstat, it finished (or crashed)
        if job.pbs_id and job.pbs_id not in active_cluster_ids:
            print(f"Job {job.molecule_name} finished on cluster.")
            job.status = "needs_parsing"
    
    # --- 3. Parse & Validate ---
    jobs_to_parse = manager.get_jobs_by_status("needs_parsing")
    
    for job in jobs_to_parse:
        print(f"Validating {job.molecule_name}, {job.params.get('functional')}...")
        success = validator.validate(job) # Returns True/False, updates job.results
        
        if success:
            job.status = "completed" 
            # Note: We don't save immediately, we batch save at the end
        else:
            # Validator already marked it as 'failed' inside the object
            print(f"Job {job.molecule_name} FAILED validation.")

    # --- 4. Transition (Spawn Children) ---
    # We only look for 'completed' jobs that haven't spawned children yet.
    
    completed_jobs = manager.get_jobs_by_status("completed")
    for job in completed_jobs:
        if not job.children_spawned:
            workflow.transition_job(job)
            job.children_spawned = True # Mark so we don't spawn duplicates next cycle

    # --- 5. Submit (The Actuator) ---
    pending_jobs = manager.get_jobs_by_status("pending")
    
    # Cache cluster status if we have work to do
    cluster_status = {}
    if pending_jobs:
        cluster_status = cluster.get_free_slots()
    
    for job in pending_jobs:
        print(f"Preparing {job.molecule_name}...")
        
        # A. Create Directory
        job_dir = Path(job.working_dir)
        job_dir.mkdir(parents=True, exist_ok=True) # exist_ok=True because Rescue jobs already created this dir
        
        # B. Generate Input (Jinja2)
        # Fetch parent for coordinates/orbitals if needed
        parent_job = manager.get_job_by_id(job.parent_id) if job.parent_id else None
        
        # Determine XYZ source: Prefer local 'input.xyz' (Rescue jobs), else Parent
        if (job_dir / "inp.xyz").exists():
            xyz_source = "inp.xyz"
        elif parent_job:
            os.system(f"cp {Path(parent_job.working_dir)}/{parent_job.molecule_name}.xyz {job_dir}/inp.xyz")
            xyz_source = "inp.xyz"
        else:
            xyz_source = "inp.xyz" # Fallback for root

        # Context building
        chem = config['chemistry']

        # Helper to resolve param: Job Param > Global Config > Default
        def resolve(key, default=None):
            if key in job.params:
                return job.params[key]
            return chem.get(key, default)

        # --- Resource Selection Logic ---
        # 1. Gather candidates (List of Dicts)
        # Check job.params['resources'] first, then config['resources']
        res_input = job.params.get('resources')
        if not res_input:
            res_input = config.get('resources', {})
            
        # Normalize to list
        if isinstance(res_input, dict):
            res_candidates = [res_input]
        elif isinstance(res_input, list):
            res_candidates = res_input
        else:
            res_candidates = [{'n_cores': 32, 'mem_per_core': 13000}] # Fallback

        # 2. Select best candidate
        selected_res = res_candidates[0] # Default to first
        
        if len(res_candidates) > 1:
            for cand in res_candidates:
                label = cand.get('node_label')
                if label and cluster_status.get(label, 0) > 0:
                    selected_res = cand
                    print(f"  -> Routing to {label} (Free: {cluster_status[label]})")
                    break

        context = {
            "molecule_name": job.molecule_name,
            "xyz_coord_fname": xyz_source,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "charge": resolve('charge', 0),
            "multiplicity": resolve('multiplicity', 1),
            "functional": resolve('functional', 'r2scan-3c'),
            "basis_set": resolve('basis_set', ''),
            "dispersion": resolve('dispersion', ''),
            "aux_basis": resolve('aux_basis', 'AutoAux'),
            "solvent_model": resolve('solvation', ''),
            "n_cores": selected_res.get('n_cores', 14),
            "mem_per_core": selected_res.get('mem_per_core', '13000')
        }
        
        # Render
        inp_name = f"{job.molecule_name}.inp"
        template_name = template_map.get(job.stage, f"{job.stage}.inp.j2")
        templater.render_and_write(template_name, job_dir / inp_name, context)
        
        # C. Submit
        # We submit a standardized script that calls the input
        pbs_id = cluster.submit_job(str(job_dir), 'suborca.py', inp_name)
        
        if pbs_id:
            job.mark_submitted(pbs_id, str(job_dir))
        else:
            print("Submission failed.")

    # --- 6. Save State ---
    manager.save()
    print("Cycle complete.")

if __name__ == "__main__":
    main()