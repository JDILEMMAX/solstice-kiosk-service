# Scope Delta Analysis: Mid-Sprint Requirement Pivot

**Client:** Solstice Events Co.  
**Project:** Check-In Kiosk & Badge Printing Service  
**Author:** Jesse Vincent (`jdilemmax`)  
**Sprint Phase:** Day 4/5 Refactor & Review

---

## 1. Executive Summary
During sprint execution, Solstice Events Co. received non-negotiable notice from their venue badge-printer vendor that the synchronous print API was being deprecated immediately. The engineering objective pivoted from a synchronous request/response model to an asynchronous, decoupled message queue and webhook callback architecture while strictly enforcing existing duplicate-scan protections.

---

## 2. Architectural Comparison Matrix

| Dimension | Original Specification (Day 3 Baseline) | Refactored Architecture (Day 4/5 Pivot) |
| :--- | :--- | :--- |
| **Communication Model** | Synchronous, blocking HTTP REST calls to vendor | Asynchronous event publishing via in-memory message queue |
| **UI State Transition** | Direct transition from Scanned to `Checked In` | Intermediate state transition: Scanned to `Pending` to `Checked In` |
| **Print Confirmation** | Immediate HTTP 200 response from vendor API | Out-of-band webhook callback to `POST /api/webhooks/printer` |
| **Worker Processing** | Single thread blocked during print execution | Background consumer worker processing queue jobs asynchronously |
| **Failure Tolerance** | Network timeouts directly caused failed kiosk scans | Queue ingestion guarantees job receipt even during printer latency |

---

## 3. Deprecated & Removed Architecture
To ensure architectural integrity and prevent legacy code from executing in parallel, the following components were formally retired:

* **Synchronous Print Driver (`backend/sync_printer_legacy.py`):** The direct, blocking HTTP client responsible for calling the synchronous printer API was decoupled and marked deprecated.
* **Immediate Success Frontend Handlers:** Client-side event logic that assumed synchronous printing success upon initial button submission was removed.

---

## 4. Modified Components
* **Attendee Data Schema (`data/schema.sql`):** Updated attendee status enums to include `UNREGISTERED`, `PENDING_PRINT` and `CHECKED_IN`, accompanied by tracking columns for `print_job_id` and `badge_issued_at`.
* **Duplicate-Scan Guard Logic (`backend/main.py`):** Modified the scan validation query to reject duplicate scans if an attendee is in either `CHECKED_IN` or `PENDING_PRINT` status, preventing duplicate queue publishing even when callbacks arrive out of order.
* **Kiosk UI State Machine (`frontend/app.js`):** Introduced a non-blocking UI polling mechanism that displays an amber "Printing Badge..." badge state until the background webhook updates the local database.

---

## 5. Net New Additions
* **In-Memory Message Queue (`backend/queue_manager.py`):** Implemented a thread-safe `asyncio.Queue` worker pipeline that accepts print tasks and processes jobs in the background without blocking FastAPI request workers.
* **Vendor Webhook Listener (`POST /api/webhooks/printer`):** Added a secure callback endpoint that verifies incoming job IDs, transitions attendee records to `CHECKED_IN` and logs print timestamps.
* **Automated Webhook Test Suite (`tests/test_async_webhook.py`):** Created unit and integration tests verifying asynchronous queue ingestion, webhook payload processing, out-of-order delivery tolerance and duplicate scan rejections.

---

## 6. Trade-off Documentation & Risk Management
* **In-Memory Queue Selection:** An internal `asyncio.Queue` was implemented rather than an external message broker (such as Redis or RabbitMQ) to eliminate external infrastructure dependencies and guarantee reliable delivery within the strict 48-hour pivot window.
* **Out-of-Order Callbacks:** To handle out-of-order webhook arrivals, database state transitions use atomic SQL conditions ensuring records cannot be overwritten by stale callbacks.