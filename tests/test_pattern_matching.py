#!/usr/bin/env python3
"""Test the new pattern matching functionality"""

import sys
sys.path.insert(0, 'src')

import asyncio
from log_analyzer_mcp_server.log_handler import analyze_logs, find_log_files
from log_analyzer_mcp_server.pattern_handler import analyze_patterns
from pathlib import Path

async def main():
    print("="*80)
    print("TESTING PATTERN MATCHING FUNCTIONALITY")
    print("="*80)
    print()
    
    # Test 1: Find files with pattern
    print("1. Testing file pattern matching:")
    print("-"*80)
    pattern = "API_*.LOG"
    files = find_log_files(pattern)
    print(f"Pattern: {pattern}")
    print(f"Found {len(files)} files:")
    for f in files:
        print(f"  - {f.name}")
    print()
    
    # Test 2: Analyze with pattern
    print("2. Testing log analysis with pattern:")
    print("-"*80)
    result = await analyze_logs({
        'log_file_path': 'API_*.LOG'
    })
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Files analyzed: {result['summary']['total_files_analyzed']}")
        print(f"Files: {', '.join([Path(f).name for f in result['files_analyzed']])}")
        print(f"Total entries: {result['summary']['total_entries_analyzed']}")
        print(f"Errors: {result['summary']['total_errors']}")
        print(f"Warnings: {result['summary']['total_warnings']}")
        print(f"Severity: {result['summary']['severity_counts']}")
    print()
    
    # Test 3: Pattern analysis
    print("3. Testing pattern analysis with wildcards:")
    print("-"*80)
    pattern_result = await analyze_patterns({
        'log_file_path': 'API_*.LOG',
        'top_n': 5
    })
    
    if 'error' in pattern_result:
        print(f"Error: {pattern_result['error']}")
    else:
        print(f"Files analyzed: {pattern_result['summary']['total_files_analyzed']}")
        print(f"Total messages: {pattern_result['summary']['total_messages_analyzed']}")
        print(f"Unique patterns: {pattern_result['summary']['unique_patterns']}")
        print()
        print("Top 5 patterns:")
        for i, p in enumerate(pattern_result['patterns'][:5], 1):
            print(f"  {i}. {p['pattern'][:60]}... ({p['count']} times, {p['percentage']}%)")
    
    print()
    print("="*80)
    print("TESTS COMPLETE!")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(main())
