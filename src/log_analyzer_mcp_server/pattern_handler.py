"""Pattern analysis handler for log files.

This module provides tools for analyzing log patterns and identifying common message structures.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
from log_analyzer_mcp_server.config import resolve_log_path, get_log_directory

@dataclass
class Pattern:
    pattern_key: str
    count: int = 0
    examples: List[str] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    severity_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    thread_ids: set = field(default_factory=set)

def normalize_message(message: str) -> str:
    """Normalize log message to create pattern by replacing variable parts."""
    # Replace numbers with placeholder
    message = re.sub(r'\b\d+\b', '<NUM>', message)
    
    # Replace hexadecimal values
    message = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', message)
    
    # Replace UUIDs/GUIDs
    message = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>', message, flags=re.IGNORECASE)
    
    # Replace IP addresses
    message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\b', '<IP:PORT>', message)
    message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', message)
    
    # Replace timestamps in various formats
    message = re.sub(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}', '<TIMESTAMP>', message)
    
    # Replace file paths
    message = re.sub(r'[A-Za-z]:\\[\w\\.]+', '<PATH>', message)
    
    # Replace common variable patterns
    message = re.sub(r'ReqID:\d+', 'ReqID:<NUM>', message)
    message = re.sub(r'duration of \d+', 'duration of <NUM>', message)
    message = re.sub(r'v:\d+', 'v:<NUM>', message)
    message = re.sub(r'l:\d+', 'l:<NUM>', message)
    
    return message

def parse_log_line(line: str, line_num: int) -> Optional[Tuple[datetime, str, str, str]]:
    """Parse log line and return (timestamp, thread_id, severity, message)."""
    # Skip non-log lines
    if not line or line.startswith('&') or line.startswith('Version '):
        return None
    
    pattern = r'^(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+\((\w+)\)\s+(.+?)(?:\(([IDWEF]),.*?\))?(?:\(Z,.*?\))?$'
    
    match = re.match(pattern, line)
    if not match:
        return None
    
    timestamp_str, thread_id, message, severity_char = match.groups()
    
    try:
        timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S.%f')
    except ValueError:
        return None
    
    severity_map = {
        'I': 'INFO',
        'D': 'DEBUG',
        'W': 'WARNING',
        'E': 'ERROR',
        'F': 'FATAL'
    }
    severity = severity_map.get(severity_char, 'INFO') if severity_char else 'INFO'
    
    return timestamp, thread_id, severity, message.strip()

def find_log_files(pattern: str) -> List[Path]:
    """
    Find log files matching a pattern.
    
    Args:
        pattern: File pattern (e.g., "API_*.LOG", "app.log")
    
    Returns:
        List of Path objects matching the pattern
    """
    resolved_path = resolve_log_path(pattern)
    
    # If it's an exact file, return it
    if resolved_path.exists() and resolved_path.is_file():
        return [resolved_path]
    
    # If pattern contains wildcards, use glob
    if '*' in pattern or '?' in pattern:
        # Get the parent directory and pattern
        if resolved_path.is_absolute():
            parent = resolved_path.parent
            pattern_name = resolved_path.name
        else:
            parent = get_log_directory()
            pattern_name = pattern
        
        matching_files = list(parent.glob(pattern_name))
        return sorted([f for f in matching_files if f.is_file()])
    
    # Not found
    return []

async def analyze_patterns(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze log files for patterns and trends.
    
    Supports pattern matching like 'API_*.LOG' to analyze multiple files.
    
    Args:
        arguments: Dictionary containing:
            - log_file_path: Path or pattern to log file(s) (e.g., "API_*.LOG")
            - min_frequency: Optional minimum frequency for pattern reporting
            - max_patterns: Optional maximum number of patterns to return
            
    Returns:
        Dict containing:
            - patterns: List of identified patterns with counts and examples
            - summary: Overall summary statistics
            - files_analyzed: List of files that were analyzed
    """
    log_file_path = arguments.get('log_file_path')
    min_frequency = arguments.get('min_frequency', 2)
    max_patterns = arguments.get('max_patterns', 10)
    
    if not log_file_path:
        return {"error": "log_file_path is required"}
    
    # Find matching log files
    log_files = find_log_files(log_file_path)
    
    if not log_files:
        return {"error": f"No log files found matching: {log_file_path}"}
    
    patterns_dict: Dict[str, Pattern] = {}
    total_messages = 0
    severity_counter = Counter()
    files_analyzed = []
    
    try:
        # Process each matching file
        for log_path in log_files:
            files_analyzed.append(str(log_path))
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    parsed = parse_log_line(line, line_num)
                    if not parsed:
                        continue
                    
                    timestamp, thread_id, severity, message = parsed
                    total_messages += 1
                    severity_counter[severity] += 1
                    
                    # Normalize message to create pattern
                    pattern_key = normalize_message(message)
                    
                    # Track pattern
                    if pattern_key not in patterns_dict:
                        patterns_dict[pattern_key] = Pattern(
                            pattern_key=pattern_key,
                            first_seen=timestamp,
                            last_seen=timestamp
                        )
                    
                    pattern = patterns_dict[pattern_key]
                    pattern.count += 1
                    pattern.last_seen = timestamp
                    pattern.severity_counts[severity] += 1
                    pattern.thread_ids.add(thread_id)
                    
                    # Store example (keep only a few)
                    if len(pattern.examples) < 3:
                        pattern.examples.append(message)
                    
                    # Limit processing for very large files
                    if total_messages >= 10000:
                        break
            
            # Stop if we've processed enough messages
            if total_messages >= 10000:
                break
    
    except Exception as e:
        return {"error": f"Error reading log file: {str(e)}"}
    
    # Filter and sort patterns
    filtered_patterns = [
        p for p in patterns_dict.values()
        if p.count >= min_frequency
    ]
    
    # Sort by count (descending)
    filtered_patterns.sort(key=lambda x: x.count, reverse=True)
    
    # Limit to max_patterns
    top_patterns = filtered_patterns[:max_patterns]
    
    # Format output
    patterns_output = []
    for pattern in top_patterns:
        patterns_output.append({
            "pattern": pattern.pattern_key,
            "count": pattern.count,
            "percentage": round((pattern.count / total_messages) * 100, 2) if total_messages > 0 else 0,
            "examples": pattern.examples,
            "severity_counts": dict(pattern.severity_counts),
            "unique_threads": len(pattern.thread_ids),
            "first_seen": pattern.first_seen.isoformat() if pattern.first_seen else None,
            "last_seen": pattern.last_seen.isoformat() if pattern.last_seen else None
        })
    
    return {
        "files_analyzed": files_analyzed,
        "pattern": log_file_path,
        "patterns": patterns_output,
        "summary": {
            "total_files_analyzed": len(files_analyzed),
            "total_messages_analyzed": total_messages,
            "unique_patterns": len(patterns_dict),
            "patterns_shown": len(patterns_output),
            "min_frequency_threshold": min_frequency,
            "severity_distribution": dict(severity_counter),
            "top_severities": [s for s, _ in severity_counter.most_common(3)]
        }
    }