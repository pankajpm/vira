# Test & Validation Scripts

This directory contains scripts for testing and validating the AlignOrGap enhancement implementation.

## Scripts

### `corpus_spot_check.py`
**Purpose**: Validate that gap evidence exists in the vector store  
**Run**: `python notebooks/corpus_spot_check.py`  
**Output**: Shows retrieved chunks for gap-related queries

### `test_solution4_prompt.py`  
**Purpose**: Test enhanced prompt with strict citation requirements (Solution 4)  
**Run**: `python notebooks/test_solution4_prompt.py`  
**Output**: Single test case showing alignment/gap analysis

### `test_with_classification.py`
**Purpose**: Test full pipeline with classification enabled  
**Run**: `python notebooks/test_with_classification.py`  
**Output**: Detailed analysis showing classified evidence sections

### `smoke_test.py` ⭐
**Purpose**: Comprehensive test suite with 5 diverse business plans  
**Run**: `python notebooks/smoke_test.py`  
**Output**: Pass/fail results with quality scores

## Quick Test

```bash
cd /Users/pankaj/projects/vira
source .venv/bin/activate
python notebooks/smoke_test.py
```

Expected: **5/5 tests passed** ✅

## What Each Test Validates

- **corpus_spot_check**: Gap evidence availability
- **test_solution4_prompt**: Enhanced prompt effectiveness  
- **test_with_classification**: Classification correctness
- **smoke_test**: End-to-end system quality

All tests should pass with the current implementation.

