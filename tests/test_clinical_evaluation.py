import unittest

from src.clinical_evaluation import EvidenceChunk, evaluate_answer

POLICY_URL = "https://example.org/clinical-policy/model-output-review"


class ClinicalEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.evidence = [
            EvidenceChunk(
                text=(
                    "Every AI generated answer requires clinician review before "
                    "use in a clinical workflow."
                ),
                source_url=POLICY_URL,
                source_title="Synthetic model-output review policy",
            )
        ]

    def test_grounded_answer_is_ready_for_clinical_review(self):
        answer = (
            "Every AI generated answer requires clinician review before use in a "
            f"clinical workflow. {POLICY_URL}"
        )

        result = evaluate_answer(answer, self.evidence)

        self.assertEqual(result.automated_status, "ready_for_clinical_review")
        self.assertEqual(result.blocking_reasons, [])
        self.assertTrue(result.requires_clinician_review)
        self.assertEqual(result.metrics.citation_precision, 1.0)

    def test_missing_citation_blocks_answer(self):
        result = evaluate_answer(self.evidence[0].text, self.evidence)

        self.assertEqual(result.automated_status, "blocked")
        self.assertIn("missing_source_citation", result.blocking_reasons)

    def test_unknown_citation_blocks_answer(self):
        answer = f"{self.evidence[0].text} https://example.org/unknown"

        result = evaluate_answer(answer, self.evidence)

        self.assertIn("citation_not_in_retrieved_evidence", result.blocking_reasons)
        self.assertEqual(result.metrics.citation_precision, 0.0)

    def test_unsafe_certainty_language_is_flagged(self):
        answer = f"This is a guaranteed cure. {POLICY_URL}"

        result = evaluate_answer(answer, self.evidence)

        self.assertIn("unsafe_certainty_language", result.blocking_reasons)
        self.assertIn("guaranteed cure", result.safety_flags)


if __name__ == "__main__":
    unittest.main()
