# Learning & Blocker Journal: Independent Solo Recon

**Developer:** Jesse Vincent (`jdilemmax`)  
**Assigned Unfamiliar Tool:** Asynchronous Message Queues (Python `asyncio.Queue`)  
**Sprint:** The Meridian Pivot (Assignment 1)

---

## 1. Recon Objective
The objective of this solo investigation was to teach myself how to implement an asynchronous producer/consumer message queue pattern in Python without technical assistance from teammates or instructors. The final deliverable is a standalone mini-prototype (`recon/queue_prototype.py`) capable of ingesting jobs, decoupling long-running background tasks and processing queue items reliably.

---

## 2. Resources Consulted
1. [Python Official Documentation - asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html)
2. [Real Python - Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/)
3. [FastAPI Documentation - Background Tasks & Concurrency](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

## 3. The Mini-Prototype Implementation
* **Prototype Script:** `recon/queue_prototype.py`
* **Architecture:** Built a producer coroutine that accepts event check-in payloads and puts them onto an `asyncio.Queue`, paired with a decoupled worker consumer that reads tasks from the queue and simulates hardware print latency.
* **Execution Command:**
  ```bash
  python recon/queue_prototype.py
  ```

---

## 4. Blocker & Troubleshooting Log

### Blocker 1: Coroutine Execution Context & Event Loop Crash
* **The Error:** Encountered `RuntimeError: There is no current event loop in thread` when attempting to call queue operations directly inside a standard procedural testing function.
* **Root Cause:** In Python 3.10+, `asyncio.Queue` must be instantiated and operated within an active, running asynchronous event loop rather than at the top-level module scope.
* **Troubleshooting Steps:** Tested creating manual event loops via `asyncio.get_event_loop()`, which caused deprecation warnings.
* **Autonomous Resolution:** Encapsulated the producer, queue instantiation and worker startup within an async `main()` entrypoint executed through `asyncio.run(main())`.

### Blocker 2: Premature Script Exit Before Queue Worker Drain
* **The Error:** The producer finished generating print tasks, but the script exited immediately, leaving unfinished tasks in the queue without the worker consumer processing them.
* **Root Cause:** The main coroutine completed its execution cycle without awaiting a synchronization barrier for in-flight queue items.
* **Autonomous Resolution:** Implemented `await queue.join()` in the supervisor coroutine and added explicit `queue.task_done()` calls inside the worker consumer `finally` block, ensuring all background tasks drain before application shutdown.

---

## 5. Time Tracking & Self-Assessment
* **Allocated Time Box:** 4.0 Hours
* **Actual Time Spent:** 2.75 Hours
* **Self-Assessment:** Successfully mastered asynchronous producer/consumer patterns, non-blocking queue synchronization and exception containment in Python, providing the exact architectural foundation required for Solstice Events Co.'s mid-sprint pivot.