#!/usr/bin/env python3
"""
Comprehensive demo of the Log Analyzer MCP Server with pattern matching
"""

import sys
sys.path.insert(0, 'src')

import asyncio
from log_analyzer_mcp_server.log_handler import analyze_logs
from log_analyzer_mcp_server.pattern_handler import analyze_patterns
from pathlib import Path

async def main():
    print("╔" + "═"*78 + "╗")
    print("║" + " LOG ANALYZER MCP SERVER - PATTERN MATCHING DEMO ".center(78) + "║")
    print("╚" + "═"*78 + "╝")
    print()
    
    # Demo 1: Single file analysis
    print("📁 DEMO 1: Single File Analysis")
    print("─"*80)
    result = await analyze_logs({
        'log_file_path': 'API_20251015DOA_0.LOG'
    })
    
    print(f"✓ Analyzed: {result['files_analyzed'][0].split('/')[-1]}")
    print(f"  Entries: {result['summary']['total_entries_analyzed']}")
    print(f"  Errors: {result['summary']['total_errors']}")
    print(f"  Warnings: {result['summary']['total_warnings']}")
    print()
    
    # Demo 2: Pattern matching - all API logs
    print("🔍 DEMO 2: Pattern Matching (API_*.LOG)")
    print("─"*80)
    result = await analyze_logs({
        'log_file_path': 'API_*.LOG'
    })
    
    print(f"✓ Pattern: API_*.LOG")
    print(f"  Files found: {result['summary']['total_files_analyzed']}")
    for f in result['files_analyzed']:
        print(f"    - {Path(f).name}")
    print(f"  Total entries: {result['summary']['total_entries_analyzed']}")
    print(f"  Severity: {result['summary']['severity_counts']}")
    print()
    
    # Demo 3: Pattern analysis
    print("📊 DEMO 3: Pattern Analysis")
    print("─"*80)
    pattern_result = await analyze_patterns({
        'log_file_path': 'API_*.LOG',
        'top_n': 5,
        'min_frequency': 10
    })
    
    print(f"✓ Pattern: {pattern_result['pattern']}")
    print(f"  Messages analyzed: {pattern_result['summary']['total_messages_analyzed']}")
    print(f"  Unique patterns: {pattern_result['summary']['unique_patterns']}")
    print(f"  Patterns shown: {pattern_result['summary']['patterns_shown']}")
    print()
    print("  Top 5 Patterns:")
    for i, p in enumerate(pattern_result['patterns'][:5], 1):
        print(f"    {i}. [{p['percentage']}%] {p['pattern'][:55]}...")
        print(f"       Count: {p['count']}, Threads: {p['unique_threads']}")
    print()
    
    # Demo 4: Query-based examples
    print("💬 DEMO 4: Natural Language Query Examples")
    print("─"*80)
    print("  For VS Code Copilot, you can ask:")
    print()
    print("    Query: 'Analyze API logs'")
    print("    → Pattern: API_*.LOG")
    print()
    print("    Query: 'Find errors in API logs'")
    print("    → Pattern: API_*.LOG, Filter: ERROR")
    print()
    print("    Query: 'Show common patterns in server logs'")
    print("    → Pattern: server_*.log, Tool: analyze_log_patterns")
    print()
    print("    Query: 'What are the warnings in application logs?'")
    print("    → Pattern: app*.log, Filter: WARNING")
    print()
    
    # Demo 5: Configuration info
    print("⚙️  DEMO 5: Configuration")
    print("─"*80)
    from log_analyzer_mcp_server.config import get_log_directory
    log_dir = get_log_directory()
    print(f"  Log Directory: {log_dir}")
    print(f"  Override with: export LOG_ANALYZER_LOG_DIR='/path/to/logs'")
    print()
    
    print("╔" + "═"*78 + "╗")
    print("║" + " DEMO COMPLETE - MCP Server Ready! ".center(78) + "║")
    print("╚" + "═"*78 + "╝")
    print()
    print("📖 See PATTERN_MATCHING.md for more examples")
    print("🚀 Use @workspace in VS Code Copilot to query logs")

if __name__ == '__main__':
    asyncio.run(main())
