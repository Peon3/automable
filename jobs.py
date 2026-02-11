import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

import parsers
import utils

# Use a forward reference for the StateManager type hint to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from state_manager import StateManager


def _spawn_child_job(parent_job: 'Job', step_config: dict, folder_name: str, new_mol_name: str,
                     manager: 'StateManager', pipelines: dict, extra_params: Optional[dict] = None):
    """Helper to create and register a child job."""
    profile_name = parent_job.pipeline_profile
    roadmap = pipelines.get(profile_name, {})
    new_stage = step_config['stage']

    # Use the factory to create an instance of the correct Job subclass for the new stage.
    new_job = job_factory(
        stage=new_stage,
        molecule_name=new_mol_name,
        parent_id=parent_job.id,
        pipeline_profile=profile_name
    )

    # The working directory for a child is relative to the parent's parent directory
    # e.g., work/pipeline/mol/stage_1 -> work/pipeline/mol/stage_2
    new_working_dir = Path(parent_job.working_dir).parent / folder_name
    new_job.working_dir = str(new_working_dir)

    # --- Parameter Inheritance Logic (from old WorkflowEngine) ---
    # 1. Inherit all parameters from parent
    new_job.params = parent_job.params.copy()
    # 2. Apply overrides defined for the new stage in the pipeline roadmap
    target_stage_rules = roadmap.get(new_stage, {})
    stage_overrides = {k: v for k, v in target_stage_rules.items() if k != 'next_steps'}
    new_job.params.update(stage_overrides)
    # 3. Apply overrides from the specific 'next_steps' entry in the parent's config
    step_overrides = {k: v for k, v in step_config.items() if k not in ['stage', 'folder', 'neb_pairs']}
    new_job.params.update(step_overrides)
    # 4. Apply any dynamic parameters passed during creation (e.g., from IRC logic)
    if extra_params:
        new_job.params.update(extra_params)

    manager.add_job(new_job)
    print(f"  -> Created {new_job.stage} job '{new_mol_name}' in {folder_name}")


class Job:
    """
    Represents a single computational task. This is the base class for all specific job types.
    """
    def __init__(self, stage: str, **kwargs):
        job_data: Optional[dict] = kwargs.get('job_data')
        if job_data:
            self.id: str = job_data['id']
            self.molecule_name: str = job_data['molecule_name']
            self.stage: str = job_data['stage']
            self.status: str = job_data['status']
            self.parent_id: Optional[str] = job_data['parent_id']
            self.pbs_id: Optional[str] = job_data['pbs_id']
            self.working_dir: Optional[str] = job_data['working_dir']
            self.results: Dict[str, Any] = job_data['results']
            self.history: List[str] = job_data['history']
            self.children_spawned: bool = job_data.get('children_spawned', False)
            self.pipeline_profile: Optional[str] = job_data.get('pipeline_profile')
            self.params: Dict[str, Any] = job_data.get('params', {})
        else:
            molecule_name = kwargs.get('molecule_name')
            if not molecule_name:
                raise ValueError("molecule_name is required when creating a new job.")

            self.id = str(uuid.uuid4())
            self.molecule_name = molecule_name
            self.stage = stage
            self.status = "pending"
            self.parent_id = kwargs.get('parent_id')
            self.pbs_id = None
            self.working_dir = kwargs.get('working_dir')
            self.results = {}
            self.history = []
            self.children_spawned = False
            self.pipeline_profile = kwargs.get('pipeline_profile')
            self.params = {}
            self.log_event(f"Job created for stage: {stage}")

    def log_event(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"[{timestamp}] {message}")

    def mark_submitted(self, pbs_id: str, working_dir: str):
        self.status = "running"
        self.pbs_id = pbs_id
        self.working_dir = working_dir
        self.log_event(f"Submitted to cluster with PBS ID: {pbs_id}")

    def mark_completed(self, parsed_results: Dict[str, Any]):
        self.status = "completed"
        self.results.update(parsed_results)
        self.log_event("Job completed successfully.")

    def mark_failed(self, reason: str):
        self.status = "failed"
        self.log_event(f"Job failed. Reason: {reason}")

    def to_dict(self) -> dict:
        return {
            "id": self.id, "molecule_name": self.molecule_name, "stage": self.stage,
            "status": self.status, "parent_id": self.parent_id, "pbs_id": self.pbs_id,
            "working_dir": self.working_dir, "results": self.results, "history": self.history,
            "children_spawned": self.children_spawned, "pipeline_profile": self.pipeline_profile,
            "params": self.params
        }

    def validate(self, manager: 'StateManager') -> bool:
        """Default validation: check if the output file exists."""
        outfile = Path(self.working_dir) / f"{self.molecule_name}.out"
        if not outfile.exists():
            self.mark_failed("Output file not found")
            return False
        # For generic jobs, existence of output implies success.
        return True

    def spawn_children(self, manager: 'StateManager', pipelines: dict):
        """Default child spawning logic. Handles one-to-one and NEB-pair transitions."""
        profile_name = self.pipeline_profile
        roadmap = pipelines.get(profile_name)
        if not roadmap or not (current_stage_rules := roadmap.get(self.stage)):
            return

        for step in current_stage_rules.get('next_steps', []):
            if 'neb_pairs' in step:
                for match in (p for p in step['neb_pairs'] if p['reactant'] == self.molecule_name):
                    product_name = match['product']
                    suffix = f"_to_{product_name}"
                    _spawn_child_job(
                        self, step, f"{step['folder']}{suffix}", f"{self.molecule_name}{suffix}",
                        manager, pipelines, extra_params={'product_name': product_name}
                    )
            else:
                _spawn_child_job(self, step, step['folder'], self.molecule_name, manager, pipelines)

    def get_submission_context(self, manager: 'StateManager', config: dict, project_root: Path) -> Dict[str, Any]:
        """Prepares the Jinja2 context dictionary for rendering the input file."""
        def resolve(key, default=None):
            return self.params.get(key, config.get('chemistry', {}).get(key, default))

        return {
            "molecule_name": self.molecule_name, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "charge": resolve('charge', 0), "multiplicity": resolve('multiplicity', 1),
            "functional": resolve('functional', 'r2scan-3c'), "basis_set": resolve('basis_set', ''),
            "dispersion": resolve('dispersion', ''), "aux_basis": resolve('aux_basis', 'AutoAux'),
            "solvent_model": resolve('solvation', ''), "nroots": resolve('nroots', 30),
            "triplets": resolve('triplets', 'false'), "tda": resolve('tda', 'true'),
            "dosoc": resolve('dosoc', 'false'), "iroot": resolve('iroot', 1),
        }


