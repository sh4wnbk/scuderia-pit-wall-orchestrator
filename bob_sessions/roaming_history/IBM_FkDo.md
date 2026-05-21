# Unit Test Plan for Untested Functions in reboot.py

## Overview
This document outlines a comprehensive test plan for two untested functions in [`reboot.py`](reboot.py):
1. [`parse_next_options()`](reboot.py:214-272) - Lines 214-272
2. VALID_FIELDS parser in [`main()`](reboot.py:274-336) - Lines 314-323

---

## 1. Test Suite for `parse_next_options()`

### Function Signature
```python
def parse_next_options(next_value: str) -> str
```

### Purpose
Parses the NEXT field for multiple options and prompts user to select one. Handles various delimiters: " or ", commas, periods, and semicolons.

### Test Cases

#### Test 1.1: Input with " or " delimiter
**Function:** `test_parse_next_options_with_or()`
- **Input:** `"Update documentation or run tests or create examples"`
- **Expected Behavior:**
  - Detects " or " delimiter (case-insensitive)
  - Splits into 3 options: `["Update documentation", "run tests", "create examples"]`
  - Displays numbered menu (1-3)
  - In interactive mode: prompts for selection
  - In non-interactive mode: returns original value unchanged
- **Mock Requirements:** Mock `sys.stdin.isatty()` to test both interactive and non-interactive scenarios

#### Test 1.2: Input with " OR " (uppercase)
**Function:** `test_parse_next_options_with_uppercase_or()`
- **Input:** `"Fix bug OR add feature OR update docs"`
- **Expected Behavior:**
  - Case-insensitive regex should match
  - Splits into 3 options: `["Fix bug", "add feature", "update docs"]`
  - Same interactive/non-interactive behavior as Test 1.1

#### Test 1.3: Input with commas
**Function:** `test_parse_next_options_with_commas()`
- **Input:** `"Write tests, update README, deploy to staging"`
- **Expected Behavior:**
  - Detects comma delimiter
  - Splits into 3 options: `["Write tests", "update README", "deploy to staging"]`
  - Strips whitespace from each option
  - Displays numbered menu

#### Test 1.4: Input with semicolons
**Function:** `test_parse_next_options_with_semicolons()`
- **Input:** `"Review code; merge PR; update changelog"`
- **Expected Behavior:**
  - Detects semicolon delimiter
  - Splits into 3 options: `["Review code", "merge PR", "update changelog"]`
  - Strips whitespace and empty strings

#### Test 1.5: Input with multiple periods (sentences)
**Function:** `test_parse_next_options_with_periods()`
- **Input:** `"Complete feature A. Test feature B. Deploy to production."`
- **Expected Behavior:**
  - Detects multiple periods (count > 1)
  - Splits by period or semicolon
  - Filters out empty strings after stripping
  - Returns 3 options: `["Complete feature A", "Test feature B", "Deploy to production"]`

#### Test 1.6: Single option input (no delimiters)
**Function:** `test_parse_next_options_single_option()`
- **Input:** `"Complete the integration tests"`
- **Expected Behavior:**
  - No " or ", no commas, no multiple periods/semicolons
  - Returns original value unchanged: `"Complete the integration tests"`
  - Does NOT display menu or prompt

#### Test 1.7: Edge case - only one option after split
**Function:** `test_parse_next_options_one_after_split()`
- **Input:** `"Update docs or"`
- **Expected Behavior:**
  - Splits into `["Update docs", ""]`
  - After filtering, only 1 valid option remains
  - Returns original value unchanged

#### Test 1.8: Non-interactive terminal (stdin not a TTY)
**Function:** `test_parse_next_options_non_interactive()`
- **Input:** `"Option A or Option B or Option C"`
- **Mock:** `sys.stdin.isatty()` returns `False`
- **Expected Behavior:**
  - Displays menu with 3 options
  - Prints: `"(Non-interactive terminal detected — skipping selection)"`
  - Prints empty line
  - Returns original value unchanged: `"Option A or Option B or Option C"`

