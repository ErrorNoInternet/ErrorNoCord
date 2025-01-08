import unittest

import utils


class TestFilterSecrets(unittest.TestCase):
    def test_filter_secrets(self):
        secret = "PLACEHOLDER_TOKEN"
        self.assertFalse(
            secret in utils.filter_secrets(f"HELLO{secret}WORLD", {"TOKEN": secret})
        )
        self.assertFalse(secret in utils.filter_secrets(secret, {"TOKEN": secret}))
        self.assertFalse(
            secret in utils.filter_secrets(f"123{secret}", {"TOKEN": secret})
        )
        self.assertFalse(
            secret in utils.filter_secrets(f"{secret}{secret}", {"TOKEN": secret})
        )
        self.assertFalse(
            secret in utils.filter_secrets(f"{secret}@#(*&*$)", {"TOKEN": secret})
        )
