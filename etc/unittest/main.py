import unittest

import gptc.version

from gptc.errors import VersionNotFoundError

DEFAULT_MESSAGES = [{"role": "user", "content": "Hello"}]


class TestGetLastProvider(unittest.TestCase):
    def test_get_latest_version(self):
        current_version = gptc.version.utils.current_version
        if current_version is not None:
            self.assertIsInstance(gptc.version.utils.current_version, str)
        try:
            self.assertIsInstance(gptc.version.utils.latest_version, str)
        except VersionNotFoundError:
            pass
