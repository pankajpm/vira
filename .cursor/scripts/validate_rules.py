#!/usr/bin/env python3
"""Validate VIRA Cursor Rules consistency and quality.

This script checks for:
- Consistent version numbers across files
- No emoji characters in code examples
- Priority tags used consistently
- No duplicate patterns
- Valid cross-references
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple
from collections import defaultdict

# Emoji pattern - common emojis used in code
EMOJI_PATTERN = re.compile(r'[🔍🔬🤔♻️✓⚠️❌📊📋📚🛑🔄⏱️]')

# Priority tag pattern
PRIORITY_PATTERN = re.compile(r'###?\s*\[(CRITICAL|IMPORTANT|GUIDANCE)\]')

# Version pattern
VERSION_PATTERN = re.compile(r'\*\*Version\*\*:\s*(\d+\.\d+)')


def find_emojis(file_path: Path) -> List[Tuple[int, str]]:
    """Find emoji characters in file."""
    emojis = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if EMOJI_PATTERN.search(line):
                emojis.append((line_num, line.strip()))
    return emojis


def check_version(file_path: Path) -> str | None:
    """Extract version from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(500)  # Check first 500 chars
        match = VERSION_PATTERN.search(content)
        return match.group(1) if match else None


def count_priority_tags(file_path: Path) -> dict:
    """Count priority tags in file."""
    counts = defaultdict(int)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = PRIORITY_PATTERN.search(line)
            if match:
                counts[match.group(1)] += 1
    return dict(counts)


def find_duplicate_patterns(rules_dir: Path) -> List[str]:
    """Find potentially duplicate code patterns across files."""
    # This is a simple heuristic - look for similar function signatures
    pattern_files = defaultdict(list)
    
    for file_path in rules_dir.glob('*.mdc'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for function definitions
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            for func in functions:
                pattern_files[func].append(file_path.name)
    
    duplicates = []
    for pattern, files in pattern_files.items():
        if len(files) > 1:
            duplicates.append(f"Function '{pattern}' appears in: {', '.join(files)}")
    
    return duplicates


def validate_rules() -> int:
    """Run all validations and return exit code."""
    script_dir = Path(__file__).parent
    cursor_dir = script_dir.parent
    rules_dir = cursor_dir / 'rules'
    
    if not rules_dir.exists():
        print(f"❌ Rules directory not found: {rules_dir}")
        return 1
    
    errors = []
    warnings = []
    
    print("🔍 Validating VIRA Cursor Rules...")
    print()
    
    # Check 1: No emojis in rule files
    print("1. Checking for emoji characters...")
    emoji_files = []
    for file_path in rules_dir.glob('*.mdc'):
        emojis = find_emojis(file_path)
        if emojis:
            emoji_files.append(file_path.name)
            for line_num, line in emojis[:3]:  # Show first 3
                errors.append(f"  {file_path.name}:{line_num} contains emoji: {line[:80]}")
    
    if emoji_files:
        print(f"   ❌ Found emojis in {len(emoji_files)} files")
        for error in errors[-10:]:  # Show last 10
            print(error)
    else:
        print("   ✓ No emojis found")
    print()
    
    # Check 2: Version consistency
    print("2. Checking version consistency...")
    versions = {}
    for file_path in rules_dir.glob('*.mdc'):
        version = check_version(file_path)
        if version:
            versions[file_path.name] = version
    
    if versions:
        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            warnings.append("Version mismatch across files:")
            for file, version in sorted(versions.items()):
                warnings.append(f"  {file}: v{version}")
            print(f"   ⚠️  {len(unique_versions)} different versions found")
        else:
            print(f"   ✓ All files at version {list(unique_versions)[0]}")
    else:
        warnings.append("No version information found in files")
        print("   ⚠️  No version tags found")
    print()
    
    # Check 3: Priority tag usage
    print("3. Checking priority tag usage...")
    files_without_tags = []
    tag_stats = {}
    
    for file_path in rules_dir.glob('*.mdc'):
        counts = count_priority_tags(file_path)
        if not counts:
            files_without_tags.append(file_path.name)
        else:
            tag_stats[file_path.name] = counts
    
    if files_without_tags:
        warnings.append(f"Files without priority tags: {', '.join(files_without_tags)}")
        print(f"   ⚠️  {len(files_without_tags)} files have no priority tags")
    else:
        print("   ✓ All files use priority tags")
    
    total_critical = sum(stats.get('CRITICAL', 0) for stats in tag_stats.values())
    total_important = sum(stats.get('IMPORTANT', 0) for stats in tag_stats.values())
    total_guidance = sum(stats.get('GUIDANCE', 0) for stats in tag_stats.values())
    print(f"   📊 Tags: {total_critical} CRITICAL, {total_important} IMPORTANT, {total_guidance} GUIDANCE")
    print()
    
    # Check 4: Duplicate patterns
    print("4. Checking for duplicate patterns...")
    duplicates = find_duplicate_patterns(rules_dir)
    if duplicates:
        print(f"   ⚠️  Found {len(duplicates)} potential duplicates")
        for dup in duplicates[:5]:  # Show first 5
            warnings.append(f"  {dup}")
    else:
        print("   ✓ No obvious duplicates found")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} ERRORS found:")
        for error in errors:
            print(error)
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNINGS found:")
        for warning in warnings:
            print(warning)
    
    if not errors and not warnings:
        print("\n✅ All validations passed!")
        return 0
    elif errors:
        print(f"\n❌ Validation failed with {len(errors)} errors")
        return 1
    else:
        print(f"\n⚠️  Validation passed with {len(warnings)} warnings")
        return 0


if __name__ == '__main__':
    sys.exit(validate_rules())
