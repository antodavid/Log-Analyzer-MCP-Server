"""Configuration for Log Analyzer MCP Server"""

import os
from pathlib import Path

# Default log directory
DEFAULT_LOG_DIR = os.getenv(
    "LOG_ANALYZER_LOG_DIR",
    str(Path(__file__).parent.parent.parent / "log_files")
)

def get_log_directory() -> Path:
    """Get the configured log directory path."""
    return Path(DEFAULT_LOG_DIR)

def resolve_log_path(log_file_pattern: str) -> Path:
    """
    Resolve a log file pattern to absolute path.
    
    If the pattern is absolute, use it as-is.
    If relative, resolve it against the configured log directory.
    
    Args:
        log_file_pattern: File path or pattern (e.g., "API_*.LOG", "app.log")
    
    Returns:
        Resolved Path object
    """
    path = Path(log_file_pattern)
    
    # If absolute path, use it directly
    if path.is_absolute():
        return path
    
    # If relative, resolve against log directory
    return get_log_directory() / log_file_pattern
