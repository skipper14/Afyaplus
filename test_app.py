import json
import unittest

import app


class TriageEngineTests(unittest.TestCase):
    def test_schema_enforcement(self):
        payload = app.ensure_schema(
            {
                "is_critical_emergency": True,
                "detected_symptoms": ["chest pain", "shortness of breath"],
                "clinical_reasoning_summary": "High-risk symptoms detected.",
                "routing_destination": "emergency_room",
            }
        )
        self.assertTrue(payload["is_critical_emergency"])
        self.assertEqual(payload["routing_destination"], "emergency_room")
        self.assertIn("chest pain", payload["detected_symptoms"])

    def test_fallback_output(self):
        result = app.build_rule_based_fallback("I have a mild headache and sore throat")
        self.assertFalse(result["is_critical_emergency"])
        self.assertEqual(result["routing_destination"], "urgent_care")

    def test_json_normalization(self):
        parsed = app.normalize_json_response('{"is_critical_emergency": false, "detected_symptoms": ["rash"], "clinical_reasoning_summary": "Mild concern.", "routing_destination": "telehealth"}')
        self.assertEqual(parsed["routing_destination"], "telehealth")


if __name__ == "__main__":
    unittest.main()
