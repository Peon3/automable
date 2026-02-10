import os
import shutil
import parsers
from pathlib import Path
from typing import Dict
from state_manager import Job, StateManager

class JobValidator:
    """
    The Gatekeeper. Parses output files and applies scientific sanity checks.
    Manages Self-Healing (Rescue) workflows.
    """
    def __init__(self, project_config: Dict, manager: StateManager):
        self.config = project_config
        self.manager = manager
        
    def validate(self, job) -> bool:
        """
        Main entry point. 
        """
        outfile = Path(job.working_dir) / f"{job.molecule_name}.out"
        
        if not outfile.exists():
            job.mark_failed("Output file not found")
            return False

        match job.stage:
            case "optimization":
                return self._validate_optimization(job, outfile)
            case "frequency":
                return self._validate_frequency(job, outfile)
            case "moessbauer":
                return self._validate_spectroscopy(job, outfile)
            case _:
                job.mark_failed(f"Unknown stage: {job.stage}")
                return False

    def _validate_optimization(self, job, outfile) -> bool:        
        # --- A. Basic Convergence ---
        return True         #debugging
        scf_is_converged = parsers.parse_orca_scf_conv(outfile)
        if not scf_is_converged:
            job.mark_failed("SCF did not converge")
            return False
        
        geom_is_converged = parsers.parse_orca_geom_conv(outfile)

        has_imaginary = parsers.check_imaginary_frequencies(outfile)

        if has_imaginary:
            print(f"    -> Alert: Imaginary frequency(/ies) detected in Optimization {job.molecule_name}")

            # Attempt to generate the displaced structure
            new_xyz = self._generate_displaced_structure(job)

            if new_xyz:
                self._spawn_rescue_job(job, new_xyz)
                job.status = "rescued" # Mark as rescued
                job.log_event("Optimization converged to saddle point, atempting rescuing.")
                return False
            else:
                job.mark_failed("Saddle point detected, but rescue generation failed.")
                return False
        # --- RESCUE LOGIC END ---

        if not geom_is_converged:
            job.mark_failed("Geometry did not converge")
            return False

        # --- B. Success ---
        # Extract final energy for the record
        energy = parsers.parse_orca_energy(outfile)
        
        # Update the Job object with results
        job.mark_completed({
            "energy": energy,
            "final_xyz": str(outfile.with_suffix(".xyz")) # Path to optimized geom
        })
        return True

    def _validate_frequency(self, job, outfile) -> bool:
        # 1. Determine the "Mode" from params dict
        # Default to 'minimum' if not specified
        mode = job.params.get('validation_mode', 'minimum') 
        return True     #debugging

        # 2. Extract Data (Common to all modes)
        frequencies = parsers.get_all_frequencies(outfile)
        if not frequencies:
            job.mark_failed("No frequencies found")
            return False

        # 3. Apply the Strategy
        if mode == "minimum":
            imaginary = [f for f in frequencies if f < -30.0]
            if imaginary:
                job.mark_failed(f"Found imaginary freqs: {imaginary}")
                return False
                
        elif mode == "transition_state":
            # Rule: Exactly one imaginary freq < -30
            imaginary = [f for f in frequencies if f < -30.0]
            if len(imaginary) != 1:
                job.mark_failed(f"TS Validation failed. Found {len(imaginary)} imaginary modes.")
                return False
                
        elif mode == "raman_id":
            # Rule: Check against your custom displacement logic
            # This calls your specialized python script logic
            target_vibs = parsers.analyze_displacements(outfile, atoms=["Fe", "O"])
            if not target_vibs:
                job.mark_failed("No Fe-O vibration identified.")
                return False
            # Store the identified mode for later analysis
            job.results['fe_o_mode'] = target_vibs[0]

        job.mark_completed({"lowest_freq": frequencies[6]})
        return True

    def _validate_spectroscopy(self, job, outfile) -> bool:
        """
        Placeholder for your Moessbauer/EPR logic.
        """
        # This is where your custom 'grep_rho' function fits in
        # rho = parse_moessbauer_rho(outfile)
        # qs = parse_quadrupole_splitting(outfile)
        
        job.mark_completed({"rho": 0, "qs": 0})
        return True
    
    def _generate_displaced_structure(self, job) -> str:
        """
        Calls orca_pltvib to generate the displaced geometry.
        Returns the path to the new .xyz file, or None if failed.
        """
        wd = Path(job.working_dir)
        hess_file = wd / f"{job.molecule_name}.hess"
        
        if not hess_file.exists():
            print(" -> No .hess file found for rescue.")
            return None
        
        try:
            os.system(f"orca_pltvib {hess_file} 6")
            
            generated_file = wd / f"{job.molecule_name}.hess.v006.xyz"
            if not generated_file.exists():
                return None
            
            with open(generated_file, 'r') as f:
                lines = f.readlines()
            
            # The first line contains the number of atoms. Add 2 for the header/footer lines of a block.
            lines_per_block = int(lines[0].strip()) + 2
            
            # Extract the fifth block (index 4)
            fifth_block = lines[4 * lines_per_block : 5 * lines_per_block]
            
            rescue_file = wd / f"{job.molecule_name}.rescue.xyz"
            with open(rescue_file, 'w') as f:
                f.writelines(fifth_block)
            
            return str(rescue_file)

        except Exception as e:
            print(f"Couldn't generate rescue structure for {job.molecule_name}: {e}")
            return None
        
    def _spawn_rescue_job(self, failed_job, new_xyz_path):
        """
        Creates the rescue job and registers it with the manager.
        """
        # Name convention: Reactant -> Reactant_Rescue_1
        new_name = f"{failed_job.molecule_name}_Rescue"
        
        # Create new folder to keep things clean
        new_dir = Path(failed_job.working_dir).parent / new_name
        new_dir.mkdir(parents=True, exist_ok=False)
        
        # Copy the displaced XYZ to the new folder
        target_xyz = new_dir / "input.xyz"
        shutil.copy(new_xyz_path, target_xyz)
        
        # Create the Job
        # IMPORTANT: We keep stage="optimization" so it continues the pipeline naturally
        # IMPORTANT: We pass 'pipeline_profile' so it knows it is still part of the same branch
        rescue_job = Job(
            molecule_name=new_name,
            stage="optimization", 
            parent_id=failed_job.id,
            working_dir=str(new_dir),
            pipeline_profile=failed_job.pipeline_profile 
        )
        
        # Register
        self.manager.add_job(rescue_job)
        print(f"  -> Rescue job {new_name} spawned.")