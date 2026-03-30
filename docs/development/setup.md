# Developer Setup & Contribution Guide

## Getting Started as a Developer

### Prerequisites

- **Python**: 3.10, 3.11, or 3.12
- **Git**: For version control
- **Poetry**: For dependency management
- **GitHub**: For code hosting and collaboration

### 1. Clone & Setup Repository

```bash
# Clone the repository
git clone https://github.com/xeondesk/gpt-computer
cd gpt-computer

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project and dependencies
poetry install --with=test,docs

# Verify installation
poetry run python -c "import gpt_computer; print('✅ Installation successful!')"
```

### 2. Configure Development Environment

```bash
# Create .env file for local development
cat > .env << EOF
# API Keys (get from respective platforms)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk-...

# Logging
LOG_LEVEL=DEBUG
EOF

# Set environment variables
source .env

# (Optional) Setup pre-commit hooks
pre-commit install
```

### 3. Verify Everything Works

```bash
# Run tests
poetry run pytest tests/ -v --tb=short

# Run linting
poetry run ruff check gpt_computer tests

# Start API server (test it's working)
poetry run python -m gpt_computer.api.main &
sleep 2
curl http://localhost:8000/health
pkill -f "gpt_computer.api.main"
```

---

## Development Workflow

### Creating a Feature Branch

```bash
# Create feature branch following naming convention
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/your-doc-update

# Make your changes
git add .
git commit -m "feat: add new feature"  # Use conventional commits
```

### Running Tests While Development

```bash
# Watch mode - re-run tests on file changes
poetry run pytest-watch tests/

# Run specific test module
poetry run pytest tests/core/test_ai.py -v

# Run with output
poetry run pytest tests/ -v -s

# Run with coverage
poetry run pytest --cov=gpt_computer tests/
```

### Code Quality Checks

```bash
# Format code with Black
poetry run black gpt_computer tests

# Fix linting issues with Ruff
poetry run ruff check --fix gpt_computer tests

# Type checking
poetry run mypy gpt_computer --ignore-missing-imports

# All checks at once (using tox)
poetry run tox -e lint
```

### Debugging

```bash
# Run with logging
LOG_LEVEL=DEBUG poetry run python -m gpt_computer.applications.cli.main

# Run with Python debugger
poetry run python -c "
from gpt_computer.core.ai import AI
import pdb
ai = AI()
pdb.set_trace()
"

# View logs
tail -f logs/*.log
```

---

## Project Structure for Contributors

Key directories for different types of contributions:

```
gpt_computer/
├── core/                 # Core logic (AI, agents, execution)
│   ├── ai.py            # → Modify for new LLM providers
│   ├── base_agent.py    # → Extend for custom agents
│   ├── agent/           # → Add new agent patterns
│   └── agent_tools/     # → Add new tools
├── applications/        # User applications
│   └── cli/            # → Modify for CLI improvements
└── api/                # REST API
    └── main.py         # → Modify for API changes

tests/                   # Test suite
├── core/               # → Add tests for core changes
├── api/                # → Add tests for API changes
└── applications/       # → Add tests for app changes

docs/                   # Documentation
├── *.rst              # → Update .rst files
└── examples/          # → Add example notebooks
```

---

## Code Style & Standards

### Naming Conventions

```python
# Classes: PascalCase
class BaseAgent: pass
class ReActAgent: pass

# Functions/variables: snake_case
def generate_code(): pass
prompt_text = "..."

# Constants: UPPER_SNAKE_CASE
MAX_TOKENS = 4096
DEFAULT_MODEL = "gpt-4"

# Private/internal: _leading_underscore
def _internal_helper(): pass
_cache = {}
```

### Code Organization

```python
# 1. Imports
from typing import Optional
import json
from gpt_computer.core.ai import AI

# 2. Constants
DEFAULT_MAX_ITERATIONS = 3
SUPPORTED_MODELS = ["gpt-4", "gpt-3.5-turbo"]

# 3. Classes
class MyAgent:
    """Docstring describing the class."""

    def __init__(self):
        """Initialize the agent."""
        pass

    def public_method(self):
        """Public method."""
        pass

    def _private_method(self):
        """Private method."""
        pass

# 4. Functions
def helper_function():
    """Helper function."""
    pass
```

