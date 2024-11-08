from rq import Queue
from redis import Redis
from rq.job import Job

# Redis connection
redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)

def cancel_job(job_id):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        job.cancel()
        print(f"Cancelled job {job_id}")
    except Exception as e:
        print(f"Could not cancel job {job_id}: {e}")

if __name__ == "__main__":
    job_id = input("Enter the Job ID to cancel: ")
    cancel_job(job_id)
