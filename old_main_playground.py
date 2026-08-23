from job_director import JobDirector

def main():
    """
    The client code. It is now much simpler. It only needs to know
    what kind of job it wants ('simple_job' or 'complex_job') and
    ask the Director to build it.
    """
    print("### Demonstrating the Director Pattern ###\n")

    # --- This variable models the user input ---
    # --- Try changing it to "complex_job" or "validation_only_job" ---
    user_job_type = "simple_job" 
    
    print(f"--> Client requests a '{user_job_type}'")

    # 1. Instantiate the Director
    director = JobDirector()

    # 2. Ask the Director to build the job. All complex logic is hidden.
    try:
        my_job = director.build_job(
            job_type=user_job_type, 
            name=f"My {user_job_type}"
        )
        print(f"--> Director successfully built job: {my_job}\n")
        my_job.run()
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()