class OptimizationJob(Job):
    def validate(self, manager: 'StateManager') -> bool:
        outfile = Path(self.working_dir) / f"{self.molecule_name}.out"
        if not super().validate(manager): return False

        if not parsers.parse_orca_scf_conv(outfile):
            self.mark_failed("SCF did not converge")
            return False

        if parsers.check_imaginary_frequencies(outfile):
            print(f"    -> Alert: Imaginary frequency detected in Optimization {self.molecule_name}")
            if new_xyz := self._generate_displaced_structure():
                self._spawn_rescue_job(manager, new_xyz)
                self.status = "rescued"
                self.log_event("Converged to saddle point, attempting rescue.")
            else:
                self.mark_failed("Saddle point detected, but rescue generation failed.")
            return False

        if not parsers.parse_orca_geom_conv(outfile):
            self.mark_failed("Geometry did not converge")
            return False

        self.mark_completed({
            "energy": parsers.parse_orca_energy(outfile),
            "final_xyz": str(outfile.with_suffix(".xyz"))
        })
        return True

    def _generate_displaced_structure(self) -> Optional[str]:
        wd = Path(self.working_dir)
        hess_file = wd / f"{self.molecule_name}.hess"
        if not hess_file.exists():
            print(" -> No .hess file found for rescue.")
            return None
        try:
            os.system(f"orca_pltvib {hess_file} 6")
            generated_file = wd / f"{self.molecule_name}.hess.v006.xyz"
            if not generated_file.exists(): return None
            with open(generated_file, 'r') as f: lines = f.readlines()
            lines_per_block = int(lines[0].strip()) + 2
            fifth_block = lines[4 * lines_per_block : 5 * lines_per_block]
            rescue_file = wd / f"{self.molecule_name}.rescue.xyz"
            with open(rescue_file, 'w') as f: f.writelines(fifth_block)
            return str(rescue_file)
        except Exception as e:
            print(f"Couldn't generate rescue structure for {self.molecule_name}: {e}")
            return None

    def _spawn_rescue_job(self, manager: 'StateManager', new_xyz_path: str):
        new_name = f"{self.molecule_name}_Rescue"
        new_dir = Path(self.working_dir).parent / new_name
        new_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(new_xyz_path, new_dir / "input.xyz")

        rescue_job = job_factory(
            molecule_name=new_name, stage=self.stage, parent_id=self.id,
            working_dir=str(new_dir), pipeline_profile=self.pipeline_profile
        )
        rescue_job.params = self.params.copy()
        manager.add_job(rescue_job)
        print(f"  -> Rescue job {new_name} spawned.")


