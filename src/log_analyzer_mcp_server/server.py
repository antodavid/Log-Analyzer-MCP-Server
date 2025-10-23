"""Log Analyzer MCP Server"""
import os
import sys
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from loguru import logger

logger.remove()
logger.add(sys.stderr, level=os.getenv('FASTMCP_LOG_LEVEL', 'WARNING'))

from log_analyzer_mcp_server.pattern_handler import analyze_patterns
from log_analyzer_mcp_server.log_handler import analyze_logs

mcp = FastMCP("Log Analyzer")

@mcp.tool()
async def analyze_log_patterns(log_file_path: str, min_frequency: int = 2, max_patterns: int = 10) -> Dict[str, Any]:
    """Analyze log files to identify common patterns and message structures.
    
    Supports pattern matching like 'API_*.LOG' to analyze multiple files.
    Examples:
      - "API_*.LOG" - analyze all API log files
      - "app.log" - analyze single file
      - "error_*.log" - analyze all error logs
    
    Args:
        log_file_path: Path or pattern to log file(s) (supports * and ? wildcards)
        min_frequency: Minimum occurrences for a pattern to be reported (default: 2)
        max_patterns: Maximum number of patterns to return (default: 10)
    
    Returns:
        Dict with patterns, frequencies, examples, and summary statistics
    """
    return await analyze_patterns({"log_file_path": log_file_path, "min_frequency": min_frequency, "max_patterns": max_patterns})

@mcp.tool()
async def analyze_log_file(log_file_path: str, severity_filter: Optional[str] = None) -> Dict[str, Any]:
    """Perform detailed analysis of log files with optional filtering.
    
    Supports pattern matching like 'API_*.LOG' to analyze multiple files.
    Examples:
      - "API_*.LOG" - analyze all API log files
      - "app.log" - analyze single file
      - Query: "find errors in API logs" -> use pattern "API_*.LOG" with severity_filter="ERROR"
    
    Args:
        log_file_path: Path or pattern to log file(s) (supports * and ? wildcards)
        severity_filter: Optional filter by severity (ERROR, WARNING, INFO, DEBUG)
    
    Returns:
        Dict with log entries, errors, warnings, and summary statistics
    """
    params = {"log_file_path": log_file_path}
    if severity_filter:
        params["severity_filter"] = severity_filter
    return await analyze_logs(params)

if __name__ == "__main__":
    mcp.run()
