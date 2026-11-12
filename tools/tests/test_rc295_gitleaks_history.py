"""Guard the PR Git ancestry needed by the unmodified Gitleaks secret scan."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class RCPullRequestGitleaksHistory(unittest.TestCase):
 def test_quality_checkout_has_full_pr_history(self):
  text = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
  checkout = text.index('      - uses: actions/checkout@v4')
  self.assertIn('with: {persist-credentials: false, fetch-depth: 0}', text[checkout:checkout+150])
  self.assertRegex(text, r'gitleaks/gitleaks-action@v(?:2|3)\b')
  self.assertLess(checkout, text.index('gitleaks/gitleaks-action@v'))

if __name__ == '__main__': unittest.main()
