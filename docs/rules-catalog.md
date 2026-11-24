# Red-Flag Rules Catalog (`R01`–`R15`)

Mig_Guard combines multimodal extraction with 15 deterministic Python rules (`backend/app/rules/checks.py` and `catalog.yaml`). Every triggered rule links directly to an evidence snippet from the worker's document.

| Rule ID | Title | Severity | Weight | Why It Matters |
| :--- | :--- | :---: | :---: | :--- |
| `R01_NO_WRITTEN_CONTRACT` | No formal written contract | High | 25 | Chat messages and social posts are not legally enforceable employment contracts[cite: 2]. |
| `R02_NON_WORK_VISA` | Visit or tourist visa offered for work | High | 30 | Working on a tourist/visit visa makes the worker undocumented and vulnerable to arrest or trafficking[cite: 2]. |
| `R03_CASH_OR_UNSPECIFIED_FEE` | Cash-only fee or no official receipt | High | 20 | Cash payments without bank records or receipts leave workers with no proof of payment[cite: 2]. |
| `R04_HIGH_RISK_SCAM_PATTERN` | High-risk scam compound pattern | High | 35 | Online/crypto/data-entry jobs in high-risk border destinations match documented trafficking indicators[cite: 2]. |
| `R05_UNREALISTIC_SALARY` | Unrealistic salary for role and country | High | 20 | Abnormally high pay is classic scam bait; abnormally low pay signals wage exploitation[cite: 2]. |
| `R06_MISSING_CRITICAL_CLAUSES` | Critical contract clauses missing | Medium | 15 | Missing salary, hours, accommodation, or return ticket terms allow post-arrival abuse[cite: 2]. |
| `R07_MISSING_AGENCY_LICENSE` | No valid BMET Recruiting License (RL) | High | 20 | Unlicensed sub-agents operate outside government oversight[cite: 2]. |
| `R08_SIGN_ON_ARRIVAL` | Contract to be signed only on arrival | High | 25 | Exposes workers to contract substitution with lower wages after reaching the destination[cite: 2]. |
| `R09_PASSPORT_RETENTION` | Passport retention clause | High | 25 | Confiscating a worker's passport restricts freedom of movement and is a trafficking indicator[cite: 2]. |
| `R10_SALARY_DEDUCTION_DEBT_BOND` | Salary deduction or debt-bondage clause | High | 25 | Deducting visa or travel costs from monthly wages traps workers in debt bondage[cite: 2]. |
| `R11_PRESSURE_TACTICS` | Urgency or pressure tactics | Medium | 15 | "Pay today" or "limited seats" pressures workers into paying before verifying documents[cite: 2]. |
| `R12_PERSONAL_MOBILE_PAYMENT` | Payment to personal mobile money / pre-visa | High | 25 | Sending fees to personal bKash/Nagad numbers or before visa verification carries high fraud risk[cite: 2]. |
| `R13_SOCIAL_MEDIA_ONLY_NO_OFFICE` | Contact only via social media, no office | Medium | 15 | Recruiters without a verifiable physical office are difficult to trace[cite: 2]. |
| `R14_TOO_GOOD_TO_BE_TRUE_BUNDLE` | Free visa + free ticket + high pay bundle | High | 25 | Zero upfront cost combined with unusually high pay and no qualifications is a common trafficking lure[cite: 2]. |
| `R15_UNVERIFIABLE_EMPLOYER` | Employer name or address unverifiable | Medium | 15 | Missing employer identity or workplace address prevents pre-departure verification[cite: 2]. |
