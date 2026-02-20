import subprocess
from typing import Set, Dict

class ClusterInterface:
    """
    Handles communication with the remote cluster (rigi) via SSH.
    """
    def __init__(self, remote_host: str = "rigi", username: str = "lege"):
        self.remote_host = remote_host
        self.username = username
        self.ssh_target = f"{username}@{remote_host} -t "

    def _run_ssh_command(self, command: str) -> str:
        """
        Internal helper to execute a command over SSH and return the text output.
        """
        # We wrap the command in quotes for the SSH call
        # equivalent to: ssh user@host "command"
        ssh_cmd = "ssh " + self.ssh_target + command
        
        try:
            # capture_output=True grabs what would be printed to screen
            # text=True ensures we get a String back, not Bytes
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            # This happens if the SSH fails or the remote command returns an error
            print(f"SSH Command Failed: {e}")
            print(f"Error Output: {e.stderr}")
            return None

    def submit_job(self, working_dir: str, submission_script: str ,input_name: str) -> str:
        """
        Submits a job and returns the PBS/Slurm Job ID.
        """
        # Construct the command string exactly as you like it:
        # cd /path/to/dir; suborca.py calc.inp
        remote_cmd = f"\'cd {working_dir} && {submission_script} {input_name}\'"
        
        print(f"Submitting: {remote_cmd}")
        output = self._run_ssh_command(remote_cmd)
        
        if output:
            # PBS usually outputs: "12345.rigi" or just "12345"
            # We assume the last line of output is the ID
            job_id = output.splitlines()[-1].strip()
            return job_id
        return None

    def get_active_job_ids(self) -> Set[str]:
        """
        Runs qstat and returns a set of all currently running/queued Job IDs.
        """
        # qstat -u username lists only your jobs
        # We can add columns extraction if needed later
        remote_cmd = f"\'qstat -u {self.username}\'"
        
        output = self._run_ssh_command(remote_cmd)
        active_ids = set()
        
        if output:
            lines = output.splitlines()
            # Skip header lines (usually top 2-3 lines in qstat)
            # Standard PBS format:
            # JobID      Username    Queue    Jobname    SessID  NDS  TSK   Memory Time  S Time
            # 55001.rigi lege        batch    Fe_opt      ...    ...   ...    ...   ...  R ...
            
            for line in lines:
                parts = line.split()
                if not parts: continue
                
                # Check if the first part looks like a Job ID (digits)
                # This filters out the header lines automatically
                job_id_str = parts[0]
                if job_id_str[0].isdigit():
                    # clean up "55001.rigi" -> "55001" if you prefer, 
                    # or keep the full string. I recommend keeping it simple first.
                    active_ids.add(job_id_str)
                    
        return active_ids

    def get_free_slots(self) -> Dict[str, int]:
        """
        Checks available nodes based on the user's specific cluster layout.
        Returns a dict like {'cpu-44': 2, 'cpu-48': 0}
        """
        # Hardcoded totals from user alias
        totals = {
            "cpu-44": 5,
            "cpu-48": 12,
            "cpu-12": 12,
            "cpu-14": 4,
            "cpu-32": 13
        }
        
        output = self._run_ssh_command("qstat -n")
        if not output:
             return {}

        free_slots = {}
        lines = output.splitlines()
        for node_type, total in totals.items():
            # Count lines containing node_type (matches 'grep | wc -l')
            occupied = sum(1 for line in lines if node_type in line)
            free = total - occupied
            free_slots[node_type] = max(0, free)
            
        return free_slots