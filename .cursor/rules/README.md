# VIRA Cursor Rules - Modular System

**Version**: 2.0  
**Last Updated**: January 8, 2026  
**Total Rules**: 150+  
**Total Lines**: ~6,000

---

## Overview

This directory contains the modular cursor rules system for VIRA. Each file covers a specific domain with detailed patterns, code examples, and project-specific conventions.

---

## File Index

| File | Size | Scope | Key Topics |
|------|------|-------|------------|
| `00-general.mdc` | 350 lines | Universal principles | Verification, file changes, naming, performance, security |
| `01-python-backend.mdc` | 385 lines | Python 3.10+, FastAPI | Type hints, async, LangChain, Pydantic |
| `02-langgraph-agents.mdc` | 536 lines | LangGraph workflows | State management, nodes, routing, error handling |
| `03-typescript-react.mdc` | 605 lines | React 19, TypeScript | Components, hooks, type safety, API clients |
| `04-realtime-ui.mdc` | 632 lines | WebSocket, streaming | Optimistic updates, refs, flushSync, reconnection |
| `05-configuration.mdc` | 482 lines | Settings, env vars | Pydantic Settings, feature flags, validation |
| `06-error-handling.mdc` | 599 lines | Exceptions, logging | Error handling, observability, monitoring |
| `07-documentation.mdc` | 635 lines | Docs, ADRs | Docstrings, ADRs, API docs, type docs |
| `08-iteration-dev.mdc` | 540 lines | Iteration model | Feature flags, backward compatibility, migration |
| `09-code-quality.mdc` | 578 lines | Code cleanup | TODOs, imports, refactoring, style |
| `10-prompt-engineering.mdc` | 559 lines | Prompts, LLMs | Prompt management, testing, optimization |

---

## Quick Navigation

### Backend Development
- **Python basics**: `01-python-backend.mdc`
- **Agent development**: `02-langgraph-agents.mdc`
- **Configuration**: `05-configuration.mdc`
- **Error handling**: `06-error-handling.mdc`

### Frontend Development
- **React/TypeScript**: `03-typescript-react.mdc`
- **Real-time features**: `04-realtime-ui.mdc`

### Quality & Maintenance
- **General principles**: `00-general.mdc`
- **Documentation**: `07-documentation.mdc`
- **Code quality**: `09-code-quality.mdc`

### Project-Specific
- **Iteration model**: `08-iteration-dev.mdc`
- **Prompt engineering**: `10-prompt-engineering.mdc`

---

## How to Use

### For Development
1. **Starting a new feature**: Read relevant domain file(s)
2. **Code review**: Reference specific rules by file and section
3. **Debugging**: Check error handling and observability rules
4. **Optimization**: Review performance and code quality rules

### For Learning
1. **New to project**: Start with `00-general.mdc` and `08-iteration-dev.mdc`
2. **Backend developer**: Read `01-python-backend.mdc` → `02-langgraph-agents.mdc`
3. **Frontend developer**: Read `03-typescript-react.mdc` → `04-realtime-ui.mdc`
4. **Full-stack**: Read all files in order

### For Maintenance
1. **Update existing rule**: Edit the relevant `.mdc` file
2. **Add new rule**: Add to appropriate file or create new file
3. **Version bump**: Update version and date in file header
4. **Commit**: Use descriptive commit message

---

## File Format

Each rule file follows this structure:

```markdown
# Title

**Version**: X.Y
**Last Updated**: YYYY-MM-DD
**Scope**: Brief description

---

## Section 1

### Subsection

Description of pattern or rule.

```language
# Code example showing the pattern
```

**Why?** Explanation of rationale.

## Section 2
...
```

---

## Key Patterns

### Python
```python
# Modern type hints
def process(data: dict[str, Any]) -> list[str] | None:
    pass

# LangGraph node
def my_node(state: AgentState) -> AgentState:
    print("🔍 Running operation...")
    try:
        state["result"] = perform_operation(state)
        print("   ✓ Complete")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        state["error"] = str(e)
    return state
```

### TypeScript
```typescript
// Typed component with cleanup
const Component: React.FC<Props> = ({ session }) => {
  const wsRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;
    return () => ws.close();
  }, [url]);
  
  return <div>...</div>;
};
```

### Configuration
```python
# Feature flags
class Settings(BaseSettings):
    enable_reflection: bool = Field(default=False, alias="ENABLE_REFLECTION")

# Usage
settings = get_settings()
if settings.enable_reflection:
    result = await reflection_agent.analyze(request)
```

---

## Emoji Conventions

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 🔍 | Analysis/Search | `print("🔍 Running analysis...")` |
| 🔬 | Research | `print("🔬 Running research...")` |
| 🤔 | Reflection | `print("🤔 Running reflection...")` |
| ♻️ | Regeneration | `print("♻️  Regenerating...")` |
| ✓ | Success | `print("   ✓ Complete")` |
| ⚠️ | Warning | `print("   ⚠️  Warning")` |
| ❌ | Error | `print("   ❌ Failed")` |
| 📊 | Metrics | `print("   📊 Confidence: 0.85")` |
| 📋 | Lists | `print("   📋 Found 3 gaps")` |
| 📚 | Data | `print("   📚 Retrieved 10 docs")` |

---

## Iteration Markers

```python
# Iteration 1: Basic RAG pipeline
# Iteration 2: Reflection + Research
# Iteration 3: Multi-agent committee (planned)
```

---

## Contributing

### Adding a New Rule
1. Determine which file it belongs in (or create new file if needed)
2. Follow existing format and structure
3. Include code examples (good and bad)
4. Explain rationale
5. Update this README if adding new file

### Updating Existing Rule
1. Edit the relevant `.mdc` file
2. Update version/date in header
3. Maintain backward compatibility where possible
4. Document breaking changes clearly

### Creating New File
1. Use numbered prefix: `11-new-domain.mdc`
2. Follow standard file structure
3. Add to this README's file index
4. Update main `.cursorrules` file

---

## Version History

- **v2.0** (2025-01-08): Initial modular system with 11 files
  - Migrated from monolithic `.cursorrules`
  - Added detailed examples and rationale
  - Organized by domain

---

## Statistics

- **Total files**: 11
- **Total lines**: ~6,000
- **Total rules**: 150+
- **Code examples**: 200+
- **Domains covered**: 10
- **Custom patterns**: 8 (LangGraph, real-time UI, iterations, etc.)

---

## Support

- **Questions**: Check relevant domain file
- **Issues**: Create GitHub issue with `[cursor-rules]` tag
- **Suggestions**: Open PR with proposed changes
- **Discussion**: Use team chat or GitHub discussions

---

## License

These rules are part of the VIRA project and follow the same license.

---

**Note**: This is a living document. Rules evolve as the project grows and new patterns emerge. Keep rules updated and relevant!
