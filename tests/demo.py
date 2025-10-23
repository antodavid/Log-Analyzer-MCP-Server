#!/usr/bin/env python3
"""
Complete demonstration of log analysis capabilities
Tests both pattern analysis and detailed log analysis tools
"""

import sys
sys.path.insert(0, 'src')

import asyncio
from log_analyzer_mcp_server.log_handler import analyze_logs
from log_analyzer_mcp_server.pattern_handler import analyze_patterns

async def main():
    log_file = 'log_files/API_20251015DOA_0.LOG'
    
    print("="*80)
    print("LOG ANALYZER MCP SERVER - DEMO")
    print("="*80)
    print()
    
    # Test 1: Pattern Analysis
    print("1. PATTERN ANALYSIS (Top 10 patterns)")
    print("-"*80)
    pattern_result = await analyze_patterns({
        'log_file_path': log_file,
        'top_n': 10
    })
    
    print(f"Total patterns found: {len(pattern_result['patterns'])}")
    print(f"Total messages analyzed: {pattern_result['summary']['total_messages_analyzed']}")
    print(f"Unique patterns: {pattern_result['summary']['unique_patterns']}")
    print()
    
    for i, pattern in enumerate(pattern_result['patterns'][:5], 1):
        print(f"{i}. Pattern: {pattern['pattern'][:70]}...")
        print(f"   Count: {pattern['count']} ({pattern['percentage']:.1f}%)")
        print(f"   Severity counts: {pattern['severity_counts']}")
        print(f"   Example: {pattern['examples'][0][:70]}..." if pattern['examples'] else "")
        print()
    
    print()
    
    # Test 2: Detailed Log Analysis
    print("2. DETAILED LOG ANALYSIS")
    print("-"*80)
    log_result = await analyze_logs({
        'log_file_path': log_file
    })
    
    summary = log_result['summary']
    print(f"Total entries analyzed: {summary['total_entries_analyzed']}")
    print(f"Entries shown: {summary['entries_shown']}")
    print(f"Total errors: {summary['total_errors']}")
    print(f"Total warnings: {summary['total_warnings']}")
    time_range = summary.get('time_range', {})
    if time_range:
        print(f"Time range: {time_range.get('start', 'N/A')} to {time_range.get('end', 'N/A')}")
    print(f"Severity distribution: {summary['severity_counts']}")
    print()
    
    print("First 5 log entries:")
    for entry in log_result['entries'][:5]:
        print(f"  [{entry['severity']}] {entry['message'][:70]}...")
    
    print()
    print("="*80)
    print("DEMO COMPLETE - MCP Server is ready for VS Code integration!")
    print("="*80)
    print()
    print("Try these commands in VS Code Copilot:")
    print("  @workspace Analyze log_files/API_20251015DOA_0.LOG for patterns")
    print("  @workspace Show top patterns from log_files/API_20251015DOA_0.LOG")
    print("  @workspace What are the most common messages in the log?")

if __name__ == '__main__':
    asyncio.run(main())
