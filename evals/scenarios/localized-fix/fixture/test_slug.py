import unittest

from slug import normalize_slug


class NormalizeSlugTest(unittest.TestCase):
    def test_trims_and_collapses_whitespace(self):
        self.assertEqual("hello-world", normalize_slug("  Hello   World  "))


if __name__ == "__main__":
    unittest.main()
