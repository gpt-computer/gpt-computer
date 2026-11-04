# CLI Entry Points

**Date**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Final - Guaranteed CLI Command Definition

This document defines the **finite, explicit set of supported CLI commands** that will be maintained with backward compatibility for a minimum of 12 months. All other commands are considered internal and may change without notice.

---

## Overview

The project currently has multiple CLI entry points defined in `pyproject.toml`:
- `gpt-computer` - Primary agent CLI (gpt_computer)
- `ge` - Alias for gpt-computer
- `gptc` - AI client and API CLI (gptc)
- `gptc-mcp` - MCP server CLI
- `gptc-tray` - System tray CLI
- `bench` - Benchmarking CLI

**Compatibility Period**: Minimum 12 months from version 0.3.0 release
**Removal Target**: Version 1.0.0

---

## Entry Points from pyproject.toml

| Entry Point | Module | Function | Purpose | Status |
|-------------|--------|----------|---------|--------|
| `gpt-computer` | `gpt_computer.applications.cli.main` | `app` | Primary agent CLI for code generation/improvement | **Primary Command** |
| `ge` | `gpt_computer.applications.cli.main` | `app` | Alias for gpt-computer | **Legacy Alias** |
| `gptc` | `gptc.cli` | `main` | AI client, API server, GUI, MCP, tray | **Primary Command** |
| `gptc-mcp` | `gptc.mcp.server` | `main` | MCP server standalone | **Secondary Command** |
| `gptc-tray` | `gptc.tray` | `_tray_main` | System tray standalone | **Secondary Command** |
| `bench` | `gpt_computer.benchmark.__main__` | `app` | Benchmarking tool | **Secondary Command** |
| `gptc_test_application` | `tests.caching_main` | `app` | Test application (internal) | Internal |

---

## gpt-computer / ge CLI

**Module**: `gpt_computer.applications.cli.main`
**Entry Point**: `app` (Typer app)

### Main Command (Default)

```bash
gpt-computer [PROJECT_PATH] [OPTIONS]
ge [PROJECT_PATH] [OPTIONS]
```

**Purpose**: Generate or improve a software project using AI agents.

**Arguments**:
- `PROJECT_PATH` - Path to project directory (default: ".")

**Options**:
- `--model`, `-m` - Model ID string (default: from MODEL_NAME env or "gpt-4o")
- `--temperature`, `-t` - Controls randomness (default: 0.1)
- `--improve`, `-i` - Improve existing project mode
- `--lite`, `-l` - Lite mode: generation using only main prompt
- `--clarify`, `-c` - Clarify mode: discuss specification before implementation
- `--self-heal`, `-sh` - Self-heal mode: fix code automatically when it fails
- `--azure`, `-a` - Azure OpenAI Service endpoint
- `--base-url`, `-b` - Base URL for API (e.g., Ollama)
- `--use-custom-preprompts` - Use project's custom preprompts
- `--llm-via-clipboard` - Use clipboard to communicate with AI
- `--verbose`, `-v` - Enable verbose logging
- `--debug`, `-d` - Enable debug mode
- `--prompt_file` - Relative path to prompt file (default: "prompt")
- `--entrypoint_prompt` - Relative path to entrypoint prompt file
- `--image_directory` - Relative path to images folder
- `--use_cache` - Cache LLM responses for speed
- `--skip-file-selection`, `-s` - Skip interactive file selection
- `--no_execution` - Run setup without LLM or code writing (testing)
- `--sysinfo` - Output system information
- `--diff_timeout` - Diff regexp timeout (default: 3)

**Subcommands**:
- `list` - List all available projects in projects/ folder
- `codemap` - Analyze and visualize code structure
- `repository` - Advanced repository intelligence and analysis

**Example Usage**:
```bash
# Generate new project
gpt-computer my-project --model gpt-4o

# Improve existing project
gpt-computer my-project --improve

# Lite mode
gpt-computer my-project --lite

# Clarify mode
gpt-computer my-project --clarify

# List projects
gpt-computer list

# Codemap analysis
gpt-computer codemap analyze my-project

# Repository intelligence
gpt-computer repository explain my-project
```

---

## gptc CLI

**Module**: `gptc.cli`
**Entry Point**: `main`

### Modes

The `gptc` CLI supports multiple modes selected as the first argument:

```bash
gptc [MODE] [MODE_OPTIONS]
```

