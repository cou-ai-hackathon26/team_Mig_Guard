# Mig_Guard (Job Offer Checker for Migrant Workers)

> AI-Powered Job Offer, Contract & Recruiter Chat Verification for Bangladeshi Overseas Migrant Workers.

**Repository:** [https://github.com/afradd/Mig_Guard.git](https://github.com/afradd/Mig_Guard.git)

---

## 1. Project, Team & Member Names

* **Project Name:** Mig_Guard
* **Team Name:** Mig_Guard Team
* **Team Members & Responsibilities:**
  * **Afrad Ali Ahim** ([@afradd](https://github.com/afradd)) — *Team Leader, AI & Backend Lead:* FastAPI architecture, Gemini Vision extraction pipeline, deterministic verification engine (license/fees/salary/clauses), risk scoring calibration, RAG legal grounding, and containerized deployment.
  * **Saima Ahmed** ([@Saima-Ahmedd](https://github.com/Saima-Ahmedd)) — *Member B, Frontend & UX Engineer:* Next.js web & mobile interface, responsive camera capture & file upload, Bangla bilingual localization (`bn`/`en`), and client-side audio speech synthesis player.
  * **Athikul Islam** ([@Athikul-Islam](https://github.com/Athikul-Islam)) — *Member C, Rules & Evaluation Lead:* 15 red-flag rule check algorithms, rule catalog definitions (`catalog.yaml`), knowledge-base corpus creation, and 20-document synthetic evaluation benchmark suite.

---

## 2. Problem & Solution Summary

### The Problem
Over 10 million Bangladeshi migrant workers remit vital billions annually, yet thousands fall victim to predatory overseas recruitment scams before departure. Traps include tourist/visit visas disguised as work permits, debt bondage through hidden salary deductions, exorbitant fees exceeding statutory government caps, fake recruiting agencies, and modern cyber-scam compound trafficking in Southeast Asia (Cambodia, Myanmar, Laos). Most official interventions happen after the worker is already stranded abroad.

### The Solution
**Mig_Guard** is an upstream fraud prevention engine that allows a prospective worker or family member to upload a photo of a job offer letter, contract, visa, or recruiter chat screenshot (or paste text). Mig_Guard:
1. Transcribes documents via Gemini Vision with a local OCR fallback.
2. Extracts 13 essential contractual fields and requires physical source text snippets for every value.
3. Deterministically benchmarks against official government databases (1,685 BMET licensed agencies, statutory fee caps, wage guidelines).
4. Evaluates 15 explainable red-flag rules and calculates a transparent 0–100 risk score.
5. Grounds explanations in verified Bangladeshi labor migration law and ILO conventions.
6. Delivers guidance in clear Bangla and spoken audio, accompanied by official helplines (e.g., Probash Bondhu 16135).
7. **Strict Safety Invariant:** Mig_Guard **never** declares any document "safe"; clean offers receive "fewer concerns found" with verification caveats.

---

## 3. Features & How the AI Works

### Key Features
* 📷 **Multimodal Ingestion:** Accepts camera photos, uploads (JPG, PNG, WEBP up to 8 MB), or pasted text in English and Bangla.
* 🔍 **Evidence-Backed Extraction:** Extracts 13 core contract fields (`employer`, `destination`, `job_title`, `salary`, `fee_asked`, `visa_type`, `duration`, `hours`, `accommodation`, `return_ticket`, `agent`, `license_number`, `payment_method`). Values lacking document text snippets are discarded.
* 🏛️ **BMET Agency Verification:** Automatically normalizes license numbers (e.g. `RL-1857`) and checks status against an offline snapshot of the official BMET Recruiting Agents Information Management System (RAIMS).
* 💰 **Statutory Fee-Cap Compliance:** Compares recruitment fees against destination-specific legal ceilings under Section 21 of the Overseas Employment and Migrants Act 2013 (e.g., Qatar ceiling of BDT 100,780).
* ⚖️ **Wage Benchmark Screening:** Detects hyper-inflated pay promises (>4× typical benchmark) commonly used by human traffickers to rush victims into paying.
* 📋 **Missing Protective Clauses Scan:** Identifies missing essential clauses including overtime, food, medical care, return airfare, termination terms, and dispute resolution.
* 🚩 **Explainable Red-Flag Heuristics:** Flags 15 recruitment scam patterns (non-work visas, cash-only payments, personal bKash/Nagad transfers, passport confiscation threats, social-media-only presence, sign-on-arrival traps).
* 📚 **RAG Legal Grounding:** Attaches official legal citations from BMET advisories and ILO standards to each triggered flag.
* 🔊 **Bangla Audio Readout:** Synthesizes an accessible audio verdict script for low-literacy users via Edge TTS or browser Web Speech API.
* ☎️ **Immediate Support Directory:** Surfaces direct dial links to government helplines (Probash Bondhu Call Center 16135, National Emergency 999, BMET).

### Architecture & Processing Flow

```text
User Input (Image/Photo/Text)
       │
       ▼
 ┌──────────────────────────────────────────────┐
 │           Ingestion & PII Redaction          │
 │  • Up to 4 images / pasted text              │
 │  • Passport & phone numbers masked           │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │         Vision & Transcription Layer         │
 │  • Primary: Gemini 3.1 Flash Vision          │
 │  • Fallback: Tesseract OCR (ben+eng)         │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │    Structured Extraction & Validation        │
 │  • Strict JSON Schema (OfferExtraction)      │
 │  • No-evidence-no-value snippet enforcement  │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │        Deterministic Verification Engine     │
 │  • BMET RAIMS Agency Registry (1,685 RLs)    │
 │  • Statutory Country Fee Caps (16 nations)   │
 │  • ILO/Host Wage Standards (Qatar Law 17)    │
 │  • Missing Protective Clauses Scan           │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │          Rule Engine & RAG Grounding         │
 │  • 15 Red-Flag Checks                        │
 │  • Token-overlap KB retrieval from 33 docs   │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐
 │         Scoring & Accessible Output          │
 │  • Score: 0 - 100                            │
 │  • Verdict: danger / caution / fewer_concerns│
 │  • Spoken Bangla Audio Script (Edge / Web)   │
 │  • Helpline Directory (16135, 999)           │
 └──────────────────────────────────────────────┘
```

---

## 4. Tech Stack, Models, APIs & Datasets

### Backend
* **Language & Framework:** Python 3.11+, FastAPI, Uvicorn, Starlette
* **Data Validation:** Pydantic v2
* **OCR Fallback:** `pytesseract` with Tesseract OCR (`ben+eng`) & Pillow
* **Rate Limiting & Safety:** Token bucket client limiter, PII redaction regexes

### Frontend
* **Framework:** Next.js 16 (App Router), React 19, TypeScript
* **Styling:** CSS variables, responsive design with mobile camera capture
* **Localization:** Custom zero-dependency bilingual dictionary (`bn`/`en`)
* **Audio:** HTML5 Web Speech API (`SpeechSynthesisUtterance`, `bn-BD`) with backend MP3 endpoint fallback

### AI Models & Cloud APIs
* **Primary Extraction Model:** Google Gemini API (`gemini-3.1-flash-lite` / `gemini-3.8-flash`) via `google-genai` SDK
* **Speech Generation:** Microsoft Edge TTS (`bn-BD-NabanitaNeural`) via `edge-tts`

### Datasets & Official Sources
* **BMET RAIMS Recruiting Agencies:** Public snapshot of 1,685 licensed recruiting agents from BMET / Overseas Employment Platform (`licensed_agencies.json`).
* **Statutory Fee Caps:** Ministry of Expatriates' Welfare & Overseas Employment published maximum migration costs (`fee_caps.json`).
* **Salary Benchmarks:** Qatar Law No. 17 of 2020 and ILO migrant wage surveys (`salary_benchmarks.json`).
* **Official Helplines:** BMET, Probash Bondhu Call Center, WARBE, BRAC Migration, National Emergency Service (`helplines.json`).
* **Knowledge Base Passages:** 33 curated passages across 8 thematic areas covering Bangladesh migration laws and worker rights (`app/rag/kb/`).

---

## 5. AI Tools Used & Transparent Disclosure

Per Rule 4 & 9 of CoU AI Hackathon 2026, all AI tool usage is disclosed:
* **Google Antigravity / Gemini CLI:** Assisted with architecture design, pipeline verification, data cleaning scripts, and test suite expansion.
* **GitHub Copilot in VS Code:** Assisted with frontend boilerplate and CI/CD workflow configuration.
* All AI suggestions were reviewed, modified, and validated through deterministic unit test suites and manual validation. Detailed logs are maintained in [`AI_USAGE.md`](AI_USAGE.md).

---

## 6. Third-Party Code & Assets Credited

* **FastAPI & Starlette:** Tiangolo / Encode (MIT License)
* **Pydantic:** Pydantic Services Inc. (MIT License)
* **Google GenAI Python SDK:** Google LLC (Apache-2.0 License)
* **Edge-TTS:** Hasson / edge-tts project (LGPL-3.0 License)
* **Pytesseract:** Samuel Hoffstaetter (GPL-3.0 License) & Google Tesseract OCR (Apache-2.0 License)
* **Government Public Records:** Bureau of Manpower, Employment and Training (BMET), Ministry of Expatriates' Welfare and Overseas Employment, Government of the People's Republic of Bangladesh.

---

## 7. Setup Instructions, Live Links & Evaluation

### Live Links
* **Backend API:** Deployed on Render (`mig-guard-backend`) — see [`render.yaml`](render.yaml)
* **Frontend Web App:** `https://mig-guard.vercel.app/`

---

### Local Setup Instructions

#### Prerequisites
* Python 3.11+
* Node.js 20+
* Google Gemini API Key

#### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and insert your PRIMARY_LLM_API_KEY

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be live at `http://localhost:8000`. Swagger API documentation available at `http://localhost:8000/docs`.

#### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install packages
npm install

# Run development server
npm run dev
```
Open `https://mig-guard.vercel.app/` in your browser.

#### 3. Run Automated Tests
```bash
cd backend
python -m pytest tests/ -v
```
All 66 tests (API endpoints, money parsing, license normalization, OCR fallback, rules engine, and scoring) will execute and pass.

#### 4. Validate Official Datasets
```bash
python scripts/validate_data.py
```
Validates JSON integrity, schema consistency, and KB passage counts.

---

## 8. Evaluation Benchmark Results

The evaluation suite tests the rule engine against a balanced 20-document synthetic dataset (8 legitimate contracts across Saudi Arabia, UAE, Malaysia, Singapore, Qatar; 12 fraudulent offers and chat lures across Cambodia, Myanmar, Laos, Dubai, Malaysia):

```bash
python eval/run_eval.py
```

### Benchmark Summary

| Metric | Target | Achieved Result |
| :--- | :---: | :---: |
| **Scam Red-Flag Recall** | $\ge 70\%$ | **113 / 113 (100.0%)** |
| **False Alarms on Legitimate Offers** | $\le 3$ | **0 false alarms** |
| **Average Decision Latency** | $< 3\text{s}$ | **~0.15s (Rules) / ~1.8s (End-to-End Vision)** |

Detailed per-document predictions are logged in [`eval/results/eval_summary.md`](eval/results/eval_summary.md).

---

## 9. Important Disclaimer

Mig_Guard is an informational decision-support and fraud-awareness tool. It does not replace formal verification with the **Bureau of Manpower, Employment and Training (BMET)**, the **Overseas Employment Platform (oep.gov.bd)**, or the **Ministry of Expatriates' Welfare and Overseas Employment**. Users are always advised to verify recruiting agency licenses directly at BMET or by calling the Probash Bondhu Call Center at **16135** before handing over money or passports.
