
"""
validate_data.py
Checks that all official data files, rules catalog, and knowledge base files
are complete, well-formed, and documented with sources.
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "backend" / "app" / "data"
KB_DIR = ROOT_DIR / "backend" / "app" / "rag" / "kb"

REQUIRED_DATA_FILES = [
    "licensed_agencies.json",
    "fee_caps.json",
    "salary_benchmarks.json",
    "high_risk_patterns.json",
    "helplines.json",
    "SOURCES.md",
]

PLACEHOLDER_TOKENS = [
    "VERIFY_OFFICIAL",
    "SAMPLE_REPLACE",
    "<paste-url>",
    "<YYYY-MM-DD>",
    "<URL>",
    "<Date>",
]


def validate() -> int:
    print("=== Mig_Guard Data & Source Verification ===\n")
    warnings = 0

    for filename in REQUIRED_DATA_FILES:
        path = DATA_DIR / filename
        if not path.exists():
            print(f"[MISSING] {path}")
            warnings += 1
            continue

        text = path.read_text(encoding="utf-8")
        if filename.endswith(".json"):
            try:
                json.loads(text)
                print(f"[OK JSON] {filename}")
            except json.JSONDecodeError as exc:
                print(f"[INVALID JSON] {filename}: {exc}")
                warnings += 1
    # 3. Check rules catalog.yaml
    catalog_path = RULES_DIR / "catalog.yaml"
    if not catalog_path.exists():
        errors.append("Missing catalog.yaml")
    else:
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog = yaml.safe_load(f)
            rules_to_check = {}
            if "rules" in catalog and isinstance(catalog["rules"], dict):
                rules_to_check.update(catalog["rules"])
            for rid, meta in catalog.items():
                if rid not in {"verdicts", "rules"} and isinstance(meta, dict):
                    rules_to_check[rid] = meta
            rule_count = len(rules_to_check)
            print(f"  [OK] catalog.yaml valid YAML with {rule_count} rules")
            if rule_count < 15:
                warnings.append(f"Catalog has only {rule_count}/15 expected rules")
            for rid, meta in rules_to_check.items():
                for field in ["severity", "weight", "title_en", "title_bn", "explanation_en", "explanation_bn", "question_en", "question_bn"]:
                    if field not in meta:
                        errors.append(f"Rule {rid} missing required field '{field}'")
        except Exception as e:
            errors.append(f"Invalid YAML in catalog.yaml: {e}")

        found_tokens = [tok for tok in PLACEHOLDER_TOKENS if tok in text]
        if found_tokens:
            print(f"  -> [WARNING] Unverified placeholders in {filename}: {', '.join(found_tokens)}")
            warnings += 1

    kb_files = sorted(KB_DIR.glob("*.md")) if KB_DIR.exists() else []
    passage_count = 0
    kb_placeholders = 0
    for kb_file in kb_files:
        kb_text = kb_file.read_text(encoding="utf-8")
        passage_count += sum(1 for line in kb_text.splitlines() if line.startswith("## "))
        if any(tok in kb_text for tok in PLACEHOLDER_TOKENS):
            kb_placeholders += 1

    print(f"\n[KB CHECK] {len(kb_files)} markdown files, {passage_count} curated passages (target: 20-30).")
    if kb_placeholders:
        print(f"  -> [WARNING] {kb_placeholders} KB file(s) still contain <URL> or <Date> placeholders.")
        warnings += 1

    print(f"\nVerification finished with {warnings} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
