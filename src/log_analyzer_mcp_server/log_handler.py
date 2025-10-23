"""Log analysis handler for processing log files.

This module provides tools for analyzing log files and extracting relevant information.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import re
from collections import Counter
import glob
from log_analyzer_mcp_server.config import resolve_log_path, get_log_directory

@dataclass
class LogEntry:
    timestamp: datetime
    thread_id: str
    severity: str
    message: str
    line_number: int
    details: Optional[Dict[str, Any]] = None

def parse_log_line(line: str, line_num: int) -> Optional[LogEntry]:
    """Parse a single log line into structured data."""
    # Skip non-log lines (header, metadata, assembly info)
    if not line or line.startswith('&') or line.startswith('Version '):
        return None
    
    # Pattern: MM/DD/YYYY HH:MM:SS.mmm (THREADID) Message(SEVERITY,...)
    # The severity marker can be followed by (Z,...) metadata which we ignore
    pattern = r'^(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+\((\w+)\)\s+(.+?)(?:\(([IDWEF]),.*?\))?(?:\(Z,.*?\))?$'
    match = re.match(pattern, line)
    
    if not match:
        return None
    
    timestamp_str, thread_id, message, severity_char = match.groups()
    
    # Map severity character to full name
    severity_map = {
        'I': 'INFO',
        'D': 'DEBUG',
        'W': 'WARNING',
        'E': 'ERROR',
        'F': 'FATAL'
    }
    severity = severity_map.get(severity_char, 'INFO') if severity_char else 'INFO'
    
    # Parse timestamp
    timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S.%f')
    
    return LogEntry(
        line_number=line_num,
        timestamp=timestamp,
        thread_id=thread_id,
        severity=severity,
        message=message.strip()
    )
    
    match = re.match(pattern, line)
    if not match:
        return None
    
    timestamp_str, thread_id, message, severity_marker = match.groups()
    
    # Parse timestamp
    try:
        timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S.%f')
    except ValueError:
        return None
    
    # Extract severity
    severity_map = {
        'I': 'INFO',
        'D': 'DEBUG',
        'W': 'WARNING',
        'E': 'ERROR',
        'F': 'FATAL'
    }
    severity = severity_map.get(severity_marker[1], 'UNKNOWN')
    
    return LogEntry(
        timestamp=timestamp,
        thread_id=thread_id,
        severity=severity,
        message=message.strip(),
        line_number=line_num
    )

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

async def analyze_logs(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze log files for specific patterns or information.
    
    Supports pattern matching like 'API_*.LOG' to analyze multiple files.
    
    Args:
        arguments: Dictionary containing:
            - log_file_path: Path or pattern to log file(s) (e.g., "API_*.LOG")
            - severity_filter: Optional severity level to filter by
            - start_time: Optional start time (ISO format)
            - end_time: Optional end time (ISO format)
            
    Returns:
        Dict containing:
            - entries: List of matching log entries
            - summary: Analysis summary with statistics
            - files_analyzed: List of files that were analyzed
    """
    log_file_path = arguments.get('log_file_path')
    severity_filter = arguments.get('severity_filter')
    start_time = arguments.get('start_time')
    end_time = arguments.get('end_time')
    
    if not log_file_path:
        return {"error": "log_file_path is required"}
    
    # Find matching log files
    log_files = find_log_files(log_file_path)
    
    if not log_files:
        return {"error": f"No log files found matching: {log_file_path}"}
    
    # Parse time filters
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None
    
    entries = []
    severity_counts = Counter()
    error_entries = []
    warning_entries = []
    files_analyzed = []
    
    try:
        # Process each matching file
        for log_path in log_files:
            files_analyzed.append(str(log_path))
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    entry = parse_log_line(line, line_num)
                    if not entry:
                        continue
                    
                    # Apply time filters
                    if start_dt and entry.timestamp < start_dt:
                        continue
                    if end_dt and entry.timestamp > end_dt:
                        continue
                    
                    # Count by severity
                    severity_counts[entry.severity] += 1
                    
                    # Apply severity filter
                    if severity_filter and entry.severity != severity_filter:
                        continue
                    
                    # Collect errors and warnings
                    if entry.severity == 'ERROR':
                        error_entries.append({
                            "file": str(log_path.name),
                            "line": entry.line_number,
                            "timestamp": entry.timestamp.isoformat(),
                            "thread_id": entry.thread_id,
                            "message": entry.message
                        })
                    elif entry.severity == 'WARNING':
                        warning_entries.append({
                            "file": str(log_path.name),
                            "line": entry.line_number,
                            "timestamp": entry.timestamp.isoformat(),
                            "thread_id": entry.thread_id,
                            "message": entry.message
                        })
                    
                    entries.append({
                        "file": str(log_path.name),
                        "line": entry.line_number,
                        "timestamp": entry.timestamp.isoformat(),
                        "thread_id": entry.thread_id,
                        "severity": entry.severity,
                        "message": entry.message
                    })
                    
                    # Limit entries to prevent overwhelming output
                    if len(entries) >= 100:
                        break
            
            # Stop if we've collected enough entries
            if len(entries) >= 100:
                break
    
    except Exception as e:
        return {"error": f"Error reading log file: {str(e)}"}
    
    # Get time range
    time_range = {}
    if entries:
        timestamps = [datetime.fromisoformat(e['timestamp']) for e in entries]
        time_range = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat()
        }
    
    return {
        "files_analyzed": files_analyzed,
        "pattern": log_file_path,
        "entries": entries[:50],  # Return first 50 entries
        "errors": error_entries[:20],  # Return first 20 errors
        "warnings": warning_entries[:20],  # Return first 20 warnings
        "summary": {
            "total_files_analyzed": len(files_analyzed),
            "total_entries_analyzed": len(entries),
            "total_errors": len(error_entries),
            "total_warnings": len(warning_entries),
            "severity_counts": dict(severity_counts),
            "time_range": time_range,
            "entries_shown": min(50, len(entries))
        }
    }