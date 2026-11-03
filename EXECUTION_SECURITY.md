# Execution Security Rules

**Date**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Draft - Pending Review

This document defines the execution security requirements for the gpt-computer restructure. It establishes security boundaries, defines required security controls, and specifies the implementation requirements for code execution environments.

---

## Security Levels

The restructure defines three execution security levels with increasing isolation:

### Execution Security Level A (Directory-Based)

**Status**: Current Migration Target
**Description**: Defense-in-depth measure using directory restrictions and resource limits
**Security Boundary**: **NOT a security sandbox** - defense-in-depth only

**Requirements**:
- Path restrictions with symlink resolution
- Resource limits (memory, CPU, process-tree termination)
- Environment variable isolation
- Request approval for destructive operations
- Network access control (best-effort)

**Limitations**:
- Does not provide full OS-level isolation
- Malicious code can potentially escape directory restrictions
- Not suitable for untrusted code execution
- Should be clearly documented as "directory-restricted, not sandboxed"

**Supported Platforms**:
- Linux: Full support (resource module, process-tree termination)
- macOS: Full support (resource module, process-tree termination)
- Windows: Partial support (job objects for resource limits, process-tree termination)

### Execution Security Level B (Process-Based)

**Status**: Future Implementation
**Description**: Actual security boundary with OS-level isolation
**Security Boundary**: **Real security sandbox**

**Requirements**:
- OS-level isolation (chroot, containers, or proper sandbox)
- Process-tree timeouts and resource limits
- Network namespace isolation
- Mount namespace isolation (if using containers)
- Tested escape attempts

**Supported Platforms**:
- Linux: Full support (namespaces, cgroups, containers)
- macOS: Partial support (sandbox-exec, containers)
- Windows: Partial support (job objects, containers)

### Execution Security Level C (Container-Based)

**Status**: Future Enhancement
**Description**: Full isolation with Docker containers
**Security Boundary**: **Complete isolation**

**Requirements**:
- Docker container isolation
- Resource quotas (CPU, memory, disk)
- Network isolation
- Volume isolation
- Image signing and verification

**Supported Platforms**:
- Linux: Full support
- macOS: Full support (Docker Desktop)
- Windows: Full support (Docker Desktop)

---

## Current Migration: Execution Security Level A

### Path Restrictions

**Objective**: Prevent code from accessing files outside allowed directories

**Implementation Requirements**:

1. **Symlink Resolution**:
   ```python
   import os
   
   def resolve_path(path: str) -> str:
       """Resolve symlinks to prevent symlink-based escapes."""
       return os.path.realpath(path)
   ```

   `FileStore.push()` resolves each destination and rejects absolute paths,
   parent traversal, and symlinks that point outside its working directory.
   `FileStore.pull()` applies the same containment check before reading files.

2. **Containment Check**:
   ```python
   from pathlib import Path
   
   def is_path_allowed(path: Path, allowed_dirs: List[Path]) -> bool:
       """Check if resolved path is within allowed directories."""
       resolved = Path(resolve_path(str(path))).resolve()
       
       for allowed_dir in allowed_dirs:
           try:
               resolved.relative_to(allowed_dir.resolve())
               return True
           except ValueError:
               continue
       return False
   ```

3. **TOCTOU Mitigation**:
   - Perform checks both before and after operations
   - Use atomic operations where possible
   - Verify path hasn't changed between check and use

4. **Implementation**:
   ```python
   def safe_read_file(path: Path, allowed_dirs: List[Path]) -> str:
       """Read file with path verification (before and after)."""
       # Check before
       if not is_path_allowed(path, allowed_dirs):
           raise PermissionError(f"Path not allowed: {path}")
       
       # Resolve and re-check after
       resolved = resolve_path(str(path))
       if not is_path_allowed(Path(resolved), allowed_dirs):
           raise PermissionError(f"Resolved path not allowed: {resolved}")
       
       return path.read_text()
   ```

### Resource Limits

**Objective**: Limit resource usage to prevent resource exhaustion attacks

**Implementation Requirements**:

1. **Memory Limits** (Unix/Linux):
   ```python
   import resource
   
   def set_memory_limit(max_memory_mb: int):
       """Set memory limit for current process and children."""
       max_memory = max_memory_mb * 1024 * 1024
       resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
   ```

2. **CPU Time Limits** (Unix/Linux):
   ```python
   def set_cpu_time_limit(max_seconds: int):
       """Set CPU time limit for current process and children."""
       resource.setrlimit(resource.RLIMIT_CPU, (max_seconds, max_seconds))
   ```

