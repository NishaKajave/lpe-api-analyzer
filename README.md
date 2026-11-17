# LoopLens: OpsZero Autonomous Loop Engineering API Failure Analyzer
## Autonomous Evaluator-Optimizer Control Center for API Test Healing & Live Telemetry

LoopLens is an enterprise Loop Engineering platform utilizing the **Evaluator-Optimizer pattern**, tailored for **Capgemini's OpsZero** autonomous operations initiative. It autonomously intercepts live and regression API failures, evaluates remediations against an independent 100-point weighted rubric, iteratively retries with targeted validator feedback (up to 5 attempts), generates unified Git code patches, halts with explicit criteria, and mandates developer review.

> [!IMPORTANT]
> **Complete Project Report (Word Document):**  
> For the comprehensive project report covering the problem statement, UI mechanics, Loop Engineering architecture, live data integration, OpsZero alignment, and live demo script, see:  
> **[`LoopLens_Loop_Engineering_OpsZero_Complete_Project_Report.docx`](LoopLens_Loop_Engineering_OpsZero_Complete_Project_Report.docx)**
>
> **Technical Execution Reference:**  
> For the detailed technical breakdown and presentation guide, see:  
> **[`FINAL_USECASE_EXECUTION.md`](FINAL_USECASE_EXECUTION.md)**

---

## Key Features

1. **Complete Loop Attempt Persistence:**
   * Every Analyzer and Evaluator cycle is stored separately (`analysis_id`, `attempt_number`, `analyzer_output`, `validation_score`, `confidence_score`, category breakdowns, `validator_feedback`, duration, timestamps, tokens, and cost).
   * Visual before-and-after diffs highlight exactly what improved between attempts.

2. **Weighted Validation System (100 Points):**
   * **Required Fields:** 20 pts (category, root cause, evidence, action, file, confidence)
   * **Evidence Quality:** 25 pts (HTTP status cited, error payload support, verified context)
   * **Recommendation Quality:** 25 pts (multiple actionable steps, developer-executable, non-generic)
   * **Safety Guard:** 15 pts (masked credentials, zero-tolerance policy against destructive commands)
   * **Technical Correctness:** 15 pts (category alignment, target file consistency, root cause mapping)

3. **Separated Confidence vs. Evaluator Score:**
   * **Analyzer Confidence:** Model certainty in recommendation.
   * **Evaluator Score:** Objective independent compliance score.
   * Scenarios like **95% Confidence / 60% Validation** demonstrate the vital role of independent validation.

4. **OpsZero Live API Health Prober & Synthetic Telemetry (Live Data):**
   * Real-time HTTP network prober tracking latency in milliseconds (`POST /api/live/probe`).
   * Built-in mock microservices (`/api/live-demo/auth-gateway`, `/order-service`, `/inventory-service`, `/payment-gateway`, `/health`) and external public API support (`https://httpbin.org/status/401`).
   * 1-Click live failure ingestion directly into the Evaluator-Optimizer loop (`POST /api/live/ingest`).
   * Closed-loop verification re-probing (`POST /api/live/verify/{id}`) confirming live endpoint recovery.

5. **Automated Unified Git Remediation Patches (Diffs):**
   * Generates production-grade unified diff code patches (`.py`, `.ts`, controller handlers).
   * 1-Click "Copy Git Patch" and live preview with syntax-highlighted additions and removals.

6. **OpsZero Autonomy Levels & MTTR Reduction Hub:**
   * **Zero-Touch Readiness KPI (52%):** Failures resolved autonomously within <= 2 attempts.
   * **MTTR Reduction KPI (18.5h saved):** Collapses root cause analysis from 45 min down to 4.2 sec (~91% reduction).
   * Autonomy level classifications: L0 (Manual), L1 (Assisted/Diagnostic), L2 (Autonomous + Developer Gate), L3 (Full Zero-Touch).

7. **Presenter Demo Showcase Bar (1-Click Presentation Tour):**
   * **Demo 1 (Auth Failure - 401):** Passes on Attempt 2 (Confidence: 91%, Validation: 97%, Stop: `PASSED_VALIDATION`).
   * **Demo 2 (Backend Null Reference - 500):** Passes on Attempt 4 (Confidence: 84%, Validation: 97%, Stop: `PASSED_VALIDATION`).
   * **Demo 3 (Unknown RPC Failure - 500):** Fails after Attempt 5 (Confidence: 65%, Validation: 72%, Stop: `MAX_ATTEMPTS_REACHED`).
   * **Demo 4 (Needs More Context):** Halts at Attempt 1 (`INSUFFICIENT_CONTEXT`), recovered via "Provide More Context" modal.
   * **Demo 5 (Live API Prober):** Live HTTP network probing with real-time latency and autonomous healing.

8. **Controlled Batch Execution:**
   * Processes `PENDING` and `FAILED` records with a strict concurrency limit of 3 at a time.
   * Interactive live progress modal with animated progress bar and real-time card updates.
   * Emergency **Stop Batch** handler for graceful cancellation.

9. **Human Developer Sign-off & Historical Feedback Loop:**
   * Reviewer name (`Nisha Kajave`).
   * Mandatory rejection reasons and comments.
   * Historical review comments feed context into future Analyzer cycles.

10. **Automated Secret Masking & Pytest Runner:**
    * Scans and scrubs Bearer tokens, passwords, API keys, and connection strings.
    * Safe execution of approved pytest suites (`tests/test_api.py`, `tests/test_live_prober.py`, `tests/test_auth_suite.py`, `tests/test_regression_suite.py`).

---

## Quickstart & Execution

### 1. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 2. Start Application Server
Option A: Double-click **`run.bat`** (or execute `.\run.bat` in PowerShell).  
Option B: Run from terminal:
```powershell
py -m uvicorn app.main:app --reload
```
*(or `python -m uvicorn app.main:app --reload`)*

Open **`http://127.0.0.1:8000`** in your browser.

### 3. Run Automated Pytest Suites
Option A: Double-click **`test.bat`**.  
Option B: Run from terminal:
```powershell
py -m pytest tests/test_api.py tests/test_live_prober.py -v -p no:langsmith
```

---

## API Endpoints

* `GET /api/analyses` — List all failures with metadata & scores
* `POST /api/analyses` — Create failure with automated secret masking
* `POST /api/analyses/{id}/run` — Run Evaluator-Optimizer loop on single record
* `GET /api/analyses/{id}/attempts` — Retrieve complete attempt history & improvement diffs
* `POST /api/analyses/{id}/decision` — Submit human approval or rejection
* `POST /api/analyses/{id}/context` — Provide missing diagnostic logs & stack trace
* `POST /api/analyses/run-pending` — Start controlled batch analysis
* `GET /api/batches/{id}` — Poll batch progress
* `POST /api/batches/{id}/stop` — Cancel active batch cleanly
* `GET /api/metrics` — Dashboard KPIs, Zero-Touch readiness, MTTR reduction & root causes
* `POST /api/live/probe` — Probe live HTTP endpoint and capture latency/payload
* `POST /api/live/ingest` — Ingest live probe failure into LoopLens Evaluator-Optimizer loop
* `POST /api/live/verify/{id}` — Re-probe live endpoint to verify remediation fix
* `GET /api/live-demo/*` — Built-in mock microservices (/auth-gateway, /order-service, etc.)
* `GET /api/audit-logs` — System audit trail
* `POST /api/test-suite/run` — Run approved pytest test suite
* `POST /api/reset-data` — Reset database to clean 25 sample failures



<!-- running project in terminal command
py -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload 
 -->