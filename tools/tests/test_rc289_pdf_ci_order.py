"""RC289: a PDF inspection gate must not execute before its dependency exists.

The real manuals and their embedded images remain an obligatory validation;
missing PyMuPDF is a CI provisioning error, not a reason to skip the test.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_PATH = ROOT / '.github/workflows/ci.yml'
PROVISION = 'RC289 provision PyMuPDF before manual PDF contracts'
EARLY_GATES = (
    'RC287 answer borders, floating format tabs, gradient schema and navigation contracts before npm',
    'RC286 portable session, rich thumbnails and manual visual contracts before npm',
)
INSTALL = "'pymupdf==1.26.7'"


def validate_provisioning_order(workflow: str) -> None:
    marker = '- name: ' + PROVISION
    if workflow.count(marker) != 1:
        raise ValueError('RC289 PDF dependency provision step must occur exactly once')
    start = workflow.index(marker)
    first_gate = min(workflow.index('- name: ' + item) for item in EARLY_GATES)
    if start >= first_gate:
        raise ValueError('PDF reader is installed after a test that imports fitz')
    section = workflow[start:first_gate]
    if INSTALL not in section or 'python3 -m pip install' not in section:
        raise ValueError('PDF inspector wheel is not pinned and installed before inspection')
    if "python3 -c 'import fitz;" not in section:
        raise ValueError('PDF inspector availability is not checked after installation')
    if 'python3 -m unittest tools.tests.test_rc289_pdf_ci_order -q' not in section:
        raise ValueError('PDF dependency ordering contract is no longer exercised in CI')
    for item in EARLY_GATES:
        if workflow.count('- name: ' + item) != 1:
            raise ValueError('missing/duplicated existing PDF-dependent manual quality gate')
    if 'python3 -m unittest tools.tests.test_rc287_result_formatting -q' not in workflow:
        raise ValueError('illustrated manual PDF validation must not be bypassed')
    if 'python3 -m unittest tools.tests.test_rc286_authoring_manuals -q' not in workflow:
        raise ValueError('manual build and embedded image validation must not be bypassed')
    if 'QUORIVIO_MANUAL_OUTPUT_DIR=/tmp/quorivio-manual-build python3 -m unittest tools.tests.test_rc284_manual_pdf_gallery -q' not in workflow:
        raise ValueError('fresh live screenshots and figure integration tests must remain active')


class RC289PdfCIOrder(unittest.TestCase):
    def test_ci_provisions_reader_before_early_pdf_gates(self):
        validate_provisioning_order(CI_PATH.read_text())

    def test_earlier_pdf_manual_contracts_remain_strict(self):
        for filename in ('test_rc287_result_formatting.py', 'test_rc286_authoring_manuals.py', 'test_rc284_manual_pdf_gallery.py'):
            source = (ROOT / 'tools/tests' / filename).read_text()
            self.assertIn('import fitz', source)
            self.assertIn('get_image_info()', source)

    def test_negative_provisioning_removed_fails(self):
        original = CI_PATH.read_text()
        with self.assertRaisesRegex(ValueError, 'pinned and installed'):
            validate_provisioning_order(original.replace(INSTALL, "'other-package==1.0'"))

    def test_negative_provisioning_moved_after_gates_fails(self):
        original = CI_PATH.read_text()
        a = original.index('      - name: ' + PROVISION)
        b = original.index('      - name: ' + EARLY_GATES[0])
        section = original[a:b]
        candidate = original[:a] + original[b:]
        at = candidate.index('      - name: ' + EARLY_GATES[1])
        candidate = candidate[:at] + section + candidate[at:]
        with self.assertRaisesRegex(ValueError, 'after a test'):
            validate_provisioning_order(candidate)

    def test_negative_pdf_inspection_removed_fails(self):
        original = CI_PATH.read_text()
        altered = original.replace('python3 -m unittest tools.tests.test_rc287_result_formatting -q',
                                   'python3 -m unittest tools.tests.test_rc287_other -q')
        with self.assertRaisesRegex(ValueError, 'must not be bypassed'):
            validate_provisioning_order(altered)


if __name__ == '__main__':
    unittest.main()
