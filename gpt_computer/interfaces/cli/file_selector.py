"""
CLI File Selector Module

Provides interactive file selection for projects.
"""

from __future__ import annotations

import fnmatch
import os
import subprocess

from pathlib import Path
from typing import Any, Dict, Generator, List, Union

import toml

from gpt_computer.agent.default.paths import metadata_path
from gpt_computer.agent.memory.disk import DiskMemory
from gpt_computer.infrastructure.files.operations import FilesDict
from gpt_computer.infrastructure.git.operations import filter_by_gitignore, is_git_repo


class FileSelector:
    IGNORE_FOLDERS = {"site-packages", "node_modules", "venv", "__pycache__"}
    FILE_LIST_NAME = "file_selection.toml"
    COMMENT = (
        "# Remove '#' to select a file or turn off linting.\n\n"
        "# Linting with BLACK (Python) enhances code suggestions from LLMs. "
        "To disable linting, uncomment the relevant option in the linting settings.\n\n"
        "# gpt-computer can only read selected files. "
        "Including irrelevant files will degrade performance, "
        "cost additional tokens and potentially overflow token limit.\n\n"
    )
    LINTING_STRING = '[linting]\n# "linting" = "off"\n\n'
    is_linting = True

    def __init__(self, project_path: Union[str, Path]):
        self.project_path = project_path
        self.metadata_db = DiskMemory(metadata_path(self.project_path))
        self.toml_path = self.metadata_db.path / self.FILE_LIST_NAME

    def ask_for_files(self, skip_file_selection=False) -> tuple[FilesDict, bool]:
        if os.getenv("GPTC_TEST_MODE") or skip_file_selection:
            assert self.FILE_LIST_NAME in self.metadata_db
            selected_files = self.get_files_from_toml(self.project_path, self.toml_path)
        else:
            if self.FILE_LIST_NAME in self.metadata_db:
                print(
                    f"File list detected at {self.toml_path}. Edit or delete it if you want to select new files."
                )
                selected_files = self.editor_file_selector(self.project_path, False)
            else:
                selected_files = self.editor_file_selector(self.project_path, True)

        content_dict = {}
        for file_path in selected_files:
            try:
                with open(
                    Path(self.project_path) / file_path, "r", encoding="utf-8"
                ) as content:
                    content_dict[str(file_path)] = content.read()
            except FileNotFoundError:
                print(f"Warning: File not found {file_path}")
            except UnicodeDecodeError:
                print(f"Warning: File not UTF-8 encoded {file_path}, skipping")

        return FilesDict(content_dict), self.is_linting

    def editor_file_selector(
        self, input_path: Union[str, Path], init: bool = True
    ) -> List[str]:
        root_path = Path(input_path)
        tree_dict = {}
        toml_file = DiskMemory(metadata_path(input_path)).path / "file_selection.toml"

        if init:
            tree_dict = {x: "selected" for x in self.get_current_files(root_path)}
            s = toml.dumps({"files": tree_dict})
            s = "\n".join(
                [
                    "# " + line if line.endswith(' = "selected"') else line
                    for line in s.split("\n")
                ]
            )
            with open(toml_file, "w") as f:
                f.write(self.COMMENT)
                f.write(self.LINTING_STRING)
                f.write(s)
        else:
            all_files = self.get_current_files(root_path)
            s = toml.dumps({"files": {x: "selected" for x in all_files}})

            with open(toml_file, "r") as file:
                linting_status = toml.load(file)
            if (
                "linting" in linting_status
                and linting_status["linting"].get("linting", "").lower() == "off"
            ):
                self.is_linting = False
                self.LINTING_STRING = '[linting]\n"linting" = "off"\n\n'
                print("\nLinting is disabled")

            with open(toml_file, "r") as file:
                selected_files = toml.load(file)

            lines = s.split("\n")
            s = "\n".join(
                lines[:1]
                + [
                    line
                    if line.split(" = ")[0].strip('"') in selected_files["files"]
                    else "# " + line
                    for line in lines[1:]
                ]
            )

            with open(toml_file, "w") as file:
                file.write(self.COMMENT)
                file.write(self.LINTING_STRING)
                file.write(s)

        print(
            "Please select and deselect (add # in front) files, save it, and close it to continue..."
        )
        self.open_with_default_editor(toml_file)
        return self.get_files_from_toml(input_path, toml_file)

    def open_with_default_editor(self, file_path: Union[str, Path]):
        editors = [
            "gedit",
            "notepad",
            "nvim",
            "write",
            "nano",
            "vim",
            "emacs",
        ]
        chosen_editor = os.environ.get("EDITOR")

        if chosen_editor:
            try:
                subprocess.run([chosen_editor, file_path])
                return
            except Exception:
                pass

        for editor in editors:
            try:
                subprocess.run([editor, file_path])
                return
            except Exception:
                continue
        print("No suitable text editor found. Please edit the file manually.")

    def is_utf8(self, file_path: Union[str, Path]) -> bool:
        try:
            with open(file_path, "rb") as file:
                file.read().decode("utf-8")
                return True
        except UnicodeDecodeError:
            return False

    def get_files_from_toml(
        self, input_path: Union[str, Path], toml_file: Union[str, Path]
    ) -> List[str]:
        selected_files = []
        edited_tree = toml.load(toml_file)

        if (
            "linting" in edited_tree
            and edited_tree["linting"].get("linting", "").lower() == "off"
        ):
            self.is_linting = False
            print("\nLinting is disabled")
        else:
            self.is_linting = True

        for file, _ in edited_tree["files"].items():
            selected_files.append(file)

        if not selected_files:
            raise Exception(
                "No files were selected. Please select at least one file to proceed."
            )

        print(f"\nYou have selected the following files:\n{input_path}")

        project_path = Path(input_path).resolve()
        selected_paths = set(
            project_path.joinpath(file).resolve(strict=False) for file in selected_files
        )

        for displayable_path in DisplayablePath.make_tree(project_path):
            if displayable_path.path in selected_paths:
                p = displayable_path
                while p.parent and p.parent.path not in selected_paths:
                    selected_paths.add(p.parent.path)
                    p = p.parent

        try:
            for displayable_path in DisplayablePath.make_tree(project_path):
                if displayable_path.path in selected_paths:
                    print(displayable_path.displayable())
        except FileNotFoundError:
            print("Specified path does not exist: ", project_path)
        except Exception as e:
            print("An error occurred while trying to display the file tree:", e)

        print("\n")
        return selected_files

    def merge_file_lists(
        self, existing_files: Dict[str, Any], new_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        for file, properties in new_files.items():
            if file not in existing_files:
                existing_files[file] = properties
        return existing_files

    def should_filter_file(self, file_path: Path, filters: List[str]) -> bool:
        for f in filters:
            if fnmatch.fnmatchcase(str(file_path), f):
                return True
        return False

    def get_current_files(self, project_path: Union[str, Path]) -> List[str]:
        all_files = []
        project_path = Path(project_path).resolve()

        file_list = project_path.glob("**/*")

        for path in file_list:
            if path.is_file():
                relpath = path.relative_to(project_path)
                parts = relpath.parts
                if any(part.startswith(".") for part in parts):
                    continue
                if any(part in self.IGNORE_FOLDERS for part in parts):
                    continue
                if relpath.name == "prompt":
                    continue

                all_files.append(str(relpath))

        if is_git_repo(project_path) and "projects" not in project_path.parts:
            all_files = filter_by_gitignore(project_path, all_files)

        return sorted(all_files, key=lambda x: Path(x).as_posix())


class DisplayablePath(object):
    display_filename_prefix_middle = "├── "
    display_filename_prefix_last = "└── "
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(
        self, path: Union[str, Path], parent_path: "DisplayablePath", is_last: bool
    ):
        self.depth = 0
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1

    @property
    def display_name(self) -> str:
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(
        cls, root: Union[str, Path], parent=None, is_last=False, criteria=None
    ) -> Generator["DisplayablePath", None, None]:
        root = Path(str(root))
        criteria = criteria or cls._default_criteria
        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        if root.is_dir():
            children = sorted(
                list(path for path in root.iterdir() if criteria(path)),
                key=lambda s: str(s).lower(),
            )
            count = 1
            for path in children:
                is_last = count == len(children)
                yield from cls.make_tree(
                    path, parent=displayable_root, is_last=is_last, criteria=criteria
                )
                count += 1

    @classmethod
    def _default_criteria(cls, path: Path) -> bool:
        return True

    def displayable(self) -> str:
        if self.parent is None:
            return self.display_name

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.display_name)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))
