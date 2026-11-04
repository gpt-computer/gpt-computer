import io
import logging

from gpt_computer.core.chat_to_files import parse_diffs


def test_parse_diffs_with_diff_tag():
    chat = """
Here is the change:
```diff
--- file.py
+++ file.py
@@ -1,1 +1,1 @@
-old
+new
```
"""
    diffs = parse_diffs(chat)
    assert "file.py" in diffs
    assert diffs["file.py"].filename_pre == "file.py"


def test_parse_diffs_with_other_tag():
    # Test that it works with python or other tags if they contain the diff markers
    chat = """
```python
--- file.py
+++ file.py
@@ -1,1 +1,1 @@
-old
+new
```
"""
    diffs = parse_diffs(chat)
    assert "file.py" in diffs


def test_parse_diffs_fallback():
    # Test the fallback when no code blocks are present but diff markers are
    chat = """
--- file.py
+++ file.py
@@ -1,1 +1,1 @@
-old
+new
"""
    diffs = parse_diffs(chat)
    assert "file.py" in diffs
    assert diffs["file.py"].filename_pre == "file.py"


def test_parse_diffs_with_logger():
    # Test that it logs warnings instead of printing
    chat = """
```diff
--- file.py
+++ file.py
@@ -1,1 +1,1 @@
-old
+new
```
```diff
--- file.py
+++ file.py
@@ -1,1 +1,1 @@
-another old
+another new
```
"""
    # Create a logger specific to the module under test
    # Note: The actual logger name is gpt_computer.agent.tools.chat_to_files
    module_logger = logging.getLogger("gpt_computer.agent.tools.chat_to_files")

    # Store original handlers and level
    original_handlers = list(module_logger.handlers)
    original_level = module_logger.level

    # Set level to WARNING to ensure messages are processed
    module_logger.setLevel(logging.WARNING)

    # Use StringIO to capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    module_logger.addHandler(handler)

    try:
        diffs = parse_diffs(chat)
        assert "file.py" in diffs
        log_output = log_stream.getvalue()
        assert "Multiple diffs found for file.py" in log_output
    finally:
        # Clean up: remove the custom handler and restore original handlers and level
        module_logger.removeHandler(handler)
        handler.close()
        module_logger.handlers = original_handlers
        module_logger.setLevel(original_level)


def test_parse_diff_with_path_prefixes():
    content = """
```diff
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,1 @@
-old
+new
```
"""
    diffs = parse_diffs(content)
    assert "b/src/main.py" in diffs
    assert diffs["b/src/main.py"].filename_pre == "a/src/main.py"


def test_parse_diff_shorthand_hunk():
    content = """
```diff
--- main.py
+++ main.py
@@ -1 +1 @@
-old
+new
```
"""
    diffs = parse_diffs(content)
    assert "main.py" in diffs
    hunk = diffs["main.py"].hunks[0]
    assert hunk.start_line_pre_edit == 1
    assert hunk.hunk_len_pre_edit == 1
    assert hunk.start_line_post_edit == 1
    assert hunk.hunk_len_post_edit == 1
