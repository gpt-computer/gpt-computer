"""Verify the built wheel contains and imports the migrated public packages."""

import subprocess
import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_built_wheel_installs_and_imports_outside_source_tree(tmp_path):
    wheel_dir = tmp_path / "wheels"
    install_dir = tmp_path / "installed"
    wheel_dir.mkdir()

    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(wheel_dir)],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    wheels = list(wheel_dir.glob("*.whl"))
    assert len(wheels) == 1, f"Expected one built wheel, found {wheels}"

    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--target",
            str(install_dir),
            "--no-deps",
            str(wheels[0]),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    script = """
import importlib
from pathlib import Path
import sys

install_dir = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(install_dir))
modules = (
    "gpt_computer.ai.client",
    "gpt_computer.agent",
    "gpt_computer.execution",
    "gpt_computer.infrastructure.files",
    "gpt_computer.interfaces.api",
    "gpt_computer.interfaces.cli",
    "gpt_computer.api",
    "gptc",
)
for name in modules:
    module = importlib.import_module(name)
    module_path = Path(module.__file__).resolve()
    assert module_path.is_relative_to(install_dir), (
        f"{name} loaded outside the installed wheel: {module_path}"
    )
"""
    subprocess.run(
        [sys.executable, "-I", "-c", script, str(install_dir)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