3. **Process-Tree Termination**:
   ```python
   import subprocess
   import signal
   import os
   
   def kill_process_tree(pid: int):
       """Kill a process and all its children."""
       try:
           # On Unix/Linux
           os.killpg(os.getpgid(pid), signal.SIGKILL)
       except ProcessLookupError:
           pass
   ```

   `DiskExecutionEnv.run()` now uses `communicate(timeout=...)` and starts a new
   process session on POSIX so timeout handling can terminate the entire process
   group. On non-POSIX systems, the current fallback terminates only the direct
   child; descendant termination remains incomplete until platform-specific
   process-tree controls (such as Windows Job Objects) are implemented.

4. **Windows Support** (Job Objects):
   ```python
   # Windows requires job objects for resource limits
   # Implementation using pywin32 or similar
   ```

5. **Fallback Behavior**:
   - If resource limits unavailable: Log warning, proceed without limits
   - Document this as a limitation
   - Never silently disable security controls

### Environment Isolation

**Objective**: Control which environment variables are accessible to executed code

**Implementation Requirements**:

1. **Explicit Allowlist**:
   ```python
   def create_isolated_env(
       allowed_vars: List[str] = None,
       scrub_credentials: bool = True
   ) -> dict:
       """Create isolated environment with explicit variable control."""
       import os
       
       if allowed_vars is None:
           allowed_vars = ["PATH", "HOME", "USER", "LANG"]
       
       env = {}
       for var in allowed_vars:
           if var in os.environ:
               env[var] = os.environ[var]
       
       if scrub_credentials:
           # Remove credential-like variables
           credential_patterns = ["KEY", "TOKEN", "SECRET", "PASSWORD", "API"]
           env = {
               k: v for k, v in env.items()
               if not any(pattern in k.upper() for pattern in credential_patterns)
           }
       
       return env
   ```

2. **Default Behavior**:
   - Scrub credentials by default
   - Only allow essential system variables
   - Explicitly require opt-in for additional variables

3. **Implementation**:
   ```python
   def execute_with_isolated_env(
       command: List[str],
       allowed_vars: List[str] = None
   ) -> subprocess.CompletedProcess:
       """Execute command with isolated environment."""
       env = create_isolated_env(allowed_vars=allowed_vars)
       return subprocess.run(command, env=env)
   ```

### Network Access Control

**Objective**: Control network access from executed code

**Implementation Requirements**:

1. **Network Allowed Flag**:
   ```python
   class ExecutionConfig:
       network_allowed: bool = False  # Default: no network access
   ```

2. **Implementation Note**:
   - Actual network blocking requires OS-level firewall rules or network namespaces (Execution Security Level B)
   - Execution Security Level A can only respect the flag in documentation and API design
   - Code should check the flag and fail fast if network access is attempted when disabled

3. **Best-Effort Implementation**:
   ```python
   def check_network_access(config: ExecutionConfig):
       """Check if network access is allowed."""
       if not config.network_allowed:
           raise PermissionError("Network access is disabled")
   ```

4. **Documentation Requirement**:
   - Clearly document that network control is best-effort in Level A
   - Document that actual isolation requires Level B

### Approval Rules

**Objective**: Require user approval for dangerous operations

**Implementation Requirements**:

1. **Destructive Operations**:
   - File writes outside project directory
   - File deletions
   - System configuration changes
   - Network operations

2. **Approval Flow**:
   ```python
   def request_approval(operation: str, details: str) -> bool:
       """Request user approval for an operation."""
       print(f"Operation: {operation}")
       print(f"Details: {details}")
       response = input("Approve? [y/N]: ")
       return response.lower() in ["y", "yes"]
   ```

3. **Implementation**:
   ```python
   def write_with_approval(
       path: Path,
       content: str,
       project_dir: Path
   ) -> None:
       """Write file with approval if outside project."""
       if not is_path_allowed(path, [project_dir]):
           if not request_approval(
               "Write file outside project",
               f"Path: {path}"
           ):
               raise PermissionError("Operation not approved")
       
       path.write_text(content)
   ```

---

## Future: Execution Security Level B

### OS-Level Isolation

**Requirements**:

1. **Linux**:
   - Use namespaces (mount, network, PID)
   - Use cgroups for resource limits
   - Use seccomp for syscall filtering
   - Use chroot or pivot_root for filesystem isolation

2. **macOS**:
   - Use sandbox-exec for sandboxing
   - Use containers (Docker Desktop)
   - Use seatbelt profiles

3. **Windows**:
   - Use job objects for resource limits
   - Use containers (Docker Desktop)
   - Use Windows Sandbox

### Testing Requirements

**Escape Attempts**:
- Test symlink escape attempts
- Test path traversal attempts
- Test network escape attempts
- Test privilege escalation attempts

