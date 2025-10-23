#!/usr/bin/env python3
"""Check severity distribution"""

import sys
sys.path.insert(0, 'src')

from log_analyzer_mcp_server.log_handler import parse_log_line
from collections import Counter

severity_counts = Counter()

with open('log_files/API_20251015DOA_0.LOG', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f, 1):
        result = parse_log_line(line.strip(), i)
        if result:
            severity_counts[result.severity] += 1

print("Severity Distribution:")
print("="*40)
for severity, count in severity_counts.most_common():
    print(f"{severity:10s}: {count:6d}")
