#!/usr/bin/python3.10
import time
import argparse
import yaml
import os
from pathlib import Path

# Import our custom classes (assumed to be in separate files)
from state_manager import StateManager
from cluster_interface import ClusterInterface
from job_validator import JobValidator
from workflow_engine import WorkflowEngine
from template_manager import TemplateManager

def main():
    # --- 1. Setup & Configuration ---
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True)
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    
    # Load Config
    with open(project_root / "config.yaml") as f:
        config = yaml.safe_load(f)

    # Initialize Modules
    manager = StateManager(project_root / "daemon_state.json")
    cluster = ClusterInterface(remote_host="rigi", username="lege")
    validator = JobValidator(config, manager)
    workflow = WorkflowEngine(manager, config)
    templater = TemplateManager(project_root / "templates")

    # Mapping abstract stages to concrete template files
    template_map = {
        "optimization": "orca_opt.inp.j2",
        "frequency": "orca_freq.inp.j2", # Assuming these exist or will exist
    }

    print(f"--- Daemon Cycle for {project_root.name} ---")

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
        print(f"Validating {job.molecule_name}...")
        success = validator.validate(job) # Returns True/False, updates job.results
        
        if success:
            job.status = "completed" 
            # Note: We don't save immediately, we batch save at the end
        else:
            # Validator already marked it as 'failed' inside the object
            print(f"Job {job.molecule_name} FAILED validation.")

    # --- 4. Transition (Spawn Children) ---
    # We only look at jobs that JUST turned 'completed' in this cycle?
    # Actually, simpler logic: Look for 'completed' jobs that haven't spawned children yet.
    # (You might need a flag in Job like 'children_spawned=False')
    
    completed_jobs = manager.get_jobs_by_status("completed")
    for job in completed_jobs:
        if not job.children_spawned:
            workflow.transition_job(job)
            job.children_spawned = True # Mark so we don't spawn duplicates next cycle

    # --- 5. Submit (The Actuator) ---
    pending_jobs = manager.get_jobs_by_status("pending")
    
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
            os.system(f"cp {parent_job.molecule_name}.xyz {job_dir}/inp.xyz")
            xyz_source = "inp.xyz"
        else:
            xyz_source = "inp.xyz" # Fallback for root

        # Context building
        chem = config['chemistry']
        res = config.get('resources', {})

        context = {
            "molecule_name": job.molecule_name,
            "xyz_coord_fname": xyz_source,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "charge": chem.get('charge', 0),
            "multiplicity": chem.get('multiplicity', 1),
            "functional": chem.get('functional', 'r2scan-3c'),
            "basis_set": chem.get('basis_set', ''),
            "dispersion": chem.get('dispersion', ''),
            "aux_basis": chem.get('aux_basis', 'AutoAux'),
            "solvent_model": chem.get('solvation', ''),
            "n_cores": res.get('n_cores', 14),
            "mem_per_core": res.get('mem_per_core', '13000')
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