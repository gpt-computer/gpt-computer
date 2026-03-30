# Phase 1 Kickoff Guide - Async/Await Migration

## 📋 Overview

**Duration**: 8 weeks (Weeks 1-8)
**Target Release**: v0.2.0
**Key Goals**:
1. Full async/await support throughout core
2. Structured observability (logging + tracing)
3. Enhanced testing infrastructure

---

## 🎯 Week-by-Week Timeline

### Week 1: Setup & Planning
**Goals**: Get team aligned and development environment ready

**Tasks**:
- [ ] Team meeting: Review architecture and async patterns
- [ ] Setup development environments (all developers)
- [ ] Create feature branches for each component
- [ ] Setup monitoring dashboards (Grafana, Prometheus)
- [ ] Schedule sync meetings (daily standups, Friday reviews)

**Deliverables**:
- [ ] Development guide (this document)
- [ ] Async programming patterns document
- [ ] Testing strategy confirmed
- [ ] CI/CD pipeline ready for async tests

**Team Assignments**:
- **Async Core Lead**: 1 Sr. Python Dev
- **Testing Infrastructure**: 1 QA Engineer
- **Observability Lead**: 1 DevOps Engineer
- **Integration Support**: 1 Backend Dev

---

### Week 2-3: Core Async Refactoring (Issue #100)

**Owner**: Async Core Lead + 1 Backend Dev
**PR#**: [to be assigned]

#### Tasks

```
Day 1-2: Design AsyncAI interface
  - Review OpenAI SDK async patterns
  - Review Anthropic SDK async patterns
  - Design backwards-compatible API
  - Code review with team

Day 3-5: Implement AsyncAI
  - AsyncOpenAI client integration
  - AsyncAnthropic client integration
  - Streaming support (critical for Phase 3)
  - Error handling

Day 6-10: Unit Testing AsyncAI
  - Mock async clients
  - Test concurrent requests (stress test 10+)
  - Test error scenarios
  - Performance benchmarking
```

#### Code Structure

```
gpt_computer/core/
├── ai.py              #← Keep (deprecated)
├── ai_async.py        # ← NEW (async implementation)
└── ai_compat.py       # ← NEW (sync wrapper for backwards compat)
```

#### Pull Request Checklist

- [ ] Code follows async/await best practices
- [ ] No blocking I/O in async functions
- [ ] All functions use `async/await` syntax
- [ ] Error handling covers API failures
- [ ] Tests have 80%+ coverage
- [ ] Performance improved ≥20%
- [ ] Documentation updated
- [ ] All CI checks passing

#### Testing Requirements

```bash
# Run these checks before submitting PR
pytest tests/core/test_ai_async.py -v
pytest tests/core/test_ai_async.py --cov=gpt_computer.core.ai_async
pytest tests/core/test_ai_async.py::test_concurrent_requests --timeout=60
```

---

### Week 3-4: Agent Updates (Issue #101)

**Owner**: 1 Sr. Python Dev + Testing QA
**Depends On**: Issue #100 (AsyncAI working)

#### Tasks

```
Day 1-2: Update BaseAgent interface
  - Make improve() async
  - Provide sync wrapper for compatibility
  - Update docstrings

Day 3-6: Update Agent Implementations
  - SimpleAgent → async
  - CliAgent → async
  - ReActAgent → async (verify tool execution)

Day 7-10: Testing all agents
  - Unit tests for each agent
  - Integration tests
  - Concurrent agent execution tests
  - Load testing (10+ concurrent agents)
```

#### Modified Files

```
gpt_computer/core/
├── base_agent.py      # ← UPDATE (add async methods)
├── agent/
│   ├── simple.py      # ← UPDATE
│   ├── cli_agent.py   # ← UPDATE
│   └── react.py       # ← UPDATE
```

#### Key Pattern

```python
# Before
def improve(self, prompt: str) -> str:
    return self.ai.generate(prompt)

# After
async def improve(self, prompt: str) -> str:
    return await self.ai.generate(prompt)

# Backwards compatibility
def improve_sync(self, prompt: str) -> str:
    return asyncio.run(self.improve(prompt))
```

---

### Week 4-5: CLI Integration (Issue #102)

**Owner**: 1 Backend Dev
**Depends On**: Issues #100, #101

#### Tasks

```
Day 1-4: Update CLI commands
  - Review Typer async support
  - Update command handlers
  - Test with asyncio.run()

Day 5-7: Testing
  - CLI command tests
  - Concurrent CLI execution
  - Performance tests

Day 8-10: Documentation
  - Update CLI documentation
  - Add examples
  - Create migration guide
```

#### Testing CLI Async

```bash
# Test single command
gptc build-app "Create hello world" --async

# Test concurrent commands (bash)
for i in {1..5}; do
  gptc build-app "Task $i" --async &
done
wait
```

---

### Week 5-6: Structured Logging (Issues #103, #104)

**Owner**: DevOps/Observability Engineer + 1 Backend Dev
**Can run in parallel** with CLI work

#### Task 1: Structured Logging (Issue #103)

```
Day 1-3: Setup structlog
  - Install structlog
  - Create logging configuration
  - Add JSON formatter

Day 4-7: Integrate logging
  - Add logging to AI module
  - Add logging to agents
  - Add logging to execution env

Day 8-10: Testing & docs
  - Verify log output
  - Documentation
  - Log analysis examples
```

#### Task 2: OpenTelemetry Tracing (Issue #104)

```
Day 1-3: Setup OpenTelemetry
  - OTLP exporter config
  - Create instrumentation decorators

Day 4-7: Add tracing
  - Trace AI requests
  - Trace agent execution
  - Trace tool calls

Day 8-10: Monitoring
  - Setup Grafana dashboards
  - Setup Jaeger UI
  - Documentation
```

#### Docker Compose for Observability

```yaml
# docker-compose-dev.yml
version: '3.8'

services:
  # Prometheus scrapes metrics
  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  # Jaeger UI for traces
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports: ["6831:6831/udp", "16686:16686"]
    environment:
      COLLECTOR_OTLP_ENABLED: "true"

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards

  # gpt-computer service
  gpt-computer:
    build: .
    ports: ["8000:8000"]
    environment:
      OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4317
      LOG_LEVEL: INFO
```

**Start observability stack**:
```bash
docker-compose -f docker-compose-dev.yml up
# Access:
# - Jaeger: http://localhost:16686
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

---

### Week 6-7: Testing Infrastructure (Issue #105)

**Owner**: QA Engineer + 1 Sr. Dev
**Can overlap with other work**

#### Tasks

```
Day 1-3: Setup pytest-asyncio
  - Install dev dependencies
  - Configure pytest for async
  - Create async test fixtures

Day 4-6: Test mocking
  - Mock AsyncOpenAI client
  - Mock AsyncAnthropic client
  - Mock execution environment

Day 7-10: Test suite
  - Write comprehensive async tests
  - Load testing (10+ concurrent)
  - Integration tests
  - Stress testing
```

#### Test File Structure

```
tests/
├── conftest.py                    # ← ADD (async fixtures)
├── core/
│   ├── test_ai_async.py          # ← NEW
│   ├── test_base_agent_async.py  # ← UPDATE for async
│   └── test_agents_async.py      # ← UPDATE for async
├── applications/
│   └── cli/
│       └── test_cli_async.py      # ← UPDATE for async
├── integration/
│   └── test_async_workflow.py     # ← NEW (end-to-end test)
└── load/
    └── test_concurrent_load.py    # ← NEW (stress test)
```

#### Key Test Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_async_openai():
    """Mock AsyncOpenAI client."""
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock(
        return_value=AsyncMock(
            choices=[AsyncMock(
                message=AsyncMock(content="Test response")
            )]
        )
    )
    return mock

@pytest.fixture
async def async_agent(mock_async_openai):
    """Create test agent with mocked AI."""
    from gpt_computer.core.ai_async import AsyncAI
    from gpt_computer.core.agent import ReActAgent

    ai = AsyncAI(model="gpt-4", api_key="test")
    ai.client = mock_async_openai
    return ReActAgent(ai, None, None)
```

---

### Week 7-8: Integration & Polish

**Activities**:
- [ ] Full integration testing
- [ ] Performance benchmarking
- [ ] Documentation cleanup
- [ ] Code review and merge
- [ ] Release preparation for v0.2.0

#### Merge Strategy