#### Test 1.9: Interactive selection - valid choice
**Function:** `test_parse_next_options_interactive_valid_choice()`
- **Input:** `"Task A or Task B or Task C"`
- **Mock:** `sys.stdin.isatty()` returns `True`, `input()` returns `"2"`
- **Expected Behavior:**
  - Displays menu
  - Prompts: `"Select option (1-3): "`
  - User enters `"2"`
  - Returns: `"Task B"`
  - Prints empty line before returning

#### Test 1.10: Interactive selection - invalid then valid choice
**Function:** `test_parse_next_options_interactive_invalid_then_valid()`
- **Input:** `"Task A or Task B"`
- **Mock:** `input()` returns `"5"` then `"1"`
- **Expected Behavior:**
  - First attempt: prints `"Please enter a number between 1 and 2"`
  - Second attempt: returns `"Task A"`

#### Test 1.11: Interactive selection - non-numeric input
**Function:** `test_parse_next_options_interactive_non_numeric()`
- **Input:** `"Task A or Task B"`
- **Mock:** `input()` returns `"abc"`
- **Expected Behavior:**
  - Catches `ValueError`
  - Prints: `"\nKeeping original NEXT value"`
  - Prints empty line
  - Returns original value: `"Task A or Task B"`

#### Test 1.12: Interactive selection - KeyboardInterrupt (Ctrl+C)
**Function:** `test_parse_next_options_keyboard_interrupt()`
- **Input:** `"Task A or Task B"`
- **Mock:** `input()` raises `KeyboardInterrupt`
- **Expected Behavior:**
  - Catches `KeyboardInterrupt`
  - Prints: `"\nKeeping original NEXT value"`
  - Prints empty line
  - Returns original value: `"Task A or Task B"`

#### Test 1.13: Mixed delimiters - " or " takes precedence
**Function:** `test_parse_next_options_mixed_delimiters()`
- **Input:** `"Task A, subtask 1 or Task B, subtask 2"`
- **Expected Behavior:**
  - " or " is checked first in the code
  - Splits by " or ": `["Task A, subtask 1", "Task B, subtask 2"]`
  - Commas within options are preserved

#### Test 1.14: Empty string input
**Function:** `test_parse_next_options_empty_string()`
- **Input:** `""`
- **Expected Behavior:**
  - No delimiters detected
  - Returns empty string unchanged: `""`

#### Test 1.15: Whitespace-only input
**Function:** `test_parse_next_options_whitespace_only()`
- **Input:** `"   "`
- **Expected Behavior:**
  - No delimiters detected
  - Returns whitespace unchanged: `"   "`

---

## 2. Test Suite for VALID_FIELDS Parser in `main()`

### Code Location
Lines 314-323 in [`main()`](reboot.py:274-336)

### Purpose
Parses LLM-generated structured output and filters lines to include only valid field names from `VALID_FIELDS` set. This prevents LLM preamble text from leaking into the final card.

### VALID_FIELDS Constant
```python
VALID_FIELDS = {"PROJECT", "STATE", "LAST ACTION", "NEXT", "DEAD ENDS", "DEADLINE", "NOTE"}
```

### Test Cases

#### Test 2.1: LLM preamble lines should be filtered out
**Function:** `test_valid_fields_filters_preamble()`
- **Input (LLM output):**
  ```
  Here is the structured output:
  PROJECT:     Test Project
  STATE:       In progress
  NEXT:        Complete testing
  ```
- **Expected Behavior:**
  - Line `"Here is the structured output:"` has no colon or invalid key
  - Parser skips it (no colon match)
  - Only valid fields appear in `fields` dict:
    ```python
    {
      "PROJECT": "Test Project",
      "STATE": "In progress",
      "NEXT": "Complete testing"
    }
    ```

#### Test 2.2: Valid field names should be included
**Function:** `test_valid_fields_includes_valid_fields()`
- **Input:**
  ```
  PROJECT:     Valid Project
  STATE:       Complete
  LAST ACTION: Deployed
  NEXT:        Monitor
  DEAD ENDS:   Approach A
  DEADLINE:    2026-05-20
  ```
- **Expected Behavior:**
  - All 6 fields are in `VALID_FIELDS`
  - All 6 fields appear in `fields` dict with correct values

