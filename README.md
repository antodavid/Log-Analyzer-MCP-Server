# Log Analyzer MCP Server

A Model Context Protocol (MCP) server for analyzing log files using the FastMCP framework.

## Features
- FastMCP 2.0 based server implementation
- Log file pattern analysis and detection
- Detailed log file analysis with filtering
- STDIO transport for VS Code integration
- Async tool execution

## Requirements
- Python 3.10+
- FastMCP 2.0+
- Loguru

## Installation
```bash
# Clone the repository
git clone https://github.com/antodavid/Log-Analyzer-MCP-Server.git
cd Log-Analyzer-MCP-Server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[dev]
```

## Running the server
```bash
# Run directly
python src/log_analyzer_mcp_server/server.py

# Or with environment variables
FASTMCP_LOG_LEVEL=INFO PYTHONPATH=src python src/log_analyzer_mcp_server/server.py
```

## Configuration

### Log Directory
The log directory can be configured via environment variable:
```bash
export LOG_ANALYZER_LOG_DIR="/path/to/your/logs"
```

Default: `log_files/` in the project root

## Available Tools

### analyze_log_patterns
Analyzes log files to identify common patterns and group similar messages.

**Supports pattern matching with wildcards!**

**Parameters:**
- `log_file_path` (str): Path or pattern to log file(s) (supports `*` and `?` wildcards)
  - Examples: `"API_*.LOG"`, `"app.log"`, `"error_*.log"`
- `min_frequency` (int, optional): Minimum number of occurrences for a pattern (default: 2)
- `max_patterns` (int, optional): Maximum number of patterns to return (default: 10)

**Returns:**
- Dictionary containing identified patterns with their frequencies, examples, and file list

**Examples:**
```python
# Analyze single file
result = await analyze_log_patterns(
    log_file_path="app.log",
    min_frequency=3,
    max_patterns=15
)

# Analyze all API logs
result = await analyze_log_patterns(
    log_file_path="API_*.LOG",
    max_patterns=20
)
```

### analyze_log_file
Performs detailed analysis of log files with optional filtering.

**Supports pattern matching with wildcards!**

**Parameters:**
- `log_file_path` (str): Path or pattern to log file(s) (supports `*` and `?` wildcards)
  - Examples: `"API_*.LOG"`, `"app.log"`, `"server_*.log"`
- `severity_filter` (str, optional): Filter by severity level (ERROR, WARNING, INFO, DEBUG)
- `start_time` (str, optional): Start time for log analysis (ISO format)
- `end_time` (str, optional): End time for log analysis (ISO format)

**Returns:**
- Dictionary containing detailed log analysis results and file list

**Examples:**
```python
# Analyze single file for errors
result = await analyze_log_file(
    log_file_path="app.log",
    severity_filter="ERROR"
)

# Analyze all API logs for warnings
result = await analyze_log_file(
    log_file_path="API_*.LOG",
    severity_filter="WARNING"
)
```

## Testing
```bash
pytest -q
```

## Extending
Add new tool modules under `log_analyzer_mcp_server/tools/` and register them in `server.py`.

## VS Code Integration

This MCP server integrates with VS Code through the Model Context Protocol. 

### Setup

1. Add the following configuration to your workspace `.vscode/settings.json`:

```json
{
    "mcpServers": {
        "log-analyzer": {
            "command": "/absolute/path/to/.venv/bin/python",
            "args": [
                "/absolute/path/to/src/log_analyzer_mcp_server/server.py"
            ],
            "env": {
                "PYTHONPATH": "/absolute/path/to/src",
                "FASTMCP_LOG_LEVEL": "INFO"
            }
        }
    }
}
```

2. Restart VS Code for the changes to take effect

3. The MCP server will automatically start when VS Code's Copilot needs it

### Usage with Copilot

You can now ask Copilot to analyze your log files:

- "Analyze the patterns in /path/to/app.log"
- "Show me common error patterns in this log file"
- "What are the most frequent messages in the server logs?"
- "Analyze errors from the last hour"

The server will use its pattern detection and analysis capabilities to provide insights.

## License
MIT
