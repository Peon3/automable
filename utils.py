from pathlib import Path
import shutil
from typing import Dict, Any, List, Optional

# Forward reference for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from state_manager import StateManager
    from jobs import Job

def select_best_resource(job: 'Job', config: dict, cluster_status: dict) -> Dict[str, Any]:
    """
    Selects the best resource candidate based on job/config specs and cluster availability.
    """
    res_input = job.params.get('resources', config.get('resources', {}))

    if isinstance(res_input, dict):
        res_candidates = [res_input]
    elif isinstance(res_input, list):
        res_candidates = res_input
    else:
        res_candidates = [{'n_cores': 32, 'mem_per_core': 13000}] # Fallback

    # Default to the first candidate
    selected_res = res_candidates[0]

    # If there are multiple options, check for free slots
    if len(res_candidates) > 1:
        for cand in res_candidates:
            if (label := cand.get('node_label')) and cluster_status.get(label, 0) > 0:
                selected_res = cand
                print(f"  -> Routing to {label} (Free: {cluster_status.get(label)})")
                break
    
    return selected_res

def find_and_copy_product_xyz(job: 'Job', manager: 'StateManager', project_root: Path) -> Optional[str]:
    """
    For NEB jobs, finds the optimized structure of the product and copies it.
    Returns 'product.xyz', None if not found, or 'WAIT' if the source is not ready.
    """
    job_dir = Path(job.working_dir)
    product_mol_name = job.params.get('product_name')
    found_product = False
    
    if product_mol_name:
        candidates = [j for j in manager.jobs.values() if j.molecule_name == product_mol_name and j.status == "completed"]
        if candidates:
            freq_candidates = [c for c in candidates if "freq" in c.stage.lower()]
            pool = freq_candidates or candidates
            
            current_func = job.params.get('functional')
            func_matches = [c for c in pool if c.params.get('functional') == current_func]
            
            best_job = (func_matches or pool)[-1]
            
            src_path = Path(best_job.results['final_xyz']) if best_job.results.get('final_xyz') else Path(best_job.working_dir) / "inp.xyz"

            if src_path.exists():
                shutil.copy(src_path, job_dir / "product.xyz")
                print(f"  -> Found product structure from job {best_job.molecule_name} ({best_job.id[:8]})")
                found_product = True

    if not found_product and (prod_path_str := job.params.get('product_xyz')):
        prod_path = (project_root / prod_path_str).resolve()
        if prod_path.exists():
            shutil.copy(prod_path, job_dir / "product.xyz")
            found_product = True
        else:
            print(f"Warning: Product XYZ not found at static path {prod_path}")

    if product_mol_name and not found_product:
        return "WAIT"

    return "product.xyz" if found_product else None

def find_and_copy_parent_hessian(job: 'Job', manager: 'StateManager') -> Optional[str]:
    """For IRC/OptTS jobs, finds the parent's hessian and copies it."""
    if not job.parent_id or not (parent_job := manager.get_job_by_id(job.parent_id)):
        return None

    parent_hess = Path(parent_job.working_dir) / f"{parent_job.molecule_name}.hess"
    if parent_hess.exists():
        shutil.copy(parent_hess, Path(job.working_dir) / "parent.hess")
        return "parent.hess"
    
    print(f"Warning: Parent Hessian not found at {parent_hess}")
    return None