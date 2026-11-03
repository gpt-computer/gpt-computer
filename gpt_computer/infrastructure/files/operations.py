"""
Files Operations Module

This module provides a FilesDict class which is a dictionary-based container for managing code files.
It extends the standard dictionary to enforce string keys and values, representing filenames and their
corresponding code content.

Classes:
    FilesDict: A dictionary-based container for managing code files.

Functions:
    file_to_lines_dict: Convert file content into a line-numbered dictionary.
"""

from collections import OrderedDict
from pathlib import Path
from typing import Union


class FilesDict(dict):
    """
    A dictionary-based container for managing code files.

    This class extends the standard dictionary to enforce string keys and values,
    representing filenames and their corresponding code content. It provides methods
    to format its contents for chat-based interaction with an AI agent and to enforce
    type checks on keys and values.
    """

    def __setitem__(self, key: Union[str, Path], value: str):
        """
        Set the code content for the given filename, enforcing type checks on the key and value.

        Overrides the dictionary's __setitem__ to enforce type checks on the key and value.
        The key must be a string or a Path object, and the value must be a string representing
        the code content.

        Parameters
        ----------
        key : Union[str, Path]
            The filename as a key for the code content.
        value : str
            The code content to associate with the filename.

        Raises
        ------
        TypeError
            If the key is not a string or Path, or if the value is not a string.
        """
        if not isinstance(key, (str, Path)):
            raise TypeError("Keys must be strings or Path's")
        if not isinstance(value, str):
            raise TypeError("Values must be strings")
        super().__setitem__(key, value)

    def to_chat(self):
        """
        Formats the items of the object (assuming file name and content pairs)
        into a string suitable for chat display.

        Returns
        -------
        str
            A string representation of the files.
        """
        chat_str = ""
        for file_name, file_content in self.items():
            lines_dict = file_to_lines_dict(file_content)
            chat_str += f"File: {file_name}\n"
            for line_number, line_content in lines_dict.items():
                chat_str += f"{line_number} {line_content}\n"
            chat_str += "\n"
        return f"```\n{chat_str}```"

    def to_log(self):
        """
        Formats the items of the object (assuming file name and content pairs)
        into a string suitable for log display.

        Returns
        -------
        str
            A string representation of the files.
        """
        log_str = ""
        for file_name, file_content in self.items():
            log_str += f"File: {file_name}\n"
            log_str += file_content
            log_str += "\n"
        return log_str


def file_to_lines_dict(file_content: str) -> dict:
    """
    Converts file content into a dictionary where each line number is a key
    and the corresponding line content is the value.

    Parameters
    ----------
    file_content : str
        The content of the file.

    Returns
    -------
    dict
        A dictionary with line numbers as keys and line contents as values.
    """
    lines_dict = OrderedDict(
        {
            line_number: line_content
            for line_number, line_content in enumerate(file_content.split("\n"), 1)
        }
    )
    return lines_dict