#### Test 2.3: Invalid field names should be excluded
**Function:** `test_valid_fields_excludes_invalid_fields()`
- **Input:**
  ```
  PROJECT:     Test
  INVALID:     This should not appear
  STATE:       Done
  RANDOM:      Also excluded
  NEXT:        Continue
  ```
- **Expected Behavior:**
  - `"INVALID"` and `"RANDOM"` are not in `VALID_FIELDS`
  - Only valid fields in result:
    ```python
    {
      "PROJECT": "Test",
      "STATE": "Done",
      "NEXT": "Continue"
    }
    ```

#### Test 2.4: Mixed valid and invalid lines
**Function:** `test_valid_fields_mixed_valid_invalid()`
- **Input:**
  ```
  Based on the session:
  PROJECT:     Mixed Test
  SUMMARY:     This is invalid
  STATE:       Working
  DESCRIPTION: Also invalid
  NEXT:        Test more
  ```
- **Expected Behavior:**
  - Line 1: No colon, skipped
  - `"SUMMARY"` and `"DESCRIPTION"` not in `VALID_FIELDS`, excluded
  - Result:
    ```python
    {
      "PROJECT": "Mixed Test",
      "STATE": "Working",
      "NEXT": "Test more"
    }
    ```

#### Test 2.5: LLM adds explanatory text after fields
**Function:** `test_valid_fields_filters_trailing_text()`
- **Input:**
  ```
  PROJECT:     Test
  STATE:       Done
  NEXT:        Deploy
  
  This completes the structured output.
  ```
- **Expected Behavior:**
  - Last line has no colon, skipped
  - Only 3 valid fields in result

#### Test 2.6: Field with colon in value
**Function:** `test_valid_fields_colon_in_value()`
- **Input:**
  ```
  PROJECT:     API: Version 2.0
  STATE:       Testing phase: integration
  NEXT:        Deploy to prod: staging first
  ```
- **Expected Behavior:**
  - `partition(":")` splits on first colon only
  - Values preserve remaining colons:
    ```python
    {
      "PROJECT": "API: Version 2.0",
      "STATE": "Testing phase: integration",
      "NEXT": "Deploy to prod: staging first"
    }
    ```

#### Test 2.7: Empty field values
**Function:** `test_valid_fields_empty_values()`
- **Input:**
  ```
  PROJECT:     
  STATE:       In progress
  NEXT:        
  DEAD ENDS:   
  ```
- **Expected Behavior:**
  - Empty values after colon are stripped to `""`
  - All fields included with empty string values:
    ```python
    {
      "PROJECT": "",
      "STATE": "In progress",
      "NEXT": "",
      "DEAD ENDS": ""
    }
    ```

#### Test 2.8: Whitespace handling
**Function:** `test_valid_fields_whitespace_handling()`
- **Input:**
  ```
    PROJECT:       Test Project   
  STATE:     In progress  
      NEXT:    Continue    
  ```
- **Expected Behavior:**
  - Keys are stripped: `"PROJECT"`, `"STATE"`, `"NEXT"`
  - Values are stripped: `"Test Project"`, `"In progress"`, `"Continue"`
  - Leading/trailing whitespace removed from both

#### Test 2.9: Case sensitivity of field names
**Function:** `test_valid_fields_case_sensitive()`
- **Input:**
  ```
  project:     Should be excluded
  PROJECT:     Should be included
  Project:     Should be excluded
  STATE:       Valid
  ```
- **Expected Behavior:**
  - `VALID_FIELDS` contains uppercase only
  - Only exact matches included:
    ```python
    {
      "PROJECT": "Should be included",
      "STATE": "Valid"
    }
    ```

#### Test 2.10: NOTE field added via --note argument
**Function:** `test_valid_fields_note_argument()`
- **Input (LLM output):**
  ```
  PROJECT:     Test
  STATE:       Done
  ```
- **Command line:** `--note "planning test coverage"`
- **Expected Behavior:**
  - Parser processes LLM output normally
  - Code adds `NOTE` field after parsing (line 324-325)
  - Final result:
    ```python
    {
      "PROJECT": "Test",
      "STATE": "Done",
      "NOTE": "planning test coverage"
    }
    ```