### Documentation Style

```python
class Agent:
    """Short description of the class.

    This is a longer description with more details about
    what the class does and how to use it.

    Attributes:
        name: The name of the agent
        model: The LLM model to use

    Example:
        >>> agent = Agent(name="my-agent")
        >>> result = agent.improve("Create a calculator")
    """

    def improve(self, prompt: str, max_iterations: int = 3) -> str:
        """Improve code based on prompt.

        Args:
            prompt: The improvement request
            max_iterations: Maximum iterations (default: 3)

        Returns:
            The improved code

        Raises:
            ValueError: If prompt is empty

        Example:
            >>> agent = Agent()
            >>> result = await agent.improve("add type hints")
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        # ... implementation
        return result
```

### Type Hints

```python
# Always use type hints for better code clarity

def process_files(
    files: dict[str, str],
    max_size: Optional[int] = None
) -> dict[str, str]:
    """Process files with type safety."""
    return files

# For complex types, use TypedDict or Pydantic
from typing import TypedDict

class AIResponse(TypedDict):
    content: str
    tokens: int
    model: str

def parse_response(response: str) -> AIResponse:
    """Parse response."""
    pass
```

---

## Making a Pull Request

### Checklist Before Submitting

- [ ] Code follows project style guide
- [ ] Added tests for new features
- [ ] All tests pass: `poetry run pytest`
- [ ] Linting passes: `poetry run ruff check`
- [ ] Code is formatted: `poetry run black`
- [ ] Type checking passes: `poetry run mypy`
- [ ] Documentation is updated
- [ ] Changelog entry added (if user-facing change)
- [ ] Commits follow conventional commits format
- [ ] No debug code or print statements left

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Related Issues
Fixes #123
Related to #456

## Changes
- Change 1
- Change 2
- Change 3

## Testing
How to test this change:
1. Step 1
2. Step 2

## Checklist
- [x] Tests added/updated
- [x] Documentation updated
- [x] Code follows style guide
```

### Conventional Commits Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

Examples:
```
feat(cli): add --debug flag to main command
fix(core): resolve token counting accuracy issue
docs(api): update API documentation with examples
test(core): add tests for edge cases in ai module
```

---

## Testing Guidelines

### Test Location
- Tests go in `tests/` directory matching source structure
- Unit tests: `tests/core/test_module.py`
- Integration tests: `tests/integrations/test_feature.py`
- API tests: `tests/api/test_endpoints.py`

### Test Requirements
1. **Descriptive names**: `test_agent_improves_code_with_type_hints()`
2. **One assertion per concept**: Test one thing per function
3. **Use fixtures**: Share setup code with `@pytest.fixture`
4. **Mock external calls**: Don't call real APIs in unit tests
5. **Test edge cases**: Empty inputs, None, boundaries

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/core/test_ai.py

# Tests matching pattern
poetry run pytest -k "test_generate"

# With coverage
poetry run pytest --cov=gpt_computer

# Verbose output
poetry run pytest -vv
```

### Test Coverage Goals
- **Core modules**: 80%+ coverage
- **API layer**: 75%+ coverage
- **CLI**: 70%+ coverage
- **Overall**: 70%+ coverage

---

## Documentation Guidelines

### Code Documentation
- Every public class/function needs a docstring
- Use Google-style docstrings (see Code Style section)
- Include examples in docstrings
- Keep comments for WHY, not WHAT

### Markdown Documentation
- Use clear headings hierarchy (H1 → H2 → H3)
- Include code examples with syntax highlighting
- Link to related documentation
- Add a "Last Updated" date

### Updating Documentation
```bash
# Build and view docs locally
poetry run sphinx-build -b html docs/ docs/_build/html
open docs/_build/html/index.html

# Auto-rebuild on changes
poetry run sphinx-autobuild docs/ docs/_build/html
```

---

## Common Development Tasks

### Adding a New Feature

