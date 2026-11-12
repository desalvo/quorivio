"""Guard the PR Git ancestry needed by the unmodified Gitleaks secret scan."""
from pathlib import Path
import unittest
import re

ROOT = Path(__file__).resolve().parents[2]

class RCPullRequestGitleaksHistory(unittest.TestCase):
 def test_quality_checkout_has_full_pr_history(self):
  text = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
  found = re.search(r'^      - uses: actions/checkout@v(?:4|7)\s*
  self.assertIn('with: {persist-credentials: false, fetch-depth: 0}', text[checkout:checkout+150])
  self.assertIn('gitleaks/gitleaks-action@v2', text)
  self.assertLess(checkout, text.index('gitleaks/gitleaks-action@v2'))

if __name__ == '__main__': unittest.main()
, text, re.MULTILINE)
  self.assertIsNotNone(found, 'Quality gate requires a supported pinned checkout action')
  checkout = found.start()
  self.assertIn('with: {persist-credentials: false, fetch-depth: 0}', text[checkout:checkout+150])
  self.assertIn('gitleaks/gitleaks-action@v2', text)
  self.assertLess(checkout, text.index('gitleaks/gitleaks-action@v2'))

if __name__ == '__main__': unittest.main()
