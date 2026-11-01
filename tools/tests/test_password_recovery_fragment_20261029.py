"""Safe SMTP one-time recovery links: no bearer in HTTP path/query."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from ci_password_recovery_postgres import extract_recovery_token


class ResetFragmentLink(unittest.TestCase):
    def setUp(self):
        self.token = 'A' * 43

    def test_fragment_link_parses_single_valid_bearer(self):
        self.assertEqual(extract_recovery_token('Click:\nhttps://quorivio.example/#reset_token=' + self.token + '\n'), self.token)

    def test_disposable_loopback_http_is_allowed_without_query_bearer(self):
        self.assertEqual(extract_recovery_token('http://127.0.0.1:8080/#reset_token=' + self.token), self.token)

    def test_query_link_legacy_not_issued_to_new_users(self):
        with self.assertRaises(AssertionError):
            extract_recovery_token('https://quorivio.example/?reset_token=' + self.token)

    def test_no_http_plaintext_or_other_fragment_fields(self):
        for link in ('http://quorivio.example/#reset_token=' + self.token,
                     'https://quorivio.example/path#reset_token=',
                     'https://quorivio.example/#reset_token=',
                     'https://quorivio.example/#reset_token=' + self.token + '&a=b',
                     'https://quorivio.example/#reset_token=invalid'):
            with self.subTest(url=link.split('#')[0]), self.assertRaises(AssertionError):
                extract_recovery_token(link if link.endswith('=') else link + self.token if link.endswith('#reset_token=') else link)

    def test_no_url_and_extra_query_are_rejected(self):
        for text in ('No recovery link',
                     'https://quorivio.example/?tracking=1#reset_token=' + self.token):
            with self.assertRaises(AssertionError):
                extract_recovery_token(text)


if __name__ == '__main__':
    unittest.main()
