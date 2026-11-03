"""
Paths Module

Defines file system paths used by the agent system.

Constants:
    META_DATA_REL_PATH, MEMORY_REL_PATH, CODE_GEN_LOG_FILE, DEBUG_LOG_FILE,
    ENTRYPOINT_FILE, ENTRYPOINT_LOG_FILE, PREPROMPTS_PATH

Functions:
    memory_path, metadata_path
"""

import os

from pathlib import Path

META_DATA_REL_PATH = ".gptcom"
MEMORY_REL_PATH = os.path.join(META_DATA_REL_PATH, "memory")
CODE_GEN_LOG_FILE = "all_output.txt"
IMPROVE_LOG_FILE = "improve.txt"
DIFF_LOG_FILE = "diff_errors.txt"
DEBUG_LOG_FILE = "debug_log_file.txt"
ENTRYPOINT_FILE = "run.sh"
ENTRYPOINT_LOG_FILE = "gen_entrypoint_chat.txt"
PREPROMPTS_PATH = Path(__file__).parent.parent.parent / "preprompts"


def memory_path(path):
    """
    Constructs the full path to the memory directory based on a given base path.

    Parameters
    ----------
    path : str
        The base path to append the memory directory to.

    Returns
    -------
    str
        The full path to the memory directory.
    """
    return os.path.join(path, MEMORY_REL_PATH)


def metadata_path(path):
    """
    Constructs the full path to the metadata directory based on a given base path.

    Parameters
    ----------
    path : str
        The base path to append the metadata directory to.

    Returns
    -------
    str
        The full path to the metadata directory.
    """
    return os.path.join(path, META_DATA_REL_PATH)
