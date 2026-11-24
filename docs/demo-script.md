# 3-Minute Live Demo & Backup Video Script

1. **0:00–0:20 | The Problem (Member C / Team):**
   - Prospective Bangladeshi migrant workers often receive informal offers on WhatsApp or paper without contracts (~75% receive no contract before departure; ~80% go through unauthorized sub-agents)[cite: 2]. Existing tools act *after* harm happens; Mig_Guard checks offers *before* payment or departure[cite: 2].
2. **0:20–1:25 | Live Demo 1 — Scam-Pattern Offer (Member B):**
   - Capture/upload a synthetic scam chat screenshot (e.g., Cambodia crypto/data-entry job on a visit visa with personal bKash payment)[cite: 2].
   - Show the **Danger** verdict, highlighted evidence snippets from the document, questions to ask the agent, official helplines, and play the **Bangla voice readout**[cite: 2].
3. **1:25–2:10 | Live Demo 2 — Incomplete Offer & Never-Says-Safe (Member B):**
   - Upload a legitimate-looking offer missing key clauses[cite: 2].
   - Highlight that Mig_Guard **never says "safe"**—missing items appear explicitly under **Unverifiable** alongside questions to ask before signing[cite: 2].
4. **2:10–2:45 | Architecture, Rules Engine & Evaluation (Member A & Member C):**
   - Briefly show how PII is masked first, how the 15 deterministic Python rules + official BMET/fee data drive the score (not a bare prompt wrapper), and show the evaluation results table (`docs/evaluation-report.md`)[cite: 2].
5. **2:45–3:00 | Privacy & Closing:**
   - Emphasize zero document storage (processed in memory and discarded immediately) and pre-departure protection for workers[cite: 2].