1. **Create branch**: `git checkout -b feature/new-feature`
2. **Implement code**: Write feature code with type hints and docstrings
3. **Add tests**: Write comprehensive tests for feature
4. **Update docs**: Add documentation and examples
5. **Test coverage**: Ensure new code has 80%+ coverage
6. **Run all checks**: `poetry run tox`
7. **Commit**: `git commit -m "feat: add new feature"`
8. **Push**: `git push origin feature/new-feature`
9. **Create PR**: Open pull request with description

### Fixing a Bug

1. **Create branch**: `git checkout -b fix/bug-name`
2. **Write test**: Create test reproducing the bug
3. **Fix code**: Make minimal fix to pass test
4. **Test**: Verify fix and run full test suite
5. **Commit**: `git commit -m "fix: resolve bug description"`
6. **Push & PR**: Same as feature branch

### Improving Documentation

1. **Create branch**: `git checkout -b docs/topic`
2. **Edit .md or .rst files**: Make documentation improvements
3. **Check formatting**: View changes locally
4. **Commit**: `git commit -m "docs: improve documentation"`
5. **Push & PR**: Same as feature branch

### Adding a New Example

1. Create example in `projects/example-name/`
2. Include `prompt` file with description
3. Include `run.sh` to execute the example
4. Add documentation explaining the example
5. Keep example small and focused

---

## Getting Help

### Resources
- **Issues**: Search [GitHub Issues](https://github.com/xeondesk/gpt-computer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/xeondesk/gpt-computer/discussions)
- **Documentation**: [Docs](https://gpt-computer.readthedocs.io)
- **Discord**: [Community Discord](https://discord.gg/...) [Add if applicable]

### Asking for Help
1. Search existing issues/discussions
2. Provide minimal reproducible example
3. Include Python version, OS, error message
4. Mention what you've already tried

---

## Advanced Development

### Running Integration Tests

```bash
# Tests requiring API keys
export OPENAI_API_KEY=sk-...
poetry run pytest -m "requires_key"

# With real API (for CI simulation)
poetry run tox
```

### Profiling Code

```bash
# Memory profiling
pip install memory-profiler
python -m memory_profiler script.py

# Time profiling
pip install py-spy
py-spy record -o profile.svg -- python script.py
```

### Debugging with IDE

**VS Code**:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {"OPENAI_API_KEY": "sk-..."}
        }
    ]
}
```

**PyCharm**:
- Use "Run" → "Debug" for debugging
- Set up environment variables in Run Configuration

---

## Code Review Process

### As a Reviewer
1. **Check tests**: Are new features tested?
2. **Review logic**: Is the implementation correct?
3. **Check style**: Does it follow guidelines?
4. **Test locally**: Verify the code works
5. **Suggest improvements**: Be constructive and kind
6. **Approve or request changes**: Clear decision

### As a Contributor
1. Respond to feedback promptly
2. Make requested changes
3. Mark conversations as resolved when done
4. Re-request review after changes
5. Be patient and constructive

---

## Release Process

### Version Numbering
Follow [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Steps
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release commit
4. Create git tag
5. GitHub Actions publishes to PyPI
6. Create GitHub Release

---

## Common Issues & Solutions

### Issue: `ModuleNotFoundError`
```bash
# Re-install package
poetry install
poetry run python -c "import gpt_computer"
```

### Issue: Tests failing locally but passing in CI
```bash
# Run same Python version as CI
poetry env use python3.10  # or 3.11, 3.12
poetry run pytest
```

### Issue: Pre-commit hooks failing
```bash
# Run hooks manually
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

### Issue: Dependency conflicts
```bash
# Update lock file
poetry lock --no-update

# Or full update
poetry update
```

---

## Resources & Links

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [MODULE_STRUCTURE.md](MODULE_STRUCTURE.md) - Code organization
- [TESTING.md](TESTING.md) - Testing guide
- [API_GUIDE.md](API_GUIDE.md) - REST API documentation
- [CONTRIBUTING.md](.github/CONTRIBUTING.md) - Official contributing guide
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Roadmap

---

**Last Updated**: March 2025
**Version**: 1.0
