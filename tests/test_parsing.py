#!/usr/bin/env python3
"""Simple test script for log parsing functionality"""

import sys
sys.path.insert(0, 'src')

from log_analyzer_mcp_server.log_handler import parse_log_line
from log_analyzer_mcp_server.pattern_handler import normalize_message

# Test log parsing
test_lines = [
    "10/15/2025 00:00:01.313 (00000025) GetComponentStatus method ran for a duration of 5 ms (I,API.NES.Serv.Telemetry.TelemetryEngine)",
    "10/15/2025 00:00:05.500 (00000042) Connection failed to server 192.168.1.100:8080 (E,API.Network.Connection)",
    "10/15/2025 00:00:10.123 (00000055) Warning: Timeout occurred after 5000ms (W,API.Services.Timeout)"
]

print("Testing log line parsing:")
print("-" * 80)
for i, line in enumerate(test_lines):
    result = parse_log_line(line, i+1)
    if result:
        print(f"✓ Parsed: {result.severity} - {result.message[:50]}...")
    else:
        print(f"✗ Failed to parse: {line[:50]}...")

print("\n" + "="*80)
print("Testing message normalization:")
print("-" * 80)

test_messages = [
    "GetComponentStatus method ran for a duration of 5 ms",
    "Connection failed to server 192.168.1.100:8080",
    "Processing request ID 12345-67890-abcdef",
    "Event at 10/15/2025 00:00:01.313 completed"
]

for msg in test_messages:
    normalized = normalize_message(msg)
    print(f"Original:   {msg}")
    print(f"Normalized: {normalized}")
    print()

print("="*80)
print("Reading actual log file (first 10 lines):")
print("-" * 80)

with open('log_files/API_20251015DOA_0.LOG', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if i >= 10:
            break
        result = parse_log_line(line.strip(), i+1)
        if result:
            print(f"Line {i+1}: [{result.severity}] {result.message[:60]}...")
        else:
            print(f"Line {i+1}: [UNPARSED] {line.strip()[:60]}...")
