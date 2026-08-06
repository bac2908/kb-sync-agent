import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from src.api import create_app

POLICY_URL = "https://example.org/clinical-policy/model-output-review"


def evaluation_payload(include_citation: bool = True) -> dict:
    evidence_text = (
        "Every AI generated answer requires clinician review before use in a "
        "clinical workflow."
    )
    citation = f" {POLICY_URL}" if include_citation else ""
    return {
        "case_id": "SYNTH-CASE-001",
        "question": "What review is required before this output can be used?",
        "answer": f"{evidence_text}{citation}",
        "evidence": [
            {
                "text": evidence_text,
                "source_url": POLICY_URL,
                "source_title": "Synthetic model-output review policy",
            }
        ],
    }


class ClinicalApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "review.db"
        app = create_app(f"sqlite:///{database_path.as_posix()}")
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.temp_directory.cleanup()

    def test_health_and_clinical_review_workflow(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        created = self.client.post("/v1/evaluations", json=evaluation_payload())
        self.assertEqual(created.status_code, 201)
        created_data = created.json()
        self.assertEqual(created_data["automated_status"], "ready_for_clinical_review")
        self.assertEqual(created_data["review_status"], "pending")

        listed = self.client.get("/v1/evaluations", params={"review_status": "pending"})
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

        reviewed = self.client.patch(
            f"/v1/evaluations/{created_data['id']}/review",
            json={
                "decision": "approved",
                "reviewer": "clinician-demo",
                "notes": "Synthetic workflow test only.",
            },
        )
        self.assertEqual(reviewed.status_code, 200)
        self.assertEqual(reviewed.json()["review_status"], "approved")

    def test_blocked_output_cannot_be_approved(self):
        created = self.client.post(
            "/v1/evaluations", json=evaluation_payload(include_citation=False)
        )
        self.assertEqual(created.status_code, 201)
        created_data = created.json()
        self.assertEqual(created_data["automated_status"], "blocked")

        reviewed = self.client.patch(
            f"/v1/evaluations/{created_data['id']}/review",
            json={
                "decision": "approved",
                "reviewer": "clinician-demo",
                "notes": "Should be rejected by the API.",
            },
        )
        self.assertEqual(reviewed.status_code, 409)

    def test_case_identifier_rejects_free_text(self):
        payload = evaluation_payload()
        payload["case_id"] = "Patient name: Example Person"

        response = self.client.post("/v1/evaluations", json=payload)

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
