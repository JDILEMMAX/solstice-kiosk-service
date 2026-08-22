# Solstice Events Co. - Check-In Kiosk & Badge Printing Service

An event check-in kiosk application and asynchronous badge-printing engine built for Solstice Events Co. during the 1MILL Devs Evaluation Phase under Power Learn Project Africa.

---

## 1. Project Context & Objectives
Solstice Events Co. is hosting a multi-day international tech conference. This system provides a resilient kiosk service for on-site staff to scan attendee QR codes, process badge printing jobs and enforce strict duplicate entry policies.

### Core Business Rules:
1. **Attendee QR Scan:** Staff scan an attendee's unique QR code to retrieve credentials and issue an automated badge-print request.
2. **Duplicate-Scan Protection:** If an attendee has already checked in or has a print job in flight, any subsequent scan must be rejected immediately to prevent wasted badge stock and credential cloning.
3. **Multi-Attendee Verification:** Built-in seed data handles multiple real-world attendee profiles, including dedicated test cases for first-time check-in and duplicate-scan rejections.

---

## 2. The Meridian Pivot: Architectural Transformation
During sprint execution, the venue's badge-printer vendor abruptly deprecated its synchronous REST API. The system was refactored from a blocking, synchronous model to a resilient, asynchronous event-driven architecture.

### Architectural Evolution:
* **Original Model (Day 3 Baseline):** The kiosk endpoint received the QR scan, executed a blocking HTTP request to the vendor printer API, waited for a synchronous 200 OK response and then displayed "Checked In" on the screen.
* **Refactored Model (Day 4/5 Pivot):** The kiosk endpoint receives the scan, performs atomic duplicate validation, publishes the print payload to an asynchronous in-memory message queue (`asyncio.Queue`) and immediately returns a `Pending` state to the UI.
* **Webhook Confirmation:** A dedicated webhook endpoint (`POST /api/webhooks/printer`) receives asynchronous completion callbacks from the printer vendor and promotes the attendee status from `Pending` to `Checked In`.

---

## 3. Tech Stack
* **Backend:** Python 3.10+ and FastAPI framework
* **Asynchronous Queue:** Python `asyncio.Queue` for non-blocking task orchestration
* **Database:** SQLite 3 with atomic transaction management and custom seeder scripts
* **Frontend:** Native HTML5, modern CSS3 and JavaScript (ES6 Fetch API with status polling)
* **Testing & Verification:** Pytest, FastAPI TestClient and automated End-to-End browser test suites

---

## 4. Repository Directory Structure
```text
solstice-kiosk-service/
│
├── frontend/                  # Event Kiosk Staff Interface
│   ├── index.html             # Single-page scanner dashboard
│   ├── styles.css             # Responsive kiosk styling & badge animation states
│   └── app.js                 # Scan event handlers & pending-state status polling
│
├── backend/                   # FastAPI Backend Application
│   ├── main.py                # REST endpoints, CORS setup & webhook listeners
│   ├── database.py            # SQLite connection pool & query helpers
│   ├── models.py              # Pydantic schemas for check-in requests & callbacks
│   ├── queue_manager.py       # Asyncio message queue producer/consumer workers
│   └── sync_printer_legacy.py # Deprecated synchronous printer service (historical audit)
│
├── data/                      # Data Persistence Layer
│   ├── schema.sql             # Relational table definitions for attendees & print logs
│   ├── seed.py                # Database seeder with 3+ mock attendee test profiles
│   └── solstice.db            # Local SQLite database instance
│
├── recon/                     # Assignment 1 Solo Recon Deliverables
│   ├── queue_prototype.py     # Standalone mini-prototype demonstrating message queues
│   ├── JOURNAL_TEMPLATE.md    # Master template for learning logs
│   └── JOURNAL.md             # Solo Learning & Blocker Journal
│
├── tests/                     # Automated Verification Suites
│   ├── test_sync_legacy.py    # Verification tests for baseline synchronous printing
│   ├── test_async_webhook.py  # Verification tests for message queue & webhook callbacks
│   ├── test_sanity.py         # End-to-end routing & duplicate-scan validation tests
│   └── test_e2e_browser.py    # Headless browser E2E test for UI transitions & duplicate guard
│
├── docs/                      # Sprint Audit Documentation
│   ├── CONTRIBUTING.md        # Git branching standards & commit message rules
│   └── SCOPE_DELTA.md         # Comprehensive Scope Delta Analysis & change log
│
├── README.md                  # Main setup and architecture guide
├── requirements.txt           # Python dependencies (fastapi, uvicorn, httpx, pytest)
└── .gitignore                 # Excludes cache files, db locks & virtual environments
```

---

## 5. Local Setup & Running Instructions

### Prerequisites:
* Python 3.10 or higher installed
* A modern web browser (Chrome, Firefox, Safari or Edge)

### Step 1: Clone the Repository
```bash
git clone https://github.com/JDILEMMAX/solstice-kiosk-service.git
cd solstice-kiosk-service
```

### Step 2: Set Up Virtual Environment & Dependencies
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv solstice-kiosk-service
   source solstice-kiosk-service/bin/activate  # On Windows: solstice-kiosk-service\Scripts\activate
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize and seed the SQLite database:
   ```bash
   python data/seed.py
   ```

### Step 3: Start the Backend Server
```bash
uvicorn backend.main:app --reload
```
The API server will be live at `http://127.0.0.1:8000`. You can inspect interactive documentation at `http://127.0.0.1:8000/docs`.

### Step 4: Run Verification Tests
Run the comprehensive test suite to validate synchronous legacy behavior, async message queue ingestion, webhook callbacks and duplicate protection:
```bash
pytest tests/
```
Run the Playwright headless browser E2E test to verify UI transitions and duplicate guard:
```bash
"D:\Software Development & IT Programs\_PROJECTS\viridian-recon\viridian_recon\Scripts\pytest.exe" tests\test_e2e_browser.py
```

### Step 5: Launch the Kiosk UI
Open `frontend/index.html` directly in your browser or run it with Live Server in VS Code to test QR scans, pending badge animations and real-time confirmations.

---

## 6. Evaluation Deliverables Index
* **Assignment 1 (Solo Recon):** Standalone message queue prototype in [`recon/queue_prototype.py`](./recon/queue_prototype.py) and documentation in [`recon/JOURNAL.md`](./recon/JOURNAL.md).
* **Assignment 2 (Deliverable & Scope Delta):** Fully refactored asynchronous kiosk engine with complete architectural impact tracked in [`docs/SCOPE_DELTA.md`](./docs/SCOPE_DELTA.md).