**Isolation Verification**:
- Verify process cannot access host filesystem
- Verify process cannot access host network
- Verify process cannot escape resource limits
- Verify process tree termination works

---

## Implementation Checklist

### Phase 2 (Execution Security Level A)

- [ ] Implement path resolution with `os.path.realpath()`
- [ ] Implement containment check with `os.path.commonpath()`
- [ ] Implement TOCTOU mitigation (check before and after)
- [ ] Implement memory limits (Unix/Linux)
- [ ] Implement CPU time limits (Unix/Linux)
- [ ] Implement process-tree termination
- [ ] Implement Windows job object support
- [ ] Implement environment variable isolation
- [ ] Implement credential scrubbing
- [ ] Implement network access control flag
- [ ] Implement approval rules for destructive operations
- [ ] Add fallback behavior when controls unavailable
- [ ] Document all limitations clearly

### Phase 3+ (Execution Security Level B)

- [ ] Implement OS-level isolation (namespaces, cgroups)
- [ ] Implement syscall filtering (seccomp)
- [ ] Implement network namespace isolation
- [ ] Implement mount namespace isolation
- [ ] Test escape attempts
- [ ] Verify isolation effectiveness
- [ ] Document platform-specific limitations

---

## Testing Requirements

### Unit Tests

```python
# tests/test_security.py

def test_path_traversal_protection():
    """Test that path traversal is prevented."""
    env = LocalExecutionEnv(project_path="/tmp/project")
    
    with pytest.raises(PermissionError):
        env.read_files(["/etc/passwd"])

def test_symlink_escape_protection():
    """Test that symlink escapes are prevented."""
    env = LocalExecutionEnv(project_path="/tmp/project")
    
    # Create symlink to outside directory
    os.symlink("/tmp", "/tmp/project/escape")
    
    with pytest.raises(PermissionError):
        env.read_files(["escape/test.txt"])

def test_timeout_terminates_process_tree():
    """Test that timeout terminates entire process tree."""
    env = LocalExecutionEnv(project_path="/tmp/project", timeout=1)
    
    with pytest.raises(TimeoutError):
        env.execute("python infinite_loop.py")
    
    # Verify child processes are also killed

def test_environment_isolation():
    """Test that environment variables are controlled."""
    os.environ["TEST_CREDENTIAL"] = "secret"
    
    env = LocalExecutionEnv(project_path="/tmp/project", scrub_env=True)
    result = env.execute("python check_env.py")
    
    assert "secret" not in result.stdout
```

### Integration Tests

- Test with real-world scenarios (Discord bot, etc.)
- Test with long-running processes
- Test with resource-intensive operations
- Test with network operations

### Security Tests

- Test escape attempts (symlinks, path traversal)
- Test resource limit enforcement
- Test environment isolation
- Test process-tree termination

---

## Documentation Requirements

### Clear Warnings

All documentation must clearly state:

1. **Execution Security Level A**:
   - "Directory-restricted, not sandboxed"
   - "Does not provide full OS-level isolation"
   - "Not suitable for untrusted code execution"
   - "Untrusted code execution disabled until Execution Security Level B"

2. **Platform Limitations**:
   - Document which features are available on which platforms
   - Document fallback behavior when controls unavailable
   - Document known limitations

3. **Upgrade Path**:
   - Document how to upgrade to Execution Security Level B
   - Document when Execution Security Level B is required
   - Document security differences between levels

### User-Facing Documentation

- README: Add security section
- API docs: Document security controls
- CLI help: Document security flags
- Migration guide: Document security changes

---

## Release Gate

### P0 Blocker Resolution

**From RESTRUCTURE_PLAN.md**:
> **P0 BLOCKER**: Define execution security release gate (when untrusted execution can be enabled)

**Resolution**:

1. **Current State (Level A)**:
   - Untrusted code execution: **DISABLED**
   - Reason: Level A does not provide sufficient isolation
   - Documentation: Must clearly state this limitation

2. **Future State (Level B)**:
   - Untrusted code execution: **ENABLED** (after testing)
   - Requirement: OS-level isolation implemented and tested
   - Testing: Escape attempts, isolation verification, platform testing

3. **Release Criteria**:
   - Level A: Can ship with untrusted execution disabled
   - Level B: Can enable untrusted execution after:
     - OS-level isolation implemented
     - Escape attempts tested
     - Isolation verified
     - Documentation updated
     - Security review completed

---

## References

- **RESTRUCTURE_PLAN.md**: Decision 4 - Execution Security Requirements
- **DEPENDENCY_RULES.md**: Architectural layer rules
- **tests/test_security.py**: Security test implementation (from RESTRUCTURE_PLAN.md)

---

**Last Updated**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Draft - Pending Review