class FrequencyJob(Job):
    def validate(self, manager: 'StateManager') -> bool:
        outfile = Path(self.working_dir) / f"{self.molecule_name}.out"
        if not super().validate(manager): return False

        frequencies = parsers.get_all_frequencies(outfile)
        if not frequencies:
            self.mark_failed("No frequencies found")
            return False

        mode = self.params.get('validation_mode', 'minimum')
        imaginary = [f for f in frequencies if f < -30.0]

        if mode == "minimum" and imaginary:
            self.mark_failed(f"Found imaginary freqs: {imaginary}")
            return False
        elif mode == "transition_state" and len(imaginary) != 1:
            self.mark_failed(f"TS Validation failed. Found {len(imaginary)} imaginary modes.")
            return False
        elif mode == "raman_id":
            target_vibs = parsers.analyze_displacements(outfile, atoms=["Fe", "O"])
            if not target_vibs:
                self.mark_failed("No Fe-O vibration identified.")
                return False
            self.results['fe_o_mode'] = target_vibs[0]

        lowest_vib = frequencies[6] if len(frequencies) > 6 else frequencies[0]
        self.mark_completed({"lowest_freq": lowest_vib})
        return True


class IRCJob(Job):
    def validate(self, manager: 'StateManager') -> bool:
        if not super().validate(manager): return False
        wd = Path(self.working_dir)
        self.mark_completed({
            "forward_xyz": str(wd / f"{self.molecule_name}_IRC_F.xyz"),
            "reverse_xyz": str(wd / f"{self.molecule_name}_IRC_B.xyz")
        })
        return True

    def spawn_children(self, manager: 'StateManager', pipelines: dict):
        """IRC jobs spawn two children from the forward and reverse endpoints."""
        if not (fwd := self.results.get('forward_xyz')) or not (rev := self.results.get('reverse_xyz')):
            print(f"Warning: IRC job {self.molecule_name} missing endpoint XYZs in results.")
            return

        profile_name = self.pipeline_profile
        roadmap = pipelines.get(profile_name)
        if not roadmap or not (rules := roadmap.get(self.stage)): return

        for step in rules.get('next_steps', []):
            if 'Opt' in step['stage']:
                _spawn_child_job(self, step, f"{step['folder']}_Fwd", f"{self.molecule_name}_Fwd", manager, pipelines, {'initial_xyz': fwd})
                _spawn_child_job(self, step, f"{step['folder']}_Rev", f"{self.molecule_name}_Rev", manager, pipelines, {'initial_xyz': rev})
            else:
                super().spawn_children(manager, pipelines) # Fallback for non-opt children


class SpecialContextJob(Job):
    """A job that requires special files like parent hessians or product structures."""
    def get_submission_context(self, manager: 'StateManager', config: dict, project_root: Path) -> Dict[str, Any]:
        context = super().get_submission_context(manager, config, project_root)
        def resolve(key, default=None): return self.params.get(key, default)

        # Logic for NEB product structure
        if "neb" in self.stage:
            product_xyz_name = utils.find_and_copy_product_xyz(self, manager, project_root)
            if product_xyz_name == "WAIT":
                context['_hold_submission'] = True
            context['product_xyz_coord_fname'] = product_xyz_name if product_xyz_name != "WAIT" else ""

        # Logic for OptTS/IRC parent hessian
        if "irc" in self.stage or self.stage == "OptTS":
            context['ts_hess_fname'] = utils.find_and_copy_parent_hessian(self, manager) or ""

        # Formatting for OptTS params
        if ts_mode_val := resolve('ts_mode'): context['ts_mode'] = f"ts_mode {{ M {ts_mode_val} }}"
        if recalc_hess_val := resolve('recalc_hess'): context['recalc_hess'] = f"recalc_hess {recalc_hess_val}"
        if hybrid_hess_val := resolve('hybrid_hess'):
            vals = ' '.join(map(str, hybrid_hess_val)) if isinstance(hybrid_hess_val, list) else hybrid_hess_val
            context['hybrid_hess'] = f"hybrid_hess {{ {vals} }}"

        return context


JOB_CLASS_MAP = {
    "OptTS": SpecialContextJob, "tddft_opt": OptimizationJob, "TightOpt": OptimizationJob,
    "LooseOpt": OptimizationJob, "IrcOpt": OptimizationJob, "Freq": FrequencyJob,
    "NumFreq": FrequencyJob, "NebFreq": FrequencyJob, "TsFreq": FrequencyJob,
    "IrcFreq": FrequencyJob, "moessbauer": Job, "tddft": Job,
    "neb_ci": SpecialContextJob, "neb_ts": SpecialContextJob, "SCF": Job, "irc": SpecialContextJob,
}

def job_factory(stage: str, **kwargs) -> Job:
    """Creates an instance of the correct Job subclass based on the stage name."""
    job_class = JOB_CLASS_MAP.get(stage, Job)
    return job_class(stage=stage, **kwargs)