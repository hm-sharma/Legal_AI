import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.main import (
    read_root,
    get_sample_contracts_info,
    analyze_sample_contract,
    reevaluate_role,
    get_page_image
)
from backend.app.schemas import AnalyzeSampleRequest, ReevaluateRoleRequest

class TestLegalDocumentAnalyzer(unittest.TestCase):

    def test_root_endpoint(self):
        res = read_root()
        self.assertEqual(res["status"], "online")
        self.assertEqual(res["version"], "1.0.0")

    def test_get_samples(self):
        samples = get_sample_contracts_info()
        self.assertGreaterEqual(len(samples), 2)
        self.assertEqual(samples[0].sample_id, "msa_draft")

    def test_analyze_sample_msa(self):
        req = AnalyzeSampleRequest(sample_id="msa_draft", role="Service Provider")
        audit_res = analyze_sample_contract(req)
        self.assertIsNotNone(audit_res.overall_contract_score)
        self.assertEqual(audit_res.selected_role, "Service Provider")
        self.assertGreater(len(audit_res.clauses), 0)

        # Verify bounding box present on identified spans
        first_span = audit_res.clauses[0].identified_spans[0]
        self.assertIsNotNone(first_span.bbox)
        self.assertGreater(first_span.bbox.x0, 0)
        self.assertGreater(first_span.bbox.y0, 0)

    def test_reevaluate_role_perspective(self):
        # 1. Analyze as Service Provider (expect low safety score / high risk)
        req_provider = AnalyzeSampleRequest(sample_id="msa_draft", role="Service Provider")
        res_provider = analyze_sample_contract(req_provider)
        score_provider = res_provider.overall_contract_score

        # 2. Reevaluate as Client / Buyer (expect higher safety score / low risk for client)
        req_client = ReevaluateRoleRequest(document_id="doc_sample_msa_draft", role="Client / Buyer")
        res_client = reevaluate_role(req_client)
        score_client = res_client.overall_contract_score

        self.assertNotEqual(score_provider, score_client)

    def test_get_page_image(self):
        img_data = get_page_image("doc_sample_msa_draft", 1)
        self.assertEqual(img_data["page_number"], 1)
        self.assertTrue(img_data["image_data_url"].startswith("data:image/png;base64,"))

if __name__ == "__main__":
    unittest.main()