1. **Create integration branch**: `develop-async`
2. **Merge feature branches** in order:
   - AsyncAI (Issue #100)
   - Agents (Issue #101)
   - CLI (Issue #102)
   - Logging (Issue #103)
   - Tracing (Issue #104)
   - Testing (Issue #105)
3. **Full integration testing**
4. **Performance validation**
5. **Merge to main** and tag v0.2.0

#### Release Checklist

- [ ] All tests passing (>90% coverage)
- [ ] All documentation updated
- [ ] CHANGELOG.md written
- [ ] Performance benchmarks documented
- [ ] Migration guide for users
- [ ] No breaking API changes (or documented)
- [ ] GitHub release created
- [ ] Docker image built and pushed

---

## 📊 Success Criteria

### Code Quality
```
Current → Target
Test Coverage: 65% → 75%
Type Hints: 70% → 80%
Cognitive Complexity: Low → Lower
```

### Performance
```
Current → Target (Week 8)
Single Request: ±0% (no regression)
Concurrent (10 req): -40% (40% faster)
Throughput: 5 req/s → 15 req/s
```

### Observability
```
Requirement: ✅ Complete
Logging: JSON structured logs
Tracing: End-to-end traces
Dashboards: Grafana working
```

---

## 🛠️ Development Setup

### Initial Setup (Day 1)

```bash
# 1. Clone repository
git clone https://github.com/khulnasoft/gpt-computer.git
cd gpt-computer

# 2. Setup Python environment
python -m venv .venv
source .venv/bin/activate  # or: .venv\Scripts\activate (Windows)

# 3. Install dependencies
poetry install --with dev

# 4. Add dev dependencies for Phase 1
poetry add -D pytest-asyncio pytest-cov pytest-xdist aiodebug

# 5. Verify setup
pytest tests/ -v

# 6. Create feature branch
git checkout -b feature/async-migration
```

### Pre-Commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Apply hooks to repo
pre-commit install

# Test hooks work
pre-commit run --all-files
```

### IDE Setup

**VS Code (.vscode/settings.json)**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python",
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

### Running Tests Locally

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/core/test_ai_async.py -v

# With coverage
pytest tests/ --cov=gpt_computer --cov-report=html

# Async tests specifically
pytest -m asyncio tests/ -v

# Watch mode (auto-rerun on changes)
pytest-watch tests/
```

---

## 📅 Daily Standup Agenda

**Time**: 15 minutes
**What to cover**:
1. What did you complete yesterday?
2. What will you work on today?
3. Any blockers?
4. Test coverage %, performance bench results

---

## 🚨 Risk Mitigation

### Risk: Breaking Changes
**Impact**: High | **Probability**: Medium

**Mitigation**:
- Maintain sync wrapper for backwards compatibility
- Extensive integration testing
- Migration guide for users
- Gradual deprecation path

### Risk: Performance Regression
**Impact**: High | **Probability**: Low

**Mitigation**:
- Benchmark on Day 1 (baseline)
- Benchmark weekly
- Load testing (>20% concurrent improvement required)
- Rollback plan if needed

### Risk: Schedule Slippage
**Impact**: Medium | **Probability**: Medium

**Mitigation**:
- Weekly review meetings
- Escalate blockers immediately
- Pre-assigned backup resources
- Prioritize core async work first

---

## 📞 Escalation Path

**Blocker encountered?**

1. **First**: Try to resolve in your team
2. **Then**: Escalate to phase lead
3. **If critical**: Escalate to engineering manager
4. **If blocking other teams**: Schedule urgent sync

---

## 🎉 Phase 1 Completion Criteria

When ALL of the following are true:
- ✅ AsyncAI module complete and tested (80%+ coverage)
- ✅ All agents support async interface
- ✅ CLI works with async commands
- ✅ Structured logging integrated throughout
- ✅ OpenTelemetry tracing working
- ✅ Test coverage ≥75%
- ✅ All documentation updated
- ✅ v0.2.0 released to PyPI

---

## 📚 Resources

### Documentation to Review
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Current architecture
- [FEATURE_SPECIFICATIONS.md](./FEATURE_SPECIFICATIONS.md) - Feature details
- [TECHNICAL_IMPLEMENTATION_GUIDE.md](./TECHNICAL_IMPLEMENTATION_GUIDE.md) - Implementation patterns

### External Resources
- [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)
- [AsyncOpenAI SDK](https://github.com/openai/openai-python#async-usage)
- [Anthropic async docs](https://github.com/anthropics/anthropic-sdk-python)
- [structlog docs](https://www.structlog.org/en/stable/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### Async Patterns
- [Real Python: asyncio](https://realpython.com/async-io-python/)
- [FastAPI: Async SQL Database](https://fastapi.tiangolo.com/advanced/sql-databases-async/)
- [RealPython: async/await patterns](https://realpython.com/async-io-python/)

---

## ✅ Action Items

### Before Week 1 Kickoff
- [ ] All developers read this guide
- [ ] Development environments setup
- [ ] Monitoring dashboards configured
- [ ] Daily standup time scheduled
- [ ] Team has access to issue tracking
- [ ] Communication channels setup (Slack, etc.)

### Week 1 Tasks
- [ ] Review async patterns as a team
- [ ] Start Issue #100: AsyncAI Implementation
- [ ] Setup CI/CD for async tests
- [ ] Baseline performance measurements

---

**Document Version**: 1.0
**Last Updated**: March 31, 2026
**Status**: 🟢 Ready for Phase 1 Kickoff
**Approval**: Pending PM/Engineering Lead Sign-off
