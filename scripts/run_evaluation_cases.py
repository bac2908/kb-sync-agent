import json
from pathlib import Path

from src.clinical_evaluation import EvidenceChunk, evaluate_answer

CASES_PATH = Path("data/evaluation/oncology_rag_cases.json")


def main() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    passed = 0

    for case in cases:
        evidence = [EvidenceChunk(**item) for item in case["evidence"]]
        result = evaluate_answer(case["answer"], evidence)
        expected = case["expected_automated_status"]
        matches = result.automated_status == expected
        passed += int(matches)

        print(
            f"[{case['case_id']}] expected={expected} "
            f"actual={result.automated_status} pass={matches}"
        )
        if result.blocking_reasons:
            print(f"  blocking_reasons={', '.join(result.blocking_reasons)}")

    print(f"\nEvaluation cases passed: {passed}/{len(cases)}")
    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
