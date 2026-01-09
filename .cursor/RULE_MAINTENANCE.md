# Cursor Rules Maintenance Guide

**Version**: 2.1  
**Last Updated**: January 8, 2026

---

## Overview

This guide explains how to maintain, update, and evolve the VIRA Cursor Rules system. Following these processes ensures rules remain accurate, consistent, and useful.

---

## Rule File Structure

### File Naming Convention
```
00-general.mdc          # General principles
01-domain-name.mdc      # Domain-specific rules
11-testing-patterns.mdc # Next available number
```

**Naming Rules**:
- Use numbered prefixes (00-99) for ordering
- Use descriptive, hyphenated names
- Use `.mdc` extension (Cursor markdown compatibility)

### File Header Template
```markdown
# Rule Title

**Version**: X.Y  
**Last Updated**: YYYY-MM-DD  
**Scope**: Brief description of what this file covers

---

## Cross-LLM Compatibility

[Compatibility notes for different LLMs]

---

## [CRITICAL] First Critical Section

[Content]

## [IMPORTANT] First Important Section

[Content]

## [GUIDANCE] First Guidance Section

[Content]

---

## Summary

[Summary of key principles]
```

---

## Adding a New Rule

### 1. Determine the Appropriate File

**Ask**:
- Does this rule fit an existing domain? → Add to existing file
- Is this a new domain? → Create new file
- Is this general guidance? → Add to `00-general.mdc`

**Examples**:
- New LangGraph pattern → `02-langgraph-agents.mdc`
- New React pattern → `03-typescript-react.mdc`
- New testing approach → `11-testing-patterns.mdc`
- New domain (e.g., deployment) → Create `12-deployment.mdc`

### 2. Add Priority Tag

Every rule section must have a priority tag:
- `[CRITICAL]` - Prevents bugs, security issues, or failures
- `[IMPORTANT]` - Improves code quality and maintainability
- `[GUIDANCE]` - Style and convention preferences

### 3. Include Code Examples

Every rule should have:
- **Good example** showing correct pattern
- **Bad example** showing what to avoid (when helpful)
- **Rationale** explaining why the pattern matters

Template:
```markdown
### [PRIORITY] Rule Title

Brief description of the rule and why it matters.

```language
# BAD - What not to do
bad_example()

# GOOD - Correct pattern
good_example()
```

**Why?** Explanation of benefits and consequences.
```

### 4. Add Development Phase Context

If the rule applies differently by phase:
```markdown
### [CRITICAL] Rule Title

**Phase Application**:
- **Prototype**: Can defer
- **Pre-Production**: Required
- **Production**: Strictly enforced

[Rule content]
```

### 5. Update Documentation

After adding a rule:
- [ ] Update rule file version number
- [ ] Update rule file "Last Updated" date
- [ ] Add to `.cursor/QUICKSTART.md` if it's a critical rule
- [ ] Update `.cursor/cursorrules-compact.md` if it's a CRITICAL rule
- [ ] Update `.cursor/RULES_IMPLEMENTATION_SUMMARY.md` stats
- [ ] Run validation: `python .cursor/scripts/validate_rules.py`

---

## Updating an Existing Rule

### Minor Update (Examples, Clarifications)
**Version Change**: None (or patch: 2.0.0 → 2.0.1)

1. Edit the rule content
2. Update "Last Updated" date
3. Add changelog note if significant
4. Run validation

### Major Update (Changing Requirements)
**Version Change**: Minor (2.0 → 2.1) or Major (2.0 → 3.0)

1. **Document the change**:
   ```markdown
   ### [CRITICAL] Updated Rule
   
   **Changed in v2.1**: Now requires X instead of Y
   
   [New content]
   
   **Migration**: If using old pattern, update to new pattern
   ```

2. **Update all affected files**:
   - Main rule file
   - Quick reference
   - Compact summary (if critical)
   - Related rule files (cross-references)

3. **Bump version**:
   - Minor: New requirement or significant clarification
   - Major: Breaking change to existing patterns

4. **Announce the change**:
   - Team notification
   - Update RULES_IMPLEMENTATION_SUMMARY.md with change log
   - Create migration guide if needed

---

## Creating a New Rule File

### 1. Determine File Number and Name
```bash
# Check existing numbers
ls .cursor/rules/

# Create new file with next number
# Example: 12-deployment.mdc
```

### 2. Use Template
```markdown
# Domain Name Rules

**Version**: 2.1  
**Last Updated**: YYYY-MM-DD  
**Scope**: Description of what this domain covers

---

## Cross-LLM Compatibility

### Version Requirements
- **Tool**: X.Y+
- **Language**: Version info

### LLM-Specific Guidance
Guidance for AI assistants

### Verification Prompt for AI
"Confirm you're using [requirements]"

---

## [CRITICAL] First Critical Rule

[Content with examples]

## [IMPORTANT] First Important Rule

[Content with examples]

---

## Summary

Key principles covered in this file
```

### 3. Register the New File

Update these locations:
- `.cursorrules` - Add to Rule Files section
- `.cursor/QUICKSTART.md` - Add to decision tree if relevant
- `.cursor/rules/README.md` - Add to file index
- `.cursor/RULES_IMPLEMENTATION_SUMMARY.md` - Update stats

### 4. Validate
```bash
python .cursor/scripts/validate_rules.py
```

---

## Deprecating a Rule

### 1. Mark as Deprecated
```markdown
### [DEPRECATED v3.0] Old Rule Name

**This rule is deprecated as of v3.0 and will be removed in v4.0**

**Reason**: Replaced by XYZ or no longer applicable

**Migration**: Use [new pattern] instead

[Original content kept for reference]
```

### 2. Update Cross-References

Find all references to the deprecated rule:
```bash
grep -r "old-rule-name" .cursor/rules/
```

Update each reference to point to new rule or remove if obsolete.

### 3. Set Removal Timeline

- **v3.0**: Mark deprecated
- **v3.5**: Add removal warnings
- **v4.0**: Remove entirely

### 4. Communicate

- Team notification of deprecation
- Update in RULES_IMPLEMENTATION_SUMMARY.md
- Add to migration guide

---

## Version Bumping

### Version Number Format: MAJOR.MINOR.PATCH

**MAJOR (2.0 → 3.0)**:
- Breaking changes to existing rules
- Major restructuring
- Significant new domains added

**MINOR (2.0 → 2.1)**:
- New rules added
- Existing rules significantly updated
- New features or patterns

**PATCH (2.0.0 → 2.0.1)**:
- Typo fixes
- Minor clarifications
- Example improvements

### How to Bump Version

1. **Decide on version bump** based on changes
2. **Update all rule files** to new version
3. **Update main `.cursorrules`** version
4. **Update RULES_IMPLEMENTATION_SUMMARY.md**:
   ```markdown
   ## Version X.Y Changes (Date)
   
   ### Improvements
   - Change 1
   - Change 2
   
   ### Files Modified
   - file1.mdc
   - file2.mdc
   ```
5. **Git tag the version**:
   ```bash
   git tag -a rules-v2.1 -m "Rules version 2.1: Added testing patterns"
   git push origin rules-v2.1
   ```

---

## Quarterly Review Process

### Schedule
Run quarterly reviews aligned with iteration releases.

### Checklist

#### 1. Statistics Review
```bash
python .cursor/scripts/validate_rules.py
```
- Check for consistency issues
- Verify no emojis
- Check version alignment

#### 2. Usage Analysis
Review code review comments from past quarter:
- Which rules are frequently cited?
- Which rules are frequently violated?
- Are any rules unclear or ambiguous?

#### 3. Tech Stack Updates
Check if any dependencies have updated:
- Python version changes
- React version changes
- LangChain/LangGraph API changes
- Pydantic version changes

Update rules accordingly.

#### 4. Rule Effectiveness
For each rule domain:
- Is the rule still relevant?
- Are examples still accurate?
- Are there new patterns to capture?
- Are there deprecated patterns to remove?

#### 5. Documentation Sync
Ensure all supporting docs are updated:
- [ ] QUICKSTART.md reflects current critical rules
- [ ] cursorrules-compact.md has latest critical rules
- [ ] DEVELOPMENT_PHASES.md reflects current process
- [ ] RULES_IMPLEMENTATION_SUMMARY.md is current

#### 6. Team Feedback
Collect feedback from team:
- Which rules are most helpful?
- Which rules are confusing?
- What's missing?
- What should be changed?

