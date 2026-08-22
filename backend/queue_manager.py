import asyncio
import uuid
import httpx
from datetime import datetime

class PrintJobQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def enqueue_job(self, qr_code: str, attendee_name: str) -> str:
        job_id = f"JOB-ASYNC-{uuid.uuid4()}"
        await self.queue.put({
            "job_id": job_id,
            "qr_code": qr_code,
            "attendee_name": attendee_name
        })
        return job_id

    async def worker(self):
        async with httpx.AsyncClient() as client:
            while True:
                job = await self.queue.get()
                try:
                    await asyncio.sleep(1.2)
                    
                    payload = {
                        "job_id": job["job_id"],
                        "qr_code": job["qr_code"],
                        "status": "completed",
                        "printed_at": datetime.now().isoformat()
                    }
                    
                    await client.post("http://localhost:8000/api/webhooks/printer", json=payload)
                except Exception as e:
                    print(f"Worker error processing job: {e}")
                finally:
                    self.queue.task_done()

print_queue = PrintJobQueue()