#### Test 2.11: All valid fields present
**Function:** `test_valid_fields_all_fields_present()`
- **Input:**
  ```
  PROJECT:     Complete Test
  STATE:       All fields
  LAST ACTION: Tested
  NEXT:        Document
  DEAD ENDS:   None
  DEADLINE:    2026-05-20
  NOTE:        Manual note
  ```
- **Expected Behavior:**
  - All 7 fields in `VALID_FIELDS` are present
  - All 7 fields in result dict

#### Test 2.12: No valid fields (all invalid)
**Function:** `test_valid_fields_no_valid_fields()`
- **Input:**
  ```
  INVALID1:    Value
  INVALID2:    Value
  RANDOM:      Value
  ```
- **Expected Behavior:**
  - No fields match `VALID_FIELDS`
  - Result is empty dict: `{}`

#### Test 2.13: Lines without colons are skipped
**Function:** `test_valid_fields_no_colon_lines()`
- **Input:**
  ```
  This is a preamble line
  PROJECT:     Test
  Another line without colon
  STATE:       Done
  Final line
  ```
- **Expected Behavior:**
  - Lines 1, 3, 5 have no colon, skipped by `if ":" in line` check
  - Only lines 2 and 4 processed:
    ```python
    {
      "PROJECT": "Test",
      "STATE": "Done"
    }
    ```

---

## Test Implementation Notes

### Mocking Requirements

1. **For `parse_next_options()` tests:**
   - Mock `sys.stdin.isatty()` to control interactive vs non-interactive mode
   - Mock `input()` to simulate user input
   - Mock `print()` to verify output messages (optional, for thorough testing)

2. **For VALID_FIELDS parser tests:**
   - No mocking required - pure parsing logic
   - Can test directly by simulating the parsing loop

### Test Framework Recommendations

- Use `unittest` (matches existing [`test_debug.py`](test_debug.py) pattern)
- Use `unittest.mock.patch` for mocking
- Group tests into test classes:
  - `TestParseNextOptions` for function 1
  - `TestValidFieldsParser` for function 2

### Example Test Structure

```python
import unittest
from unittest.mock import patch, MagicMock
import reboot

class TestParseNextOptions(unittest.TestCase):
    
    @patch('sys.stdin.isatty')
    @patch('builtins.input')
    def test_parse_next_options_with_or(self, mock_input, mock_isatty):
        mock_isatty.return_value = True
        mock_input.return_value = "1"
        
        result = reboot.parse_next_options("Task A or Task B or Task C")
        
        self.assertEqual(result, "Task A")
    
    # ... more tests

class TestValidFieldsParser(unittest.TestCase):
    
    def test_valid_fields_filters_preamble(self):
        llm_output = """Here is the output:
PROJECT:     Test
STATE:       Done"""
        
        fields = {}
        for line in llm_output.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                if key in reboot.VALID_FIELDS:
                    fields[key] = val.strip()
        
        self.assertEqual(fields, {
            "PROJECT": "Test",
            "STATE": "Done"
        })
    
    # ... more tests
```

---

## Test Coverage Summary

### `parse_next_options()` - 15 test cases
- Delimiter handling: 5 tests (or, commas, semicolons, periods, mixed)
- Edge cases: 3 tests (single option, empty, whitespace)
- Interactive mode: 5 tests (valid choice, invalid choice, non-numeric, Ctrl+C, non-TTY)
- Boundary conditions: 2 tests (one option after split, uppercase OR)

### VALID_FIELDS parser - 13 test cases
- Filtering: 4 tests (preamble, invalid fields, mixed, trailing text)
- Valid fields: 2 tests (all valid, specific valid fields)
- Edge cases: 4 tests (empty values, no valid fields, no colons, case sensitivity)
- Value handling: 2 tests (colons in values, whitespace)
- Integration: 1 test (NOTE argument)

**Total: 28 test cases**

---

## Next Steps

1. Implement test suite in new file: `test_untested_functions.py`
2. Run tests to verify coverage
3. Add tests to CI/CD pipeline if applicable
4. Update [`test_debug.py`](test_debug.py) to include these new tests or keep separate
