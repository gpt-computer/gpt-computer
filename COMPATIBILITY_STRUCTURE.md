# Compatibility Module Structure

**Date**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Documented - Implementation Pending

This document defines the structure of compatibility modules to be created for backward compatibility.

---

## Compatibility Module Locations

### gptc Package Compatibility

```
gptc/                           # Compatibility package (temporary)
├── __init__.py                 # Top-level re-exports (Client, AsyncClient, ChatCompletion, Model)
├── providers/                  # Compatibility submodule
│   ├── __init__.py             # Re-export from gpt_computer.ai.providers
│   ├── openai.py               # Re-export from gpt_computer.ai.providers.openai
│   ├── anthropic.py            # Re-export from gpt_computer.ai.providers.anthropic
│   ├── google.py               # Re-export from gpt_computer.ai.providers.google
│   ├── groq.py                 # Re-export from gpt_computer.ai.providers.groq
│   ├── mistral.py              # Re-export from gpt_computer.ai.providers.mistral
│   ├── cohere.py               # Re-export from gpt_computer.ai.providers.cohere
│   └── local.py                # Re-export from gpt_computer.ai.providers.local
├── Provider/                    # Compatibility for dynamic Provider module
│   └── __init__.py             # Dynamic re-export of known providers
├── errors/                     # Compatibility submodule
│   └── __init__.py             # Re-export from gpt_computer.ai.errors
├── mcp/                        # Compatibility submodule
│   └── __init__.py             # Re-export from gpt_computer.interfaces.mcp
├── integration/                # Compatibility submodule
│   └── __init__.py             # Re-export from gpt_computer.ai.integration
└── client/                     # Compatibility submodule
    └── __init__.py             # Re-export from gpt_computer.ai.client
```

### gpt_computer Core Compatibility

```
gpt_computer/                   # Add compatibility for core module
└── core/                       # Compatibility for gpt_computer.core imports
    ├── __init__.py             # Re-export from appropriate locations
    ├── ai.py                   # Re-export from gpt_computer.ai.client
    ├── agent.py                 # Re-export from gpt_computer.agent
    └── default/                 # Compatibility for default implementations
        └── __init__.py         # Re-export from new locations
```

---

## Implementation Priority

### Phase 2 (Current)

1. **Create directory structure** - Done
2. **Create stub __init__.py files** - Implement with deprecation warnings
3. **Implement top-level shims** - Critical imports first

### Phase 3 (Vertical Slice)

4. **Implement shims after AI migration** - Update paths to match actual structure
5. **Test shims with actual imports** - Verify they work with migrated code

---

## Status

**Current**: Structure documented, stub files not yet created
**Next**: Implement actual compatibility shims with deprecation warnings
**P0 Blocker**: Must verify compatibility mapping matches actual legacy namespaces before proceeding

---

**Last Updated**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
