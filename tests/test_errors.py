#!/usr/bin/env python3
"""Test error detection in log file"""

import sys
sys.path.insert(0, 'src')

from log_analyzer_mcp_server.log_handler import parse_log_line

print("Scanning log file for errors and warnings...")
print("="*80)

errors = []
warnings = []
total_lines = 0
parsed_lines = 0

with open('log_files/API_20251015DOA_0.LOG', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f, 1):
        total_lines = i
        result = parse_log_line(line.strip(), i)
        
        if result:
            parsed_lines += 1
            if result.severity == 'ERROR':
                errors.append((i, result.message[:100]))
            elif result.severity == 'WARNING':
                warnings.append((i, result.message[:100]))

print(f"Total lines: {total_lines}")
print(f"Parsed lines: {parsed_lines} ({parsed_lines*100//total_lines}%)")
print(f"Errors found: {len(errors)}")
print(f"Warnings found: {len(warnings)}")
print()

if errors:
    print("First 10 ERRORS:")
    print("-"*80)
    for line_num, msg in errors[:10]:
        print(f"  Line {line_num}: {msg}")
    print()

if warnings:
    print("First 10 WARNINGS:")
    print("-"*80)
    for line_num, msg in warnings[:10]:
        print(f"  Line {line_num}: {msg}")
