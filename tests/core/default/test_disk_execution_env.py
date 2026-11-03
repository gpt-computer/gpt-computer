import tempfile
import unittest

from unittest.mock import MagicMock, patch

from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv

# from gpt_computer.core.default.git_version_manager import GitVersionManager
from gpt_computer.core.default.paths import ENTRYPOINT_FILE
from gpt_computer.core.files_dict import FilesDict


class TestOnDiskExecutionEnv(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env = DiskExecutionEnv()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_successful_execution(self):
        entrypoint_content = """
        python -m venv venv
        source venv/bin/activate
        python script.py
        """
        code = {
            ENTRYPOINT_FILE: entrypoint_content,
            "script.py": "print('This is a test script')",
        }
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value.wait.return_value = 0
            process = self.env.upload(FilesDict(code)).popen(f"bash {ENTRYPOINT_FILE}")
            self.assertIsNotNone(process)
            mock_popen.assert_called_once()

    def test_missing_entrypoint(self):
        code = {"script.py": "print('This is a test script')"}
        p = self.env.upload(FilesDict(code)).popen(f"bash {ENTRYPOINT_FILE}")
        p.communicate()
        assert p.returncode != 0

    def test_keyboard_interrupt_handling(self):
        entrypoint_content = """
        python script.py
        """
        code = {
            ENTRYPOINT_FILE: entrypoint_content,
            "script.py": "print('This is a test script')",
        }
        with patch("subprocess.Popen") as mock_popen:
            with patch(
                "gpt_computer.execution.local._kill_process_tree"
            ) as mock_kill_tree:
                mock_process = MagicMock()
                mock_process.communicate.side_effect = [KeyboardInterrupt, ("", "")]
                mock_process.returncode = 0
                mock_popen.return_value = mock_process
                stdout_full, stderr_full, returncode = self.env.upload(
                    FilesDict(code)
                ).run(f"bash {ENTRYPOINT_FILE}")
                mock_kill_tree.assert_called_once_with(mock_process)

    def test_execution_with_output(self):
        entrypoint_content = """
        python script.py
        """
        code = {
            ENTRYPOINT_FILE: entrypoint_content,
            "script.py": "import sys; print('Out'); sys.stderr.write('Error')",
        }
        with patch("subprocess.Popen") as mock_popen:
            process = MagicMock()
            process.wait.return_value = 0
            process.communicate.return_value = (b"Out\n", b"Error\n")
            mock_popen.return_value = process
            process = self.env.upload(FilesDict(code)).popen(f"bash {ENTRYPOINT_FILE}")
            stdout, stderr = process.communicate()
            self.assertEqual(stdout, b"Out\n")
            self.assertEqual(stderr, b"Error\n")


if __name__ == "__main__":
    unittest.main()