**Available Modes**:
- `api` (default) - Run API server with optional GUI
- `gui` - Run GUI mode
- `client` - Run client mode
- `mcp` - Run MCP server
- `auth` - Manage authentication for providers
- `dev` - Development mode (API with debug and reload)
- `systray` / `tray` - Run as system tray application
- `pa` - Manage PA providers

### API Mode (Default)

```bash
gptc api [OPTIONS]
gptc [OPTIONS]  # api is default
```

**Purpose**: Run the API server with optional GUI.

**Options**:
- `--bind` - Bind address (default: 0.0.0.0)
- `--port`, `-p` - Port for API server
- `--debug`, `-d` - Enable verbose logging
- `--gui`, `-g` - (deprecated) Use --no-gui instead
- `--no-gui`, `-ng` - Run API without GUI
- `--model` - Default model for chat completion
- `--provider` - Default provider for chat completion
- `--media-provider` - Default provider for image generation
- `--proxy` - Default HTTP proxy
- `--workers` - Number of worker processes
- `--disable-colors` - Disable colorized output
- `--ignore-cookie-files` - Do not read .har or cookie files
- `--cookies-dir` - Custom directory for cookies/HAR files
- `--gptc-api-key` - Authentication key for API
- `--ignored-providers` - Providers to ignore during request processing
- `--cookie-browsers` - Browsers to fetch cookies from
- `--reload` - Enable hot reload
- `--demo` - Enable demo mode
- `--timeout` - Default request timeout in seconds
- `--stream-timeout` - Default streaming timeout in seconds
- `--ssl-keyfile` - SSL key file
- `--ssl-certfile` - SSL cert file
- `--log-config` - Path to log config
- `--access-log` - Enable access logging
- `--no-access-log` - Disable access logging
- `--browser-port` - Port for browser automation tool
- `--browser-host` - Host for browser automation tool (default: 127.0.0.1)
- `--no-headless` - Run browser in visible (non-headless) mode
- `--disable-pa-auto-download` - Do not auto-download PA providers
- `--pa-repo` - GitHub repo for PA providers (default: gpt-computer/pa-providers)
- `--pa-branch` - Branch for PA providers (default: main)

**Example Usage**:
```bash
# Start API server with GUI
gptc api

# Start API server without GUI on custom port
gptc api --no-gui --port 8080

# Start API with specific model
gptc api --model gpt-4o --provider openai

# Development mode with reload
gptc dev

# Start with port shorthand
gptc 8080
```

### GUI Mode

```bash
gptc gui [OPTIONS]
```

**Purpose**: Run GUI mode.

**Options**:
- `--debug` - Enable verbose logging

**Example Usage**:
```bash
gptc gui
gptc gui --debug
```

### Client Mode

```bash
gptc client [OPTIONS]
```

**Purpose**: Run client mode (interactive client).

**Options**:
- `--debug` - Enable verbose logging

**Example Usage**:
```bash
gptc client
gptc client --debug
```

### MCP Mode

```bash
gptc mcp [OPTIONS]
```

**Purpose**: Run MCP (Model Context Protocol) server.

**Options**:
- `--debug`, `-d` - Enable verbose logging
- `--http` - Use HTTP instead of stdio
- `--host` - HTTP server host (default: 0.0.0.0)
- `--port` - HTTP server port (default: 8765)
- `--origin` - CORS origin
- `--safe` - Enable safe mode (module allowlist cannot be overridden)

**Example Usage**:
```bash
# MCP with stdio (default)
gptc mcp

# MCP with HTTP
gptc mcp --http --port 8765

# MCP in safe mode
gptc mcp --safe
```

### Auth Mode

```bash
gptc auth PROVIDER [ACTION]
```

**Purpose**: Manage authentication for providers.

**Arguments**:
- `PROVIDER` - Provider to authenticate with (choices: gemini-cli, antigravity, qwencode, github-copilot)
- `ACTION` - Action to perform (choices: status, login, logout; default: login)

**Example Usage**:
```bash
# Login to Gemini
gptc auth gemini-cli login

# Check auth status
gptc auth gemini-cli status

# Logout from Copilot
gptc auth github-copilot logout
```

### Dev Mode

```bash
gptc dev [OPTIONS]
```

**Purpose**: Development mode (API with debug and reload on port 8080).

**Options**: Inherits all API mode options

**Example Usage**:
```bash
gptc dev
```

### Systray/Tray Mode

```bash
gptc systray [OPTIONS]
gptc tray [OPTIONS]
```

**Purpose**: Run gptc as a system tray application.