---

## Automation

### Pre-Commit Validation (Future)

Create `.cursor/.pre-commit-config-rules.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-rules
        name: Validate Cursor Rules
        entry: python .cursor/scripts/validate_rules.py
        language: system
        pass_filenames: false
        files: ^\.cursor/(rules/.*\.mdc|cursorrules)$
```

### CI/CD Integration (Future)

Add to GitHub Actions:
```yaml
name: Validate Rules
on:
  pull_request:
    paths:
      - '.cursor/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Rules
        run: python .cursor/scripts/validate_rules.py
```

---

## Rule Ownership

### Domain Ownership

Assign owners for each rule domain:

| Domain | File | Owner | Backup |
|--------|------|-------|--------|
| General | 00-general.mdc | Tech Lead | - |
| Python Backend | 01-python-backend.mdc | Backend Lead | - |
| LangGraph Agents | 02-langgraph-agents.mdc | AI/ML Lead | - |
| TypeScript/React | 03-typescript-react.mdc | Frontend Lead | - |
| Real-time UI | 04-realtime-ui.mdc | Frontend Lead | - |
| Configuration | 05-configuration.mdc | DevOps | - |
| Error Handling | 06-error-handling.mdc | Backend Lead | - |
| Documentation | 07-documentation.mdc | Tech Lead | - |
| Iteration Dev | 08-iteration-dev.mdc | Product Owner | - |
| Code Quality | 09-code-quality.mdc | Tech Lead | - |
| Prompt Engineering | 10-prompt-engineering.mdc | AI/ML Lead | - |
| Testing | 11-testing-patterns.mdc | QA Lead | - |

**Owner Responsibilities**:
- Keep domain rules current
- Review PRs affecting their domain
- Propose updates based on team feedback
- Participate in quarterly reviews

---

## Communication

### When to Announce Rule Changes

**Always announce**:
- New CRITICAL rules
- Breaking changes to existing rules
- Deprecated rules
- Major version bumps

**Announcement Channels**:
- Team chat
- Engineering meeting
- RULES_IMPLEMENTATION_SUMMARY.md update log
- Git commit message

**Announcement Template**:
```
🔄 Cursor Rules Update: vX.Y

Changes:
- Added: [New rule description]
- Updated: [Changed rule description]
- Deprecated: [Old rule description]

Action Required:
- [Any migration steps needed]

See .cursor/RULES_IMPLEMENTATION_SUMMARY.md for details
```

---

## Troubleshooting

### Problem: LLM Not Following Rules

**Diagnosis**:
1. Is rule in context? (Check if file is being loaded)
2. Is rule clear? (Ambiguous rules get ignored)
3. Is rule contradicted? (Check for conflicting rules)
4. Is rule CRITICAL? (Lower priority rules may be ignored)

**Solutions**:
- Add to cursorrules-compact.md for visibility
- Add explicit examples
- Add "Verification Prompt for AI" section
- Increase priority if critical

### Problem: Rules Conflicting

**Diagnosis**:
Find conflicting rules:
```bash
grep -A 5 "conflicting_pattern" .cursor/rules/*.mdc
```

**Solutions**:
- Clarify which rule takes precedence
- Document the exception in both rules
- Merge into single comprehensive rule

### Problem: Rules Out of Date

**Diagnosis**:
- Tech stack version changed
- API patterns evolved
- Best practices updated

**Solutions**:
- Run quarterly review
- Update affected rules
- Bump version appropriately
- Announce changes

---

## Best Practices

### DO:
- Keep rules specific and actionable
- Include code examples for every pattern
- Use priority tags consistently
- Update version numbers when changing rules
- Run validation after changes
- Get team feedback regularly

### DON'T:
- Add rules without examples
- Create ambiguous requirements
- Mix multiple concerns in one rule
- Forget to update cross-references
- Skip validation checks
- Ignore team feedback

---

## Summary

Maintaining high-quality rules requires:
1. **Clear ownership** of rule domains
2. **Regular reviews** (quarterly recommended)
3. **Consistent formatting** and priority tags
4. **Automation** for validation
5. **Team communication** for changes
6. **Version control** for tracking evolution

Rules are living documents - they should evolve with the codebase and team practices.
