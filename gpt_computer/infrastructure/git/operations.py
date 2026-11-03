"""
Git Operations

Git command wrappers for repository management.

Functions:
    is_git_installed: Check if git is available.
    is_git_repo: Check if a path is a git repository.
    init_git_repo: Initialize a git repository.
    has_uncommitted_changes: Check for uncommitted changes.
    filter_files_with_uncommitted_changes: Filter files with uncommitted changes.
    stage_files: Stage files in git.
    filter_by_gitignore: Filter files by gitignore.
    stage_uncommitted_to_git: Stage uncommitted files before overwrite.
"""

import logging
import shutil
import subprocess

from pathlib import Path
from typing import List

from gpt_computer.infrastructure.files.operations import FilesDict

logger = logging.getLogger(__name__)


def is_git_installed():
    return shutil.which("git") is not None


def is_git_repo(path: Path):
    return (
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).returncode
        == 0
    )


def init_git_repo(path: Path):
    subprocess.run(["git", "init"], cwd=path)


def has_uncommitted_changes(path: Path):
    return bool(
        subprocess.run(
            ["git", "diff", "--exit-code"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).returncode
        == 0
    )


def filter_files_with_uncommitted_changes(
    basepath: Path, files_dict: FilesDict
) -> List[Path]:
    files_with_diff = (
        subprocess.run(
            ["git", "diff", "--name-only"], cwd=basepath, stdout=subprocess.PIPE
        )
        .stdout.decode()
        .splitlines()
    )
    return [f for f in files_dict.keys() if f in files_with_diff]


def stage_files(path: Path, files: List[str]):
    subprocess.run(["git", "add", *files], cwd=path)


def filter_by_gitignore(path: Path, file_list: List[str]) -> List[str]:
    out = subprocess.run(
        ["git", "-C", ".", "check-ignore", "--no-index", "--stdin"],
        cwd=path,
        input="\n".join(file_list).encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    paths = out.stdout.decode().splitlines()
    return [f for f in file_list if f not in paths]


def stage_uncommitted_to_git(path, files_dict, improve_mode):
    # Check if there's a git repo and verify that there aren't any uncommitted changes
    if is_git_installed() and not improve_mode:
        if not is_git_repo(path):
            logger.info("Initializing an empty git repository")
            init_git_repo(path)

    if is_git_repo(path):
        modified_files = filter_files_with_uncommitted_changes(path, files_dict)
        if modified_files:
            logger.info(
                f"Staging the following uncommitted files before overwriting: {', '.join(modified_files)}"
            )
            stage_files(path, modified_files)
