# Evaluation Results (Synthetic Offer Set)

| Doc ID | Category | Expected | Predicted | Missed Flags | False Alarms |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `legit_01_saudi_electrician` | legit | 0 | 0 | - | - |
| `legit_02_uae_chef_bn` | legit | 0 | 0 | - | - |
| `legit_03_malaysia_factory_en` | legit | 0 | 0 | - | - |
| `legit_04_singapore_domestic_bn` | legit | 0 | 0 | - | - |
| `legit_05_saudi_driver_bn` | legit | 0 | 0 | - | - |
| `legit_06_uae_security_en` | legit | 0 | 0 | - | - |
| `legit_07_malaysia_plantation_bn` | legit | 0 | 0 | - | - |
| `legit_08_qatar_construction_en` | legit | 0 | 0 | - | - |
| `scam_01_cambodia_crypto_chat` | scam | 12 | 12 | - | - |
| `scam_02_visit_visa_deduction_bn` | scam | 8 | 8 | - | - |
| `scam_03_laos_typing_telegram_en` | scam | 12 | 12 | - | - |
| `scam_04_myanmar_marketing_bn` | scam | 11 | 11 | - | - |
| `scam_05_dubai_tourist_visa_cash_en` | scam | 8 | 8 | - | - |
| `scam_06_malaysia_passport_seizure_bn` | scam | 10 | 10 | - | - |
| `scam_07_saudi_debt_bondage_en` | scam | 8 | 8 | - | - |
| `scam_08_cambodia_crypto_vip_bn` | scam | 12 | 12 | - | - |
| `scam_09_qatar_cash_only_urgent_bn` | scam | 8 | 8 | - | - |
| `scam_10_singapore_underpaid_deduction_en` | scam | 8 | 8 | - | - |
| `scam_11_thailand_border_forex_chat_en` | scam | 10 | 10 | - | - |
| `scam_12_malaysia_hand_to_hand_bn` | scam | 10 | 10 | - | - |

## Summary Metrics
- **Scam Red-Flag Recall:** 117/117 (100.0%)
- **False Alarms on Legitimate Offers:** 0
- **Note:** Evaluated on a small synthetic dataset of Bangla and English offers; no real worker documents were used.
