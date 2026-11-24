# System Architecture & Pipeline Data Flow

Mig_Guard is designed as an explainable, privacy-first pipeline protecting prospective migrant workers from fraudulent recruitment offers before departure.

```
Phone Camera / Document Upload / Chat Screenshot / Pasted Text
                             |
                             v
1. INGEST & PRE-PROCESS      Clean image, resize, mask sensitive PII (passports, phone numbers)
                             |
                             v
2. READ & TRANSCRIBE         Multimodal vision model (Gemini/Claude) with Bengali + English OCR fallback
                             |
                             v
3. STRUCTURED EXTRACTION     Strict JSON schema extraction with confidence and source snippet per field
                             |
                             v
4. VERIFICATION CHECKS       Deterministic evaluation against official data:
                             - BMET RAIMS recruiting agency license verification
                             - Official government recruitment fee caps (Emigration Act 2013)
                             - Country-specific salary benchmarks & wage floors
                             - High-risk destination & scam compound pattern matching
                             |
                             v
5. GROUNDED EXPLANATION      Retrieval-Augmented Generation (RAG) over 33 curated legal & rights passages
                             |
                             v
6. DETERMINISTIC SCORING     Rule weights aggregated to: Danger, Caution, or Fewer Concerns Found (Never Safe)
                             |
                             v
7. MULTIMODAL DELIVERY       Bangla audio synthesis (TTS), highlighted evidence, missing clauses,
                             questions to ask the recruiter, and official emergency helplines
```

## Core Principles

1. **Deterministic Rule Engine:** LLMs transcribe and extract, but verdicts are governed strictly by deterministic Python rules (`backend/app/rules/`).
2. **Never-Says-Safe:** The most favorable verdict is "Fewer concerns found — verify with official authorities." Missing or unreadable clauses are cataloged as `unverifiable`.
3. **Evidence Grounding:** Every triggered red flag links directly to verbatim snippet evidence from the uploaded document.
4. **Zero Document Storage:** All documents are processed strictly in memory and immediately discarded.