**Options**:
- `--port`, `-p` - Port for API server (default: from config)
- `--host` - Bind host for API server (default: 0.0.0.0)
- `--debug`, `-d` - Enable verbose logging
- `--no-autostart` - Do not start API server automatically

**Example Usage**:
```bash
gptc tray
gptc systray --port 8080
gptc tray --no-autostart
```

### PA Mode

```bash
gptc pa ACTION [OPTIONS]
```

**Purpose**: Manage PA providers (download from gpt-computer/pa-providers, list, remove).

**Arguments**:
- `ACTION` - Action to perform (choices: download, list, remove, update)

**Options**:
- `--repo` - GitHub repository to download from (default: gpt-computer/pa-providers)
- `--branch` - Branch to download from (default: main)
- `--file`, `-f` - Download/remove specific file (e.g., koala.pa.py)
- `--all` - Download all *.pa.py files even if they exist (overwrite)
- `--dir` - Target directory (default: ~/.gptc/workspace)
- `--timeout` - Per-request timeout in seconds for GitHub API (default: 30)

**Example Usage**:
```bash
# Download all PA providers
gptc pa download

# Download specific provider
gptc pa download --file koala.pa.py

# List installed providers
gptc pa list

# Remove a provider
gptc pa remove --file koala.pa.py

# Update all providers
gptc pa update
```

### Global Options

- `--install-autocomplete` - Install Bash autocompletion for gptc CLI

**Example Usage**:
```bash
gptc --install-autocomplete
```

---

## gptc-mcp CLI

**Module**: `gptc.mcp.server`
**Entry Point**: `main`

```bash
gptc-mcp [OPTIONS]
```

**Purpose**: Standalone MCP server entry point (alternative to `gptc mcp`).

**Options**: Same as `gptc mcp` mode

**Example Usage**:
```bash
gptc-mcp --http --port 8765
```

---

## gptc-tray CLI

**Module**: `gptc.tray`
**Entry Point**: `_tray_main`

```bash
gptc-tray [OPTIONS]
```

**Purpose**: Standalone system tray entry point (alternative to `gptc tray`).

**Options**: Same as `gptc tray` mode

**Example Usage**:
```bash
gptc-tray --port 8080
```

---

## bench CLI

**Module**: `gpt_computer.benchmark.__main__`
**Entry Point**: `app`

```bash
bench PATH_TO_AGENT [BENCH_CONFIG] [OPTIONS]
```

**Purpose**: Run benchmarks against specified agent.

**Arguments**:
- `PATH_TO_AGENT` - Python file containing `default_config_agent()` function
- `BENCH_CONFIG` - Optional task name in benchmark (default: default_bench_config.toml)

**Options**:
- `--yaml-output` - Path to YAML file for results output
- `--verbose` - Print results for each task
- `--use-cache` - Cache LLM responses (default: True)

**Example Usage**:
```bash
# Run benchmark with default config
bench projects/bench-template/benchmark_agent.py

# Run with custom config
bench projects/bench-template/benchmark_agent.py custom_config.toml

# Output to YAML
bench projects/bench-template/benchmark_agent.py --yaml-output results.yaml

# Verbose output
bench projects/bench-template/benchmark_agent.py --verbose
```

---

## CLI Command Mapping for Restructure

### Primary Commands (to preserve)

**After restructure**, the primary command should be `gptc` with subcommands:

| Current Command | New Command | Status |
|-----------------|-------------|--------|
| `gpt-computer [project]` | `gptc init [project]` | **Rename** |
| `gpt-computer [project] --improve` | `gptc improve [project]` | **Rename** |
| `gptc api` | `gptc api` | **Keep** |
| `gptc mcp` | `gptc mcp` | **Keep** |
| `gptc tray` | `gptc tray` | **Keep** |
| `bench` | `gptc bench` | **Move as subcommand** |
| `gpt-computer list` | `gptc list` | **Move** |
| `gpt-computer codemap` | `gptc codemap` | **Move** |
| `gpt-computer repository` | `gptc repository` | **Move** |

### Legacy Aliases (to deprecate)

| Legacy Command | New Command | Deprecation Period |
|----------------|-------------|-------------------|
| `gpt-computer` | `gptc` | 12 months (remove in 1.0.0) |
| `ge` | `gptc` | 12 months (remove in 1.0.0) |
| `gptc-mcp` | `gptc mcp` | 12 months (remove in 1.0.0) |
| `gptc-tray` | `gptc tray` | 12 months (remove in 1.0.0) |
| `bench` | `gptc bench` | 12 months (remove in 1.0.0) |

### Modes to Deprecate

