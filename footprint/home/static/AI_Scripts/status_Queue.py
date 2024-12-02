from rq import Queue
from redis import Redis
from rq.job import Job
from rq.registry import StartedJobRegistry

# Redis connection
redis_conn = Redis(host='localhost', port=6379)
queue_name = 'default'  # Default queue name 
q = Queue(name=queue_name, connection=redis_conn)

def view_all_jobs():
    # Initialize the StartedJobRegistry
    started_job_registry = StartedJobRegistry(name=queue_name, connection=redis_conn)
    
    # Fetch started job
    started_jobs = []
    for job_id in started_job_registry.get_job_ids():
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            started_jobs.append(job)
        except Exception as e:
            print(f"Warning: Could not fetch job {job_id} due to: {e}")
            started_job_registry.remove(job_id)  

    # Get queued jobs directly from the queue
    queued_jobs = []
    for job_id in q.get_job_ids():
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            queued_jobs.append(job)
        except Exception as e:
            print(f"Warning: Could not fetch job {job_id} due to: {e}")

    # Display started job if there is one - used for debugging
    if started_jobs:
        started_job = started_jobs[0]
        video_url = started_job.args[0]
        user_id = started_job.args[2]
        print(f"Current Processing Video: \"User ID: {user_id}\", \"Video Link: {video_url}\"")
    else:
        print("No currently processing video.")

    # Display queued jobs in order
    if queued_jobs:
        for position, job in enumerate(queued_jobs, start=1):
            video_url = job.args[0]
            user_id = job.args[2]
            print(f"{position} in Queue: \"User ID: {user_id}\", \"Video Link: {video_url}\"")
    else:
        print("No videos in queue.")

if __name__ == "__main__":
    view_all_jobs()
