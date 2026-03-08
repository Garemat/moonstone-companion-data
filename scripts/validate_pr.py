#!/usr/bin/env python3
"""
Validate that a PR description meets the template requirements:
- At least one 'Type of Change' checkbox is checked
- All 'Checklist' items are checked

Usage:
    PR_BODY="..." python3 scripts/validate_pr.py
"""

import os
import sys

body = os.environ.get("PR_BODY", "")

type_section = ""
checklist_section = ""
in_type = in_checklist = False

for line in body.splitlines():
    if line.startswith("## Type of Change"):
        in_type, in_checklist = True, False
    elif line.startswith("## Checklist"):
        in_type, in_checklist = False, True
    elif line.startswith("## "):
        in_type = in_checklist = False

    if in_type:
        type_section += line + "\n"
    if in_checklist:
        checklist_section += line + "\n"

errors = []

if "- [x]" not in type_section:
    errors.append("Please select at least one 'Type of Change' in your PR description.")

if "- [ ]" in checklist_section:
    errors.append("Please ensure all items in the 'Checklist' are completed.")

if errors:
    for msg in errors:
        print(f"::error::Validation Failed: {msg}")
    sys.exit(1)

print("PR template validation passed.")
