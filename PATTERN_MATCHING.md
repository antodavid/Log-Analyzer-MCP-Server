# Pattern Matching Examples

## Using the MCP Server with Pattern Matching

The Log Analyzer MCP Server now supports pattern matching with wildcards (`*` and `?`) to analyze multiple log files at once.

## Example Queries for VS Code Copilot

### 1. Analyze all API logs
```
@workspace Analyze patterns in API_*.LOG
@workspace Find errors in API_*.LOG files
@workspace Show me the top 10 patterns from API logs
```

### 2. Analyze specific log types
```
@workspace What are common patterns in error_*.log files?
@workspace Find all warnings in server_*.log
@workspace Analyze API_2025*.LOG for errors
```

### 3. Direct tool usage examples

#### Analyze all API logs for patterns
```python
import asyncio
from log_analyzer_mcp_server.pattern_handler import analyze_patterns

async def main():
    result = await analyze_patterns({
        'log_file_path': 'API_*.LOG',  # Matches all API log files
        'top_n': 10,
        'min_frequency': 5
    })
    
    print(f"Files analyzed: {result['files_analyzed']}")
    print(f"Total messages: {result['summary']['total_messages_analyzed']}")
    
    for pattern in result['patterns'][:5]:
        print(f"\nPattern: {pattern['pattern']}")
        print(f"Count: {pattern['count']} ({pattern['percentage']}%)")
        print(f"Example: {pattern['examples'][0]}")

asyncio.run(main())
```

#### Find errors in all server logs
```python
import asyncio
from log_analyzer_mcp_server.log_handler import analyze_logs

async def main():
    result = await analyze_logs({
        'log_file_path': 'server_*.log',  # Matches all server log files
        'severity_filter': 'ERROR'
    })
    
    print(f"Files analyzed: {result['files_analyzed']}")
    print(f"Total errors found: {result['summary']['total_errors']}")
    
    for error in result['errors'][:10]:
        print(f"\n[{error['file']}:{error['line']}] {error['timestamp']}")
        print(f"  {error['message']}")

asyncio.run(main())
```

## Pattern Matching Rules

### Wildcards
- `*` - Matches any number of characters
- `?` - Matches exactly one character

### Examples
- `API_*.LOG` - Matches: `API_20251015.LOG`, `API_data.LOG`, etc.
- `error_?.log` - Matches: `error_1.log`, `error_2.log`, but not `error_10.log`
- `*.LOG` - Matches all .LOG files
- `app.log` - Exact filename (no wildcards)

### Path Resolution
- Relative paths are resolved against the configured log directory
- Absolute paths are used as-is
- Default log directory: `log_files/` in project root
- Override with: `export LOG_ANALYZER_LOG_DIR="/path/to/logs"`

## Query-Based File Selection

The MCP server intelligently matches patterns based on your query:

| Query | Suggested Pattern | Explanation |
|-------|------------------|-------------|
| "analyze API logs" | `API_*.LOG` | Matches all files starting with "API_" |
| "find errors in server logs" | `server_*.log` | Matches all server log files |
| "check application logs" | `app*.log` | Matches all application logs |
| "analyze today's logs" | `*_20251023*.log` | Matches logs with today's date |

## Configuration

### Environment Variables
```bash
# Set custom log directory
export LOG_ANALYZER_LOG_DIR="/var/log/myapp"

# Or in .vscode/settings.json
{
  "mcpServers": {
    "log-analyzer": {
      "env": {
        "LOG_ANALYZER_LOG_DIR": "/var/log/myapp"
      }
    }
  }
}
```

### VS Code Settings
See `.vscode/settings.json` for the complete configuration example.

## Testing

Run the pattern matching test:
```bash
python tests/test_pattern_matching.py
```

## Output Format

When analyzing multiple files, the response includes:

```json
{
  "files_analyzed": ["API_20251015DOA_0.LOG", "API_20251016DOA_0.LOG"],
  "pattern": "API_*.LOG",
  "summary": {
    "total_files_analyzed": 2,
    "total_entries_analyzed": 200,
    ...
  },
  "entries": [...],
  "errors": [...],
  "warnings": [...]
}
```

Each entry includes the source file name for traceability.