| Mode | Reason | Replacement |
|------|--------|-------------|
| `gptc gui` | GUI should be accessed via API mode with `--gui` flag | `gptc api --gui` |
| `gptc client` | Unclear purpose, likely redundant with API mode | Document or deprecate |
| `gptc dev` | Can be achieved with `gptc api --debug --reload` | `gptc api --debug --reload` |
| `gptc systray` | Use `tray` instead | `gptc tray` |

---

## Proposed Final CLI Structure

After restructure, the CLI should have this structure:

```bash
gptc [SUBCOMMAND] [OPTIONS]

Subcommands:
  init [PROJECT]        Initialize/generate a new project
  improve [PROJECT]     Improve an existing project
  api                   Run API server (with optional GUI)
  mcp                   Run MCP server
  tray                  Run system tray application
  bench                 Run benchmarks
  list                  List available projects
  codemap               Analyze code structure
  repository            Repository intelligence analysis
  auth                  Manage authentication
  pa                    Manage PA providers

Global Options:
  --help, -h            Show help
  --version             Show version
```

**Deprecation warnings** should be added for:
- `gpt-computer` → Use `gptc init` instead
- `ge` → Use `gptc` instead
- `gptc-mcp` → Use `gptc mcp` instead
- `gptc-tray` → Use `gptc tray` instead
- `bench` → Use `gptc bench` instead

---

## Guaranteed CLI Commands

The following CLI entry points are guaranteed to work with deprecation warnings during the compatibility period:

### Primary Commands

| Command | Status | Deprecation | Migration Path |
|---------|--------|-------------|----------------|
| `gptc` | Primary | No | Keep as primary command |
| `gpt-computer` | Legacy | Yes | Use `gptc init` or `gptc improve` |
| `ge` | Legacy | Yes | Use `gptc` |

### Subcommands (via gptc)

| Command | Status | Notes |
|---------|--------|-------|
| `gptc api` | Keep | API server mode |
| `gptc mcp` | Keep | MCP server mode |
| `gptc tray` | Keep | System tray mode |
| `gptc bench` | Keep | Benchmarking (moved from standalone) |

### Legacy Standalone Commands

| Command | Status | Deprecation | Migration Path |
|---------|--------|-------------|----------------|
| `gptc-mcp` | Legacy | Yes | Use `gptc mcp` |
| `gptc-tray` | Legacy | Yes | Use `gptc tray` |
| `bench` | Legacy | Yes | Use `gptc bench` |

### Intentionally NOT Supported

The following modes are intentionally not guaranteed as public APIs:

| Mode | Reason |
|------|--------|
| `gptc gui` | Use `gptc api --gui` instead |
| `gptc client` | Purpose unclear, use API mode |
| `gptc dev` | Use `gptc api --debug --reload` |
| `gptc systray` | Use `gptc tray` |
| `gptc auth` | Internal authentication management |
| `gptc pa` | Internal PA provider management |

---

## Final CLI Structure

After restructure, the supported CLI structure is:

```bash
gptc [SUBCOMMAND] [OPTIONS]

Subcommands:
  init [PROJECT]        Initialize/generate a new project
  improve [PROJECT]     Improve an existing project
  api                   Run API server (with optional GUI)
  mcp                   Run MCP server
  tray                  Run system tray application
  bench                 Run benchmarks
  list                  List available projects
  codemap               Analyze code structure
  repository            Repository intelligence analysis
```

---

## Deprecation Policy

### Version Schedule

- **Current**: 0.1.1
- **Restructure release**: 0.3.0
- **Deprecation period**: 0.3.x → 0.4.x → 0.5.x (minimum 12 months)
- **Removal scheduled**: 1.0.0

### Warning Behavior

Legacy CLI commands will emit deprecation warnings:

```bash
$ gpt-computer my-project
WARNING: The 'gpt-computer' command is deprecated and will be removed in version 1.0.0.
Use 'gptc init my-project' instead. See MIGRATION_GUIDE.md for details.
```

---

## Testing Requirements

For each guaranteed CLI command:
1. Command executes successfully
2. Deprecation warning is emitted for legacy commands
3. Functionality is preserved
4. Help text is accurate

---

**Last Updated**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Final - Guaranteed CLI Command Definition
3. Design compatibility wrapper for legacy CLI entry points
4. Implement deprecation warnings for legacy aliases
5. Update documentation to reflect new CLI structure
6. Create migration guide for CLI users

---

**Last Updated**: 2026-10-28
**Phase**: Phase 0 - Baseline and Inventory
