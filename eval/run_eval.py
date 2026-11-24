import csv
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.rules.engine import evaluate_rules  # noqa: E402

EVAL_DIR = ROOT_DIR / "eval"
LABELS_PATH = EVAL_DIR / "labels.csv"
RESULTS_PATH = EVAL_DIR / "results" / "eval_summary.md"


def find_doc_path(doc_id: str, category: str) -> Path:
    return EVAL_DIR / "test_docs" / category / f"{doc_id}.json"


def run():
    rows = []
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    report_lines = [
        "# Evaluation Results (Synthetic Offer Set)",
        "",
        "| Doc ID | Category | Expected | Predicted | Missed Flags | False Alarms |",
        "| :--- | :--- | :---: | :---: | :--- | :--- |",
    ]

    total_expected = 0
    total_caught = 0
    legit_false_alarms = 0

    for row in rows:
        doc_id = row["doc_id"].strip()
        category = row["category"].strip()
        raw_expected = row["expected_flags"].strip()
        expected = set() if raw_expected == "NONE" or not raw_expected else set(raw_expected.split(";"))

        doc_path = find_doc_path(doc_id, category)
        if not doc_path.exists():
            print(f"[WARNING] Missing file: {doc_path}")
            continue

        with open(doc_path, "r", encoding="utf-8") as df:
            doc_data = json.load(df)

        result = evaluate_rules(doc_data)
        predicted = {flag["rule_id"] for flag in result["flags"]}

        caught = expected & predicted
        missed = sorted(expected - predicted)
        false_positives = sorted(predicted - expected)

        total_expected += len(expected)
        total_caught += len(caught)
        if category == "legit":
            legit_false_alarms += len(false_positives)

        missed_str = ", ".join(missed) if missed else "-"
        fp_str = ", ".join(false_positives) if false_positives else "-"
        report_lines.append(
            f"| `{doc_id}` | {category} | {len(expected)} | {len(predicted)} | {missed_str} | {fp_str} |"
        )

    recall = (total_caught / total_expected * 100) if total_expected else 0.0
    report_lines.extend([
        "",
        "## Summary Metrics",
        f"- **Scam Red-Flag Recall:** {total_caught}/{total_expected} ({recall:.1f}%)",
        f"- **False Alarms on Legitimate Offers:** {legit_false_alarms}",
        "- **Note:** Evaluated on a small synthetic dataset of Bangla and English offers; no real worker documents were used.",
    ])

    output_text = "\n".join(report_lines) + "\n"
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as out:
        out.write(output_text)

    print(output_text)
    print(f"Saved evaluation report to {RESULTS_PATH}")


if __name__ == "__main__":
    run()
