import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def producer(queue: asyncio.Queue, num_jobs: int):
    """Generates print jobs and puts them on the queue."""
    for i in range(num_jobs):
        job = f"print_job_{i+1}"
        logger.info(f"Producing {job}")
        await queue.put(job)
        await asyncio.sleep(0.5)

async def consumer(queue: asyncio.Queue):
    """Consumes print jobs from the queue and simulates hardware latency."""
    while True:
        job = await queue.get()
        try:
            logger.info(f"Consuming {job}")
            await asyncio.sleep(1.0)
            logger.info(f"Completed {job}")
        finally:
            queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    # Start the worker
    worker_task = asyncio.create_task(consumer(queue))
    
    # Run the producer
    await producer(queue, 5)
    
    # Wait for the queue to drain completely
    logger.info("Waiting for queue to drain...")
    await queue.join()
    logger.info("Queue drained.")
    
    # Cancel the worker task as we are done
    worker_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted.")
