from job import Job
from strategy_register import STRATEGY_REGISTER

class JobDirector:
    """
    Acts as a Director. It knows how to construct a Job
    based on a string identifier by using the STRATEGY_REGISTER.
    This hides the complex construction logic from the client.
    """
    def build_job(self, job_type: str, name: str) -> Job:
        """
        Constructs and returns a fully configured Job object.
        
        Args:
            job_type: A string key that exists in the STRATEGY_REGISTER.
            name: The desired name for the job.
            
        Returns:
            A configured Job instance.
            
        Raises:
            ValueError: If the job_type is not found in the register.
        """
        # 1. Look up the configuration from the register
        job_config = STRATEGY_REGISTER.get(job_type)
        if not job_config:
            raise ValueError(f"Job type '{job_type}' not found in the register.")

        # 2. Create the product and set its properties
        new_job = Job()
        new_job.name = name

        # 3. Instantiate and inject dependencies (strategies) based on the config
        if pre_validator_class := job_config.get("pre_validator"):
            new_job.pre_validator = pre_validator_class()
        if post_validator_class := job_config.get("post_validator"):
            new_job.post_validator = post_validator_class()

        return new_job