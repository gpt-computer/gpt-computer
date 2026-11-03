"""
Security Boundary Tests

Validates Execution Security Level A (directory-based restrictions).
These tests do not prove full OS-level isolation. Untrusted code execution
should remain disabled until Execution Security Level B is implemented.
"""

import os
import sys
import tempfile
import time

import pytest

from gpt_computer.execution import DiskExecutionEnv
from gpt_computer.infrastructure.files import FilesDict


class TestPathTraversal:
    """Test path traversal protection."""

    def test_push_rejects_parent_traversal(self):
        """Pushing a file with parent traversal must not write outside the project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = os.path.join(tmpdir, "project")
            outside_file = os.path.join(tmpdir, "outside.txt")
            env = DiskExecutionEnv(project)

            with pytest.raises(PermissionError):
                env.files.push(FilesDict({"../outside.txt": "escaped"}))

            assert not os.path.exists(outside_file)

    def test_push_rejects_absolute_path(self):
        """Pushing an absolute path must not write outside the project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = os.path.join(tmpdir, "project")
            outside_file = os.path.join(tmpdir, "outside.txt")
            env = DiskExecutionEnv(project)

            with pytest.raises(PermissionError):
                env.files.push(FilesDict({outside_file: "escaped"}))

            assert not os.path.exists(outside_file)

    @pytest.mark.skipif(
        sys.platform == "win32", reason="Symlink behavior differs on Windows"
    )
    def test_push_rejects_symlink_escape(self):
        """Pushing through a project symlink must not write outside the project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = os.path.join(tmpdir, "project")
            outside = os.path.join(tmpdir, "outside")
            os.makedirs(project)
            os.makedirs(outside)
            os.symlink(outside, os.path.join(project, "escape"))
            env = DiskExecutionEnv(project)

            with pytest.raises(PermissionError):
                env.files.push(FilesDict({"escape/outside.txt": "escaped"}))

            assert not os.path.exists(os.path.join(outside, "outside.txt"))

    @pytest.mark.skipif(
        sys.platform == "win32", reason="Symlink behavior differs on Windows"
    )
    def test_pull_rejects_symlink_escape(self):
        """Pulling files must not read through a symlink outside the project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = os.path.join(tmpdir, "project")
            os.makedirs(project)
            outside_file = os.path.join(tmpdir, "outside.txt")
            with open(outside_file, "w") as file:
                file.write("secret")
            os.symlink(outside_file, os.path.join(project, "external.txt"))
            env = DiskExecutionEnv(project)

            with pytest.raises(PermissionError):
                env.files.pull()

    def test_working_dir_containment(self):
        """Test that working directory is properly contained."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = DiskExecutionEnv(tmpdir)
            assert str(env.files.working_dir).startswith(tmpdir) or tmpdir in str(
                env.files.working_dir
            )


class TestSymlinkEscape:
    """Test symlink escape protection."""

    @pytest.mark.skipif(
        sys.platform == "win32", reason="Symlink behavior differs on Windows"
    )
    def test_symlink_resolution(self):
        """Test that symlinks are resolved properly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a symlink to /tmp
            link_path = os.path.join(tmpdir, "escape_link")
            try:
                os.symlink("/tmp", link_path)
            except OSError:
                pytest.skip("Cannot create symlink")

            # Verify realpath resolves the symlink
            resolved = os.path.realpath(link_path)
            assert (
                resolved == "/private/tmp"
                or resolved.startswith("/private/tmp")
                or resolved == "/tmp"
                or resolved.startswith("/tmp")
            )


class TestExecutionTimeout:
    """Test execution timeout behavior."""

    def test_timeout_terminates_process(self):
        """Timeouts interrupt commands even when they continuously emit output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = DiskExecutionEnv(tmpdir)
            source = (
                "import time\n"
                "while True:\n"
                "    print('tick', flush=True)\n"
                "    time.sleep(0.05)\n"
            )
            env.files.push(FilesDict({"infinite.py": source}))

            started = time.monotonic()
            with pytest.raises(TimeoutError):
                env.run(f'"{sys.executable}" infinite.py', timeout=1)
            assert time.monotonic() - started < 3

    @pytest.mark.skipif(
        os.name != "posix", reason="Process-group termination is POSIX-specific"
    )
    def test_timeout_terminates_descendants(self):
        """Timeouts kill descendants in the command's process group."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = DiskExecutionEnv(tmpdir)
            marker = os.path.join(tmpdir, "child-survived")
            child_code = (
                "import pathlib, time; time.sleep(2); "
                f"pathlib.Path({marker!r}).touch()"
            )
            parent_code = "\n".join(
                [
                    "import subprocess, sys, time",
                    f"subprocess.Popen([sys.executable, '-c', {child_code!r}])",
                    "while True:",
                    "    print('tick', flush=True)",
                    "    time.sleep(0.05)",
                ]
            )
            env.files.push(FilesDict({"infinite.py": parent_code}))

            with pytest.raises(TimeoutError):
                env.run(f'"{sys.executable}" infinite.py', timeout=1)

            time.sleep(2.2)
            assert not os.path.exists(marker)

    def test_normal_execution_completes(self):
        """Test that normal execution completes without timeout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = DiskExecutionEnv(tmpdir)
            env.files.push(FilesDict({"hello.py": "print('hello world')"}))

            stdout, stderr, returncode = env.run(
                f'"{sys.executable}" hello.py', timeout=10
            )
            assert "hello world" in stdout
            assert returncode == 0


class TestEnvironmentIsolation:
    """Test environment variable isolation."""

    def test_scrub_env_flag_exists(self):
        """Test that scrub_env parameter is documented."""
        # This is a documentation/contract test
        # Actual implementation would be in execution layer
        pass

    def test_network_allowed_flag_exists(self):
        """Test that network_allowed parameter is documented."""
        # This is a documentation/contract test
        pass


class TestPathResolution:
    """Test path resolution utilities."""

    def test_realpath_resolves_symlinks(self):
        """Test that os.path.realpath resolves symlinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            # Create symlink
            link = os.path.join(tmpdir, "link.txt")
            try:
                os.symlink(test_file, link)
            except OSError:
                pytest.skip("Cannot create symlink")

            # Verify realpath resolves to same path
            assert os.path.realpath(link) == os.path.realpath(test_file)

    def test_commonpath_containment(self):
        """Test that commonpath can verify containment."""
        import os.path

        allowed = "/tmp/project"
        inside = "/tmp/project/src/main.py"
        outside = "/etc/passwd"

        # Inside path should share commonpath with allowed
        assert os.path.commonpath([allowed, inside]) == allowed

        # Outside path should not share commonpath with allowed
        try:
            common = os.path.commonpath([allowed, outside])
            assert common != allowed
        except ValueError:
            pass  # Different drives on Windows
