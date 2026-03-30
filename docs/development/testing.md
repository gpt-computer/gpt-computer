# Testing Guide for gpt-computer

## Overview

gpt-computer uses a comprehensive testing strategy with pytest as the primary testing framework. This guide covers how to write, run, and maintain tests.

---

## Test Structure

```
tests/
├── __init__.py
├── ai_cache.json              # Cached AI responses for reproducible tests
├── mock_ai.py                 # Mock LLM for testing without API calls
├── test_install.py            # Installation verification
├── test_project_config.py     # Project config tests
├── api/                       # API endpoint tests
│   └── test_api.py
├── applications/              # CLI and application tests
│   └── cli/
│       ├── test_main.py
│       ├── test_cli_agent.py
│       ├── test_list_command.py
│       └── ...
├── benchmark/                 # Benchmark tests
│   └── test_BenchConfig.py
├── core/                      # Core module tests
│   ├── test_ai.py
│   ├── test_chat_to_files.py
│   ├── test_logging.py
│   ├── test_git.py
│   ├── agent/
│   │   └── test_react.py
│   ├── default/
│   │   ├── test_disk_execution_env.py
│   │   ├── test_steps.py
│   │   └── ...
│   └── ...
└── test_data/                 # Test fixtures and sample data
    └── sample_projects/
```

---

## Quick Start: Running Tests

### Run All Tests
```bash
# Install test dependencies first
poetry install --with=test

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with detailed output and stop on first failure
pytest -vv -x
```

### Run Specific Tests
```bash
# Run a specific test file
pytest tests/core/test_ai.py

# Run a specific test class
pytest tests/core/test_ai.py::TestAI

# Run a specific test function
pytest tests/core/test_ai.py::TestAI::test_generate

# Run tests matching a pattern
pytest -k "test_ai"
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=gpt_computer --cov-report=html

# View coverage in browser
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux

# Generate coverage report with missing lines
pytest --cov=gpt_computer --cov-report=term-missing
```

### Run Tests by Category
```bash
# Skip tests requiring API key
pytest -m "not requires_key"

# Run only slow tests
pytest -m "slow"

# Run only unit tests
pytest -m "unit"

# Run only integration tests
pytest -m "integration"
```

---

## Test Markers

Available pytest markers for organizing tests:

| Marker | Usage | Example |
|--------|-------|---------|
| `requires_key` | Tests needing OpenAI API key | Real LLM calls |
| `slow` | Slow running tests | Large file operations |
| `unit` | Unit tests | Component isolation |
| `integration` | Integration tests | Multi-component interaction |
| `api` | API endpoint tests | REST interface |

### Using Markers in Tests
```python
import pytest

@pytest.mark.requires_key
def test_real_openai_call():
    """This test needs a real API key."""
    pass

@pytest.mark.slow
def test_large_file_operation():
    """This test takes time."""
    pass

@pytest.mark.unit
def test_single_component():
    """Test single component in isolation."""
    pass
```

---

## Writing Tests

### Basic Test Structure
```python
import pytest
from gpt_computer.core.ai import AI

class TestAI:
    """Test suite for AI module."""

    @pytest.fixture
    def ai_instance(self):
        """Create an AI instance for testing."""
        return AI(model="gpt-3.5-turbo", api_key="sk-test")

    def test_initialization(self, ai_instance):
        """Test AI instance initialization."""
        assert ai_instance is not None
        assert ai_instance.model == "gpt-3.5-turbo"

    def test_token_counting(self, ai_instance):
        """Test token counting."""
        text = "This is a test sentence."
        tokens = ai_instance.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)
```

### Using Fixtures
```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_ai():
    """Fixture providing a mocked AI instance."""
    ai = MagicMock()
    ai.generate.return_value = "Mocked response"
    ai.count_tokens.return_value = 100
    return ai

@pytest.fixture
def temp_project(tmp_path):
    """Fixture providing a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('hello')")
    return project_dir

def test_with_fixtures(mock_ai, temp_project):
    """Test using multiple fixtures."""
    response = mock_ai.generate("test prompt")
    assert response == "Mocked response"
    assert (temp_project / "main.py").exists()
```

### Testing Asynchronous Code
```python
import pytest
from gpt_computer.core.base_agent import BaseAgent

@pytest.mark.asyncio
async def test_async_agent_improve():
    """Test asynchronous agent improvement loop."""
    agent = BaseAgent(...)
    result = await agent.improve("Generate hello world")
    assert result is not None
```

### Mocking API Calls
```python
from unittest.mock import patch, MagicMock
import pytest

@pytest.mark.requires_key
def test_real_api_call():
    """Test with real API (only when OPENAI_API_KEY is set)."""
    from gpt_computer.core.ai import AI
    ai = AI()
    response = ai.generate("test prompt")
    assert len(response) > 0

def test_mock_api_call():
    """Test with mocked API."""
    with patch('gpt_computer.core.ai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = \
            MagicMock(choices=[MagicMock(message=MagicMock(content="mocked response"))])

        from gpt_computer.core.ai import AI
        ai = AI(api_key="sk-test")
        response = ai.generate("test")
        assert response == "mocked response"
```

