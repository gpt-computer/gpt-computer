"""
Chat-to-Files Module

Provides functionality for parsing chat transcripts containing file paths and code blocks,
applying diffs, and parsing unified git diff format strings.

Functions:
    chat_to_files_dict: Parse chat transcript into FilesDict.
    apply_diffs: Apply diffs to files.
    parse_diffs: Parse diff string into Diff objects.
"""

from __future__ import annotations

import logging
import re

from typing import Dict, Tuple

from regex import regex

from gpt_computer.infrastructure.diff.parser import ADD, REMOVE, RETAIN, Diff, Hunk
from gpt_computer.infrastructure.files.operations import FilesDict, file_to_lines_dict

# Initialize a logger for this module
logger = logging.getLogger(__name__)


def chat_to_files_dict(chat: str) -> FilesDict:
    """
    Converts a chat string containing file paths and code blocks into a FilesDict object.

    Args:
    - chat (str): The chat string containing file paths and code blocks.

    Returns:
    - FilesDict: A dictionary with file paths as keys and code blocks as values.
    """
    # Regex to match file paths and associated code blocks
    regex_pattern = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex_pattern, chat, re.DOTALL)

    files_dict = FilesDict()
    for match in matches:
        # Clean and standardize the file path
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))
        path = re.sub(r"^\[(.*)\]$", r"\1", path)
        path = re.sub(r"^`(.*)`$", r"\1", path)
        path = re.sub(r"[\]\:]$", "", path)

        # Extract and clean the code content
        content = match.group(2)

        # Add the cleaned path and content to the FilesDict
        files_dict[path.strip()] = content.strip()

    return files_dict


def apply_diffs(diffs: Dict[str, Diff], files: FilesDict) -> FilesDict:
    """
    Applies diffs to the provided files.

    Args:
    - diffs (Dict[str, Diff]): A dictionary of diffs to apply, keyed by filename.
    - files (FilesDict): The original files to which diffs will be applied.

    Returns:
    - FilesDict: The updated files after applying diffs.
    """
    files = FilesDict(files.copy())
    REMOVE_FLAG = "<REMOVE_LINE>"  # Placeholder to mark lines for removal
    for diff in diffs.values():
        if diff.is_new_file():
            # If it's a new file, create it with the content from the diff
            files[diff.filename_post] = "\n".join(
                line[1] for hunk in diff.hunks for line in hunk.lines
            )
        else:
            if diff.filename_pre not in files:
                # If the file being modified does not exist, initialize it as empty
                files[diff.filename_pre] = ""
            # Convert the file content to a dictionary of lines
            line_dict = file_to_lines_dict(files[diff.filename_pre])
            for hunk in diff.hunks:
                current_line = hunk.start_line_pre_edit
                for line in hunk.lines:
                    if line[0] == RETAIN:
                        current_line += 1
                    elif line[0] == ADD:
                        # Handle added lines
                        current_line -= 1
                        if (
                            current_line in line_dict.keys()
                            and line_dict[current_line] != REMOVE_FLAG
                        ):
                            line_dict[current_line] += "\n" + line[1]
                        else:
                            line_dict[current_line] = line[1]
                        current_line += 1
                    elif line[0] == REMOVE:
                        # Mark removed lines with REMOVE_FLAG
                        line_dict[current_line] = REMOVE_FLAG
                        current_line += 1

            # Remove lines marked for removal
            line_dict = {
                key: line_content
                for key, line_content in line_dict.items()
                if REMOVE_FLAG not in line_content
            }
            # Reassemble the file content
            files[diff.filename_post] = "\n".join(line_dict.values())
    return files


