"""
CLI Smoke Tests

Verifies that CLI commands work correctly after the restructure.
"""

import shutil
import subprocess
import sys

import pytest


def test_gptc_help():
    """Test gptc --help works."""
    executable = shutil.which("gptc")
    assert executable is not None, "gptc console script is not installed"
    result = subprocess.run(
        [executable, "--help"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


@pytest.mark.parametrize(
    "mode",
    ["api", "gui", "client", "mcp", "auth", "dev", "systray", "tray", "pa"],
)
def test_gptc_mode_help(mode):
    """Each gptc mode exposes help without starting its service."""
    executable = shutil.which("gptc")
    assert executable is not None, "gptc console script is not installed"
    result = subprocess.run(
        [executable, mode, "--help"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()


def test_gptc_no_args():
    """Test gptc with no arguments shows usage."""
    result = subprocess.run(
        [sys.executable, "-c", "import gptc.cli"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Should not crash on import
    assert result.returncode == 0


def test_gpt_computer_help():
    """Test gpt-computer --help works."""
    _assert_console_help("gpt-computer")


@pytest.mark.parametrize("command", ["ge", "bench"])
def test_secondary_console_script_help(command):
    """Public aliases and the benchmark command expose help."""
    _assert_console_help(command)


def _assert_console_help(command):
    executable = shutil.which(command)
    assert executable is not None, f"{command} console script is not installed"
    result = subprocess.run(
        [executable, "--help"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "usage" in result.stdout.lower()


def test_mcp_and_tray_entrypoint_targets_import():
    """Standalone server entry-point targets import without starting services."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from gpt_computer.interfaces.mcp.server import main as mcp_main; "
            "from gptc.tray import _tray_main; "
            "assert callable(mcp_main) and callable(_tray_main)",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr


def test_codemap_help():
    """Test codemap CLI works."""
    result = subprocess.run(
        [sys.executable, "-m", "gpt_computer.analysis.codemap.cli", "--help"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0


def test_interfaces_cli_import():
    """CLI imports must not initialize the legacy AI runtime."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; "
            "from gpt_computer.interfaces.cli import app; "
            "assert 'gpt_computer.core.ai' not in sys.modules; "
            "assert 'openai' not in sys.modules; "
            "print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_api_app_import():
    """Test that the FastAPI app can be imported."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from gpt_computer.interfaces.api import app; print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout
