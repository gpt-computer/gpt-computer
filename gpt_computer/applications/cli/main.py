"""
Entrypoint for the CLI tool.

This module serves as the entry point for a command-line interface (CLI) tool.
It is designed to interact with OpenAI's language models.
The module provides functionality to:
- Load necessary environment variables,
- Configure various parameters for the AI interaction,
- Manage the generation or improvement of code projects.

Main Functionality
------------------
- Load environment variables required for OpenAI API interaction.
- Parse user-specified parameters for project configuration and AI behavior.
- Facilitate interaction with AI models, databases, and archival processes.

Parameters
----------
None

Notes
-----
- The `OPENAI_API_KEY` must be set in the environment or provided in a `.env` file within the working directory.
- The default project path is `projects/example`.
- When using the `azure_endpoint` parameter, provide the Azure OpenAI service endpoint URL.
"""

import asyncio
import difflib
import json
import logging
import os
import platform
import subprocess
import sys
import time

from pathlib import Path

import typer

from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from termcolor import colored

from gpt_computer.applications.cli.cli_agent import CliAgent
from gpt_computer.applications.cli.collect import collect_and_send_human_review
from gpt_computer.applications.cli.file_selector import FileSelector
from gpt_computer.core.ai import AI, ClipboardAI
from gpt_computer.core.config import get_settings
from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_computer.core.default.disk_memory import DiskMemory
from gpt_computer.core.default.file_store import FileStore
from gpt_computer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_computer.core.default.steps import (
    execute_entrypoint,
    gen_code,
    handle_improve_mode,
    improve_fn as improve_fn,
)
from gpt_computer.core.files_dict import FilesDict
from gpt_computer.core.git import stage_uncommitted_to_git
from gpt_computer.core.logging_config import setup_logging
from gpt_computer.core.preprompts_holder import PrepromptsHolder
from gpt_computer.core.prompt import Prompt
from gpt_computer.tools.custom_steps import clarified_gen, lite_gen, self_heal

# Import structured logging and tracing if available
try:
    from gpt_computer.core.structured_logging import (
        get_logger,
        setup_structured_logging,
    )
    from gpt_computer.core.tracing import trace_async_function

    STRUCTURED_LOGGING_AVAILABLE = True
    TRACING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False
    TRACING_AVAILABLE = False

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}
)  # creates a CLI app

logger = logging.getLogger(__name__)


def concatenate_paths(base_path, sub_path):
    # Compute the relative path from base_path to sub_path
    relative_path = os.path.relpath(sub_path, base_path)

    # If the relative path is not in the parent directory, use the original sub_path
    if not relative_path.startswith(".."):
        return sub_path

    # Otherwise, concatenate base_path and sub_path
    return os.path.normpath(os.path.join(base_path, sub_path))


async def load_prompt(
    input_repo: DiskMemory,
    improve_mode: bool,
    prompt_file: str,
    image_directory: str,
    entrypoint_prompt_file: str = "",
) -> Prompt:
    """
    Load or request a prompt from the user based on the mode.

    Parameters
    ----------
    input_repo : DiskMemory
        The disk memory object where prompts and other data are stored.
    improve_mode : bool
        Flag indicating whether the application is in improve mode.

    Returns
    -------
    str
        The loaded or inputted prompt.
    """

    if os.path.isdir(prompt_file):
        raise ValueError(
            f"The path to the prompt, {prompt_file}, already exists as a directory. No prompt can be read from it. Please specify a prompt file using --prompt_file"
        )
    prompt_str = input_repo.get(prompt_file)
    if prompt_str:
        typer.echo(colored("Using prompt from file: ", "green") + prompt_file)
        typer.echo(prompt_str)
    else:
        loop = asyncio.get_event_loop()
        if not improve_mode:
            prompt_str = await loop.run_in_executor(
                None,
                input,
                "\nWhat application do you want gpt-computer to generate?\n",
            )
        else:
            prompt_str = await loop.run_in_executor(
                None, input, "\nHow do you want to improve the application?\n"
            )

    if entrypoint_prompt_file == "":
        entrypoint_prompt = ""
    else:
        full_entrypoint_prompt_file = concatenate_paths(
            input_repo.path, entrypoint_prompt_file
        )
        if os.path.isfile(full_entrypoint_prompt_file):
            entrypoint_prompt = input_repo.get(full_entrypoint_prompt_file)

        else:
            raise ValueError("The provided file at --entrypoint-prompt does not exist")

    if image_directory == "":
        return Prompt(prompt_str, entrypoint_prompt=entrypoint_prompt)

    full_image_directory = concatenate_paths(input_repo.path, image_directory)
    if os.path.isdir(full_image_directory):
        if len(os.listdir(full_image_directory)) == 0:
            raise ValueError("The provided --image_directory is empty.")
        image_repo = DiskMemory(full_image_directory)
        return Prompt(
            prompt_str,
            image_repo.get(".").to_dict(),
            entrypoint_prompt=entrypoint_prompt,
        )
    else:
        raise ValueError("The provided --image_directory is not a directory.")


def get_preprompts_path(use_custom_preprompts: bool, input_path: Path) -> Path:
    """
    Get the path to the preprompts, using custom ones if specified.

    Parameters
    ----------
    use_custom_preprompts : bool
        Flag indicating whether to use custom preprompts.
    input_path : Path
        The path to the project directory.

    Returns
    -------
    Path
        The path to the directory containing the preprompts.
    """
    original_preprompts_path = PREPROMPTS_PATH
    if not use_custom_preprompts:
        return original_preprompts_path

    custom_preprompts_path = input_path / "preprompts"
    if not custom_preprompts_path.exists():
        custom_preprompts_path.mkdir()

    for file in original_preprompts_path.glob("*"):
        if not (custom_preprompts_path / file.name).exists():
            (custom_preprompts_path / file.name).write_text(file.read_text())
    return custom_preprompts_path


def compare(f1: FilesDict, f2: FilesDict):
    def colored_diff(s1, s2):
        lines1 = s1.splitlines()
        lines2 = s2.splitlines()

        diff = difflib.unified_diff(lines1, lines2, lineterm="")

        RED = "\033[38;5;202m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        colored_lines = []
        for line in diff:
            if line.startswith("+"):
                colored_lines.append(GREEN + line + RESET)
            elif line.startswith("-"):
                colored_lines.append(RED + line + RESET)
            else:
                colored_lines.append(line)

        return "\n".join(colored_lines)

    for file in sorted(set(f1) | set(f2)):
        diff = colored_diff(f1.get(file, ""), f2.get(file, ""))
        if diff:
            typer.echo(f"Changes to {file}:")
            typer.echo(diff)


async def prompt_yesno() -> bool:
    TERM_CHOICES = colored("y", "green") + "/" + colored("n", "red") + " "
    loop = asyncio.get_event_loop()
    while True:
        response = await loop.run_in_executor(None, input, TERM_CHOICES)
        response = response.strip().lower()
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            break
        typer.echo("Please respond with 'y' or 'n'")


def get_system_info():
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "packages": format_installed_packages(get_installed_packages()),
    }
    return system_info


def get_installed_packages():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
        )
        packages = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in packages}
    except Exception as e:
        return str(e)


def format_installed_packages(packages):
    return "\n".join([f"{name}: {version}" for name, version in packages.items()])


@app.command(
    help="""
        GPT-computer lets you:

        \b
        - Specify a software in natural language
        - Sit back and watch as an AI writes and executes the code
        - Ask the AI to implement improvements
    """
)
def main(
    project_path: str = typer.Argument(".", help="path"),
    model: str = typer.Option(
        os.environ.get("MODEL_NAME", "gpt-4o"), "--model", "-m", help="model id string"
    ),
    temperature: float = typer.Option(
        0.1,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs",
    ),
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve an existing project by modifying the files.",
    ),
    lite_mode: bool = typer.Option(
        False,
        "--lite",
        "-l",
        help="Lite mode: run a generation using only the main prompt.",
    ),
    clarify_mode: bool = typer.Option(
        False,
        "--clarify",
        "-c",
        help="Clarify mode - discuss specification with AI before implementation.",
    ),
    self_heal_mode: bool = typer.Option(
        False,
        "--self-heal",
        "-sh",
        help="Self-heal mode - fix the code by itself when it fails.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
            In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    base_url: str = typer.Option(
        None,
        "--base-url",
        "-b",
        help="Base URL for the API (e.g. http://localhost:11434/v1 for Ollama).",
    ),
    use_custom_preprompts: bool = typer.Option(
        False,
        "--use-custom-preprompts",
        help="""Use your project's custom preprompts instead of the default ones.
          Copies all original preprompts to the project's workspace if they don't exist there.""",
    ),
    llm_via_clipboard: bool = typer.Option(
        False,
        "--llm-via-clipboard",
        help="Use the clipboard to communicate with the AI.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging for debugging."
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug mode for debugging."
    ),
    prompt_file: str = typer.Option(
        "prompt",
        "--prompt_file",
        help="Relative path to a text file containing a prompt.",
    ),
    entrypoint_prompt_file: str = typer.Option(
        "",
        "--entrypoint_prompt",
        help="Relative path to a text file containing a file that specifies requirements for you entrypoint.",
    ),
    image_directory: str = typer.Option(
        "",
        "--image_directory",
        help="Relative path to a folder containing images.",
    ),
    use_cache: bool = typer.Option(
        False,
        "--use_cache",
        help="Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.",
    ),
    skip_file_selection: bool = typer.Option(
        False,
        "--skip-file-selection",
        "-s",
        help="Skip interactive file selection in improve mode and use the generated TOML file directly.",
    ),
    no_execution: bool = typer.Option(
        False,
        "--no_execution",
        help="Run setup but to not call LLM or write any code. For testing purposes.",
    ),
    sysinfo: bool = typer.Option(
        False,
        "--sysinfo",
        help="Output system information for debugging",
    ),
    diff_timeout: int = typer.Option(
        3,
        "--diff_timeout",
        help="Diff regexp timeout. Default: 3. Increase if regexp search timeouts.",
    ),
):
    """
    The main entry point for the CLI tool that generates or improves a project.
    """
    asyncio.run(
        _main(
            project_path,
            model,
            temperature,
            improve_mode,
            lite_mode,
            clarify_mode,
            self_heal_mode,
            azure_endpoint,
            base_url,
            use_custom_preprompts,
            llm_via_clipboard,
            verbose,
            debug,
            prompt_file,
            entrypoint_prompt_file,
            image_directory,
            use_cache,
            skip_file_selection,
            no_execution,
            sysinfo,
            diff_timeout,
        )
    )


@ trace_async_function("CLI", "main") if TRACING_AVAILABLE else lambda x: x
async def _main(
    project_path: str,
    model: str,
    temperature: float,
    improve_mode: bool,
    lite_mode: bool,
    clarify_mode: bool,
    self_heal_mode: bool,
    azure_endpoint: str,
    base_url: str,
    use_custom_preprompts: bool,
    llm_via_clipboard: bool,
    verbose: bool,
    debug: bool,
    prompt_file: str,
    entrypoint_prompt_file: str,
    image_directory: str,
    use_cache: bool,
    skip_file_selection: bool,
    no_execution: bool,
    sysinfo: bool,
    diff_timeout: int,
):
    start_time = time.time()

    # Initialize structured logger if available
    if STRUCTURED_LOGGING_AVAILABLE:
        structured_logger = get_logger("CLI")
        structured_logger.info(
            "CLI session started",
            project_path=project_path,
            model=model,
            temperature=temperature,
            improve_mode=improve_mode,
            lite_mode=lite_mode,
            clarify_mode=clarify_mode,
            self_heal_mode=self_heal_mode,
            llm_via_clipboard=llm_via_clipboard,
            verbose=verbose,
            debug=debug,
        )
    else:
        structured_logger = None
    if debug:
        import pdb

        sys.excepthook = lambda *_: pdb.pm()

    settings = get_settings()

    # Override settings with CLI options if provided
    if model != "gpt-4o":
        settings.model_name = model
    if temperature != 0.1:
        settings.temperature = temperature
    settings.verbose = verbose
    settings.debug = debug

    if sysinfo:
        sys_info = get_system_info()
        for key, value in sys_info.items():
            typer.echo(f"{key}: {value}")
        raise typer.Exit()

    # Validate arguments
    if improve_mode and (clarify_mode or lite_mode):
        typer.echo("Error: Clarify and lite mode are not compatible with improve mode.")
        raise typer.Exit(code=1)

    if use_cache:
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
    if improve_mode:
        assert not (
            clarify_mode or lite_mode
        ), "Clarify and lite mode are not active for improve mode"

    if llm_via_clipboard:
        ai = ClipboardAI()
    else:
        ai = AI(
            model_name=settings.model_name,
            temperature=settings.temperature,
            azure_endpoint=azure_endpoint or settings.azure_openai_endpoint,
            base_url=base_url,
        )

    path = Path(project_path)
    typer.echo(f"Running gpt-computer in {path.absolute()}\n")

    prompt = await load_prompt(
        DiskMemory(path),
        improve_mode,
        prompt_file,
        image_directory,
        entrypoint_prompt_file,
    )

    # todo: if ai.vision is false and not llm_via_clipboard - ask if they would like to use gpt-4-vision-preview instead? If so recreate AI
    if not ai.vision:
        prompt.image_urls = None

    # configure generation function
    if clarify_mode:
        code_gen_fn = clarified_gen
    elif lite_mode:
        code_gen_fn = lite_gen
    else:
        code_gen_fn = gen_code

    # configure execution function
    if self_heal_mode:
        execution_fn = self_heal
    else:
        execution_fn = execute_entrypoint

    preprompts_holder = PrepromptsHolder(
        get_preprompts_path(use_custom_preprompts, Path(project_path))
    )

    memory = DiskMemory(memory_path(project_path))
    memory.archive_logs()

    # Set up structured logging if available, fallback to regular logging
    if STRUCTURED_LOGGING_AVAILABLE:
        setup_structured_logging(
            level="DEBUG" if verbose else "INFO",
            service_name="gpt-computer-cli",
            log_file=str(memory.path / "logs" / "structured.log"),
            console_output=True,
        )
    else:
        setup_logging(verbose=verbose, memory=memory)

    execution_env = DiskExecutionEnv()
    agent = CliAgent.with_default_config(
        memory,
        execution_env,
        ai=ai,
        code_gen_fn=code_gen_fn,
        improve_fn=improve_fn,
        process_code_fn=execution_fn,
        preprompts_holder=preprompts_holder,
    )

    files = FileStore(project_path)
    if not no_execution:
        if improve_mode:
            files_dict_before, is_linting = FileSelector(project_path).ask_for_files(
                skip_file_selection=skip_file_selection
            )

            # lint the code
            if is_linting:
                files_dict_before = files.linting(files_dict_before)

            files_dict = await handle_improve_mode(
                prompt, agent, memory, files_dict_before, diff_timeout=diff_timeout
            )
            if not files_dict or files_dict_before == files_dict:
                typer.echo(
                    f"No changes applied. Could you please upload the debug_log_file.txt in {memory.path}/logs folder in a github issue?"
                )

            else:
                typer.echo("\nChanges to be made:")
                compare(files_dict_before, files_dict)

                typer.echo()
                typer.echo(
                    colored("Do you want to apply these changes?", "light_green")
                )
                if not await prompt_yesno():
                    files_dict = files_dict_before

        else:
            files_dict = await agent.init(prompt)
            # collect user feedback if user consents
            config = (code_gen_fn.__name__, execution_fn.__name__)
            collect_and_send_human_review(prompt, model, temperature, config, memory)

        stage_uncommitted_to_git(path, files_dict, improve_mode)

        files.push(files_dict)

    if ai.token_usage_log.is_openai_model():
        cost_message = f"Total api cost: $ {ai.token_usage_log.usage_cost()}"
        typer.echo(cost_message)
        if structured_logger:
            structured_logger.info(
                "CLI session completed",
                total_cost=ai.token_usage_log.usage_cost(),
                total_tokens=ai.token_usage_log.total_tokens(),
                total_time_ms=(time.time() - start_time) * 1000,
                success=True,
            )
    elif os.getenv("LOCAL_MODEL"):
        cost_message = "Total api cost: $ 0.0 since we are using local LLM."
        typer.echo(cost_message)
        if structured_logger:
            structured_logger.info(
                "CLI session completed",
                total_cost=0.0,
                local_model=True,
                total_time_ms=(time.time() - start_time) * 1000,
                success=True,
            )
    else:
        token_message = f"Total tokens used: {ai.token_usage_log.total_tokens()}"
        typer.echo(token_message)
        if structured_logger:
            structured_logger.info(
                "CLI session completed",
                total_tokens=ai.token_usage_log.total_tokens(),
                total_time_ms=(time.time() - start_time) * 1000,
                success=True,
            )


@app.command(help="List all available projects in the projects/ folder.")
def list():
    """
    Lists all available projects in the projects/ folder by looking for directories containing a 'prompt' file.
    """
    projects_dir = Path("projects")
    if not projects_dir.exists() or not projects_dir.is_dir():
        typer.echo(colored("No projects directory found.", "red"))
        return

    typer.echo(colored("Available projects:", "cyan"))
    for item in sorted(projects_dir.iterdir()):
        if item.is_dir() and (item / "prompt").exists():
            typer.echo(f"  - {item.name}")


if __name__ == "__main__":
    app()