def parse_diffs(diff_string: str, diff_timeout=3) -> dict:
    """
    Parses a diff string in the unified git diff format.

    Args:
    - diff_string (str): The diff string to parse.

    Returns:
    - dict: A dictionary of Diff objects keyed by filename.
    """
    # Regex to match individual diff blocks. Captures the content within ```diff ... ```
    diff_content_pattern = regex.compile(
        r"```(?:[a-zA-Z0-9_-]+)?\s*\n(.*?)\n```", regex.DOTALL
    )

    diffs = {}
    try:
        # Iterate over all diff blocks found in the string
        for match in diff_content_pattern.finditer(diff_string, timeout=diff_timeout):
            # Pass the captured content (group 1) to _parse_diff_block_content
            diff_block_content = match.group(1)
            parsed_diffs_from_block = _parse_diff_block_content(diff_block_content)
            for filename, diff_obj in parsed_diffs_from_block.items():
                if filename not in diffs:
                    diffs[filename] = diff_obj
                else:
                    logger.warning(
                        f"Multiple diffs found for {filename}. Only the first one is kept."
                    )
    except TimeoutError:
        logger.error("gpt-computer timed out while parsing git diff")

    if not diffs:
        # Fallback: try to find diffs without code blocks if the LLM was lazy
        if "--- " in diff_string and "+++ " in diff_string and "@@ " in diff_string:
            logger.info(
                "Failed to find diff blocks in code blocks, attempting to parse raw string..."
            )
            # This is a very basic fallback, could be improved
            raw_diffs = _parse_diff_block_content(diff_string)
            if raw_diffs:
                return raw_diffs

        logger.warning(
            "No proposed changes found. Please try to reselect the files for uploading and edit your prompt file."
        )

    return diffs


def _parse_diff_block_content(diff_content: str) -> dict:
    """
    Parses the content of a diff block (lines without the ``` fences) into a Diff object.
    """
    lines = diff_content.strip().split("\n")
    diffs = {}
    current_diff = None
    hunk_lines = []
    filename_pre = None
    filename_post = None
    hunk_header = None

    for line in lines:
        if line.startswith("--- "):
            # Pre-edit filename
            filename_pre = line[4:].strip()
        elif line.startswith("+++ "):
            # Post-edit filename and initiation of a new Diff object
            if (
                filename_post is not None
                and current_diff is not None
                and hunk_header is not None
            ):
                current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))
                hunk_lines = []
            filename_post = line[4:].strip()
            current_diff = Diff(filename_pre, filename_post)
            diffs[filename_post] = current_diff
        elif line.startswith("@@ "):
            # Start of a new hunk in the diff
            if hunk_lines and current_diff is not None and hunk_header is not None:
                current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))
                hunk_lines = []
            hunk_header = parse_hunk_header(line)
        elif line.startswith("+"):
            # Added line
            hunk_lines.append((ADD, line[1:]))
        elif line.startswith("-"):
            # Removed line
            hunk_lines.append((REMOVE, line[1:]))
        else:
            # Retained line
            hunk_lines.append((RETAIN, line[1:]))

    # Append the last hunk if any
    if current_diff is not None and hunk_lines and hunk_header is not None:
        current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))

    return diffs


def parse_hunk_header(header_line: str) -> Tuple[int, int, int, int]:
    """
    Parses the header of a hunk from a diff.

    Args:
    - header_line (str): The header line of a hunk.

    Returns:
    - tuple: A tuple containing start and length information for pre- and post-edit.
    """
    # Pattern to extract pre and post info, allowing for missing lengths
    pattern = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    match = pattern.search(header_line)

    if not match:
        logger.warning(f"Failed to parse hunk header: {header_line}")
        return 0, 0, 0, 0

    def get_val(idx, default=1):
        return int(match.group(idx)) if match.group(idx) else default

    start_line_pre_edit = get_val(1)
    hunk_len_pre_edit = get_val(2)
    start_line_post_edit = get_val(3)
    hunk_len_post_edit = get_val(4)

    return (
        start_line_pre_edit,
        hunk_len_pre_edit,
        start_line_post_edit,
        hunk_len_post_edit,
    )