---

## Test Configuration

### pytest.ini Options (in pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["--strict-markers", "--verbose"]
markers = [
    "requires_key: tests needing API key",
    "slow: slow running tests",
]
```

### Coverage Configuration
```toml
[tool.coverage.run]
source = ["gpt_computer"]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "@abstractmethod",
]
```

---

## CI/CD Testing Pipeline

### GitHub Actions Workflow
Tests run automatically on:
- **Push to main/develop**: Full test suite
- **Pull requests**: Full test suite
- **Weekly schedule**: Security checks

View results:
1. Go to your GitHub repository
2. Click "Actions" tab
3. Select "CI - Tests" workflow
4. View test results and coverage

### Running Tests Locally (Mimicking CI)
```bash
# Install tox
pip install tox

# Run tests for all Python versions
tox

# Run tests for specific version
tox -e py310

# Run linting and type checks
tox -e lint

# Run coverage analysis
tox -e coverage
```

---

## Coverage Goals & Requirements

### Coverage Targets
- **Minimum overall**: 70%
- **Core modules**: 80%+
- **Critical paths**: 90%+

### Coverage Report
```bash
# Generate detailed coverage report
pytest --cov=gpt_computer --cov-report=term-missing

# Output example:
# Name                    Stmts   Miss  Cover   Missing
# ------------------------------------------------
# gpt_computer/core/ai.py    150     10    93%   45-47,100-102
```

### Improving Coverage
1. **Identify uncovered lines**: `pytest --cov --cov-report=term-missing`
2. **Add tests for gaps**: Create tests for missing lines
3. **Mark intentional gaps**: Use `# pragma: no cover` for expected gaps
4. **Run coverage locally**: Verify improvements before pushing

---

## Best Practices

### Do's ✅
- **Test one thing per test**: Single responsibility principle
- **Use descriptive names**: `test_generate_with_max_tokens_exceeds_limit()`
- **Use fixtures**: Share setup code across tests
- **Test edge cases**: Empty inputs, None values, limits
- **Mock external calls**: Don't call real APIs in unit tests
- **Use markers**: Organize tests by category
- **Keep tests fast**: Slow tests reduce productivity
- **Document complex tests**: Explain WHY the test exists

### Don'ts ❌
- **Don't test implementation details**: Test behavior, not internal code
- **Don't create interdependent tests**: Each test should be independent
- **Don't hardcode values**: Use fixtures and parameters
- **Don't skip important assertions**: Make tests meaningful
- **Don't ignore test failures**: Fix failures immediately
- **Don't leave debug code**: Clean up before committing
- **Don't test third-party libraries**: You don't own them
- **Don't create giant test files**: Organize into logical modules

---

## Debugging Tests

### Run Tests with Print Output
```bash
# Show print statements
pytest -s

# Verbose output with prints
pytest -vv -s
```

### Debug with pdb
```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    result = some_function()
    assert result

# Or use pytest's --pdb flag
pytest --pdb  # Drop to debugger on failures
```

### Run Tests with Logging
```bash
# Show log output
pytest --log-cli-level=DEBUG

# View logs in file
pytest --log-file=test.log --log-file-level=DEBUG
```

---

## Continuous Integration

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks before each commit
# (automatic)

# Manually run all hooks
pre-commit run --all-files
```

### Pull Request Checks
- ✅ All tests pass
- ✅ Code coverage maintained
- ✅ Linting passes (Ruff)
- ✅ Type checking passes (MyPy)
- ✅ Format check passes (Black)

---

## Common Test Issues & Solutions

### Issue: `ImportError: No module named 'gpt_computer'`
**Solution**: Install package in editable mode
```bash
poetry install
```

### Issue: `OPENAI_API_KEY not set` error
**Solution**: Either set environment variable or skip:
```bash
# Option 1: Provide key
export OPENAI_API_KEY=sk-...
pytest

# Option 2: Skip tests requiring key
pytest -m "not requires_key"
```

### Issue: Tests timeout
**Solution**: Check for infinite loops, increase timeout
```bash
pytest --timeout=300  # 5 minute timeout
```

### Issue: Flaky tests (pass sometimes, fail sometimes)
**Solution**:
- Check for timing issues
- Use `pytest-retry` for auto-retry
- Ensure proper mocking of external services
- Check for test interdependencies

---

## Performance Testing

### Benchmark Tests
```bash
# Run benchmark tests
pytest tests/benchmark/

# Profile test execution
pytest --profile
```

### Load Testing
See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for performance testing roadmap.

---

## Resources & References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

---

## Contributing Test Improvements

When contributing tests:
1. Ensure tests follow project conventions
2. Add tests for new features
3. Update existing tests if changing behavior
4. Maintain or improve code coverage
5. Keep tests fast and reliable
6. Document complex test logic

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for more details.

---

**Last Updated**: March 2025
**Version**: 1.0
