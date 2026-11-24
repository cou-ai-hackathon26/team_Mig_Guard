# AI Usage Log

This document records all AI coding tools, language models, APIs, and automated assistance used during the development of **Mig_Guard** for the CoU AI Hackathon 2026, in compliance with Rule 9, Rule 10, and Rule 16.

---

## 1. Summary of AI Tools & Models

| Tool / Model | Provider | Scope of Use | Disclosed in README |
|---|---|---|:---:|
| **Claude 3.5 Sonnet / 3.7 Sonnet** | Anthropic | Architecture drafting, deterministic rules logic, schema design, evaluation set creation | Yes |
| **Gemini 1.5 Pro / Flash** | Google | Multimodal document extraction, transcription testing, Bengali OCR validation | Yes |
| **GitHub Copilot / Cursor** | GitHub / Anysphere | Backend endpoint scaffolding, test authoring, frontend React components | Yes |

---

## 2. Running Log by Phase

### Phase 0: Planning & Ideation (19–20 Nov 2026)
- **Tool:** Claude 3.5 Sonnet
- **Scope:** Assistance in drafting the problem statement, wireframing user journeys for low-literacy workers, researching official migration circulars from BMET and ILO, and designing the 15-rule catalog structure.
- **Human Verification:** All legal provisions, fee caps, and penalty provisions were checked against the Bangladesh Overseas Employment and Migrants Act 2013 and official circulars. No project code was written.

### Phase 1: Skeleton & First Working Slice (21 Nov 2026)
- **Tool:** GitHub Copilot, Claude 3.5 Sonnet
- **Scope:** Scaffolding FastAPI routes (`/api/health`, `/api/analyze`), creating the initial `offer_extraction.json` schema, writing the first 10 pure-function rule checks in `checks.py`, and authoring initial pytest unit tests.
- **Human Verification:** Extraction schemas and rule weights were reviewed and adjusted by team members to prevent false reassurance.

### Phase 2: Full Pipeline, Rules Engine & Evaluation (22 Nov 2026)
- **Tool:** Copilot, Claude 3.5 Sonnet
- **Scope:** Implementing the remaining red-flag rules (R10–R15), generating 20 synthetic test documents in `eval/test_docs/` (8 legitimate, 12 scam offers) in English and Bangla, implementing `eval/run_eval.py`, and structuring curated knowledge base passages.
- **Human Verification:** All synthetic documents were created from scratch without real PII. Evaluation labels were audited by hand.

### Phase 3 & Final Day: Audio, Hardening & Documentation (23–24 Nov 2026)
- **Tool:** Claude 3.7 Sonnet, Copilot
- **Scope:** Drafting technical documentation (`docs/architecture.md`, `docs/rules-catalog.md`, `docs/privacy-and-safety.md`, `docs/evaluation-report.md`, `docs/demo-script.md`, `docs/submission-text.md`), completing the comprehensive `README.md`, and writing the automated data validator (`scripts/validate_data.py`).
- **Human Verification:** Every link, benchmark figure, and helpline number in `SOURCES.md` and `helplines.json` was cross-checked against official government portals.
