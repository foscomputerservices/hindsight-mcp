# Hindsight MCP Server

A Model Context Protocol (MCP) server that maintains a searchable knowledge base of development learnings, common errors, coding patterns, and best practices. Built for use with Claude Desktop and other MCP-compatible clients.

## Features

- **Full-Text Search**: Fast SQLite FTS5-powered search across all knowledge types
- **Lessons Database**: Store patterns, practices, gotchas, and architectural decisions
- **Error Tracking**: Record common errors with solutions and track occurrence frequency
- **Swift Patterns**: iOS/Swift-specific patterns with version constraints
- **Session Context**: Link knowledge to development sessions
- **Multi-Technology**: Organize by technology (Swift, Python, Xcode, etc.)
- **Tag System**: Flexible categorization with tags
- **Export/Import**: JSON export for backup and migration

## Requirements

- Python 3.10+
- macOS, Linux, or Windows
- Claude Desktop (or other MCP client)

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/foscomputerservices/hindsight-mcp.git
cd hindsight-mcp

# Run the installer
./install.sh
```

The installer:
- Creates `~/.hindsight/` runtime directory
- Copies server files
- Sets up Python virtual environment
- Initializes the database

Then configure your MCP client (see below) and restart it.

### Manual Installation

If you prefer manual setup:

```bash
# Clone anywhere
git clone https://github.com/foscomputerservices/hindsight-mcp.git ~/hindsight-mcp

# Create runtime directory
mkdir -p ~/.hindsight

# Copy server files
cp ~/hindsight-mcp/server.py ~/.hindsight/
cp ~/hindsight-mcp/schema.sql ~/.hindsight/
cp ~/hindsight-mcp/config.json ~/.hindsight/

# Set up Python environment
python3 -m venv ~/.hindsight/.venv
~/.hindsight/.venv/bin/pip install mcp pydantic

# Initialize database
sqlite3 ~/.hindsight/knowledge.db < ~/.hindsight/schema.sql
```

### Updating

To update to the latest version:

```bash
cd /path/to/hindsight-mcp
git pull
./install.sh
```

Your database and config are preserved during updates.

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hindsight": {
      "command": "/Users/YOUR_USERNAME/.hindsight/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/.hindsight/server.py"]
    }
  }
}
```

Replace `YOUR_USERNAME` with your actual username.

Restart Claude Desktop after configuration.

### Claude Code (CLI) Configuration

**Option 1: CLI command**
```bash
claude mcp add hindsight -- ~/.hindsight/.venv/bin/python ~/.hindsight/server.py
```

**Option 2: Project-level config** (`.mcp.json` in project root)
```json
{
  "mcpServers": {
    "hindsight": {
      "type": "stdio",
      "command": "/Users/YOUR_USERNAME/.hindsight/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/.hindsight/server.py"]
    }
  }
}
```

**Option 3: User-level config** (`~/.claude/settings.json`)
```json
{
  "mcpServers": {
    "hindsight": {
      "type": "stdio",
      "command": "/Users/YOUR_USERNAME/.hindsight/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/.hindsight/server.py"]
    }
  }
}
```

Verify with: `claude mcp list`

## Available Tools

### Query Tools

| Tool | Description |
|------|-------------|
| `query_knowledge` | Search across all knowledge types with FTS |
| `search_errors` | Find errors by pattern or technology |
| `get_swift_patterns` | Retrieve Swift patterns with version filtering |
| `list_technologies` | List technologies with entry counts |
| `list_tags` | List tags with usage counts |
| `get_statistics` | Dashboard-style analytics |

### Add/Update Tools

| Tool | Description |
|------|-------------|
| `add_lesson` | Add a new lesson (pattern, practice, gotcha, decision) |
| `add_common_error` | Record an error with solution |
| `add_swift_pattern` | Add Swift pattern with code example |
| `add_session_context` | Link a development session |
| `update_lesson` | Update existing lesson |
| `increment_error_count` | Track error occurrence |

### Export Tool

| Tool | Description |
|------|-------------|
| `export_knowledge` | Export as JSON with filtering |

## Usage Examples

### Adding a Lesson

```
Add a lesson about SwiftUI state management:
- Title: "SwiftUI State Management"
- Content: "Use @State for local view state, @Binding for child views..."
- Category: pattern
- Technology: swift
- Tags: swiftui, state-management
```

### Searching Knowledge

```
Search for "memory leak" in the knowledge base
```

```
Find Swift errors related to "actor isolation"
```

### Recording an Error

```
Add a common error:
- Technology: swift
- Error: "Publishing changes from background threads is not allowed"
- Solution: "Use MainActor.run or @MainActor annotation"
```

### Querying Patterns

```
Show Swift patterns for iOS 17+ that relate to observation
```

## Configuration

### config.json

```json
{
  "database": {
    "path": "~/.hindsight/knowledge.db",
    "connection_timeout": 30,
    "busy_timeout": 5000
  },
  "search": {
    "default_limit": 10,
    "max_limit": 100
  },
  "logging": {
    "level": "INFO",
    "file": "~/.hindsight/logs/hindsight.log"
  }
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `HINDSIGHT_DB_PATH` | Override database path |
| `HINDSIGHT_LOG_LEVEL` | Override log level (DEBUG, INFO, WARNING, ERROR) |
| `HINDSIGHT_LOG_FILE` | Override log file path |

## Backup

### Manual Backup

```bash
~/.hindsight/backup.sh
```

### Scheduled Backups (macOS)

```bash
# Install daily backup at 3:00 AM
~/.hindsight/setup-backup-schedule.sh install

# Check status
~/.hindsight/setup-backup-schedule.sh status

# Uninstall
~/.hindsight/setup-backup-schedule.sh uninstall
```

Backups are stored in `~/.hindsight/backups/` with 30-day rotation.

## Database Schema

### Tables

- **lessons** - Development learnings with categories
- **common_errors** - Error patterns with solutions
- **swift_patterns** - Swift/iOS patterns with version constraints
- **sessions** - Development session context
- **tags** - Categorization tags
- **lesson_tags** - Tag associations

### Full-Text Search

FTS5 virtual tables provide fast search:
- `lessons_fts` - Search lessons by title, content, technology
- `errors_fts` - Search errors by pattern, solution, cause
- `patterns_fts` - Search patterns by name, description

## Development

Development happens in the cloned repository. The runtime (`~/.hindsight/`) only contains what's needed to run the server.

### Repository Structure

```
hindsight-mcp/              # Source repository
├── server.py               # MCP server implementation
├── schema.sql              # Database schema
├── config.json             # Default configuration
├── install.sh              # Installation script
├── backup.sh               # Backup script
├── setup-backup-schedule.sh
├── test-data.sql           # Sample seed data
├── requirements.txt        # Python dependencies
├── tests/                  # Test suite
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_tools.py
│   ├── test_fts.py
│   └── test_performance.py
├── docs/                   # Documentation
└── .claude/                # Development session history
```

### Runtime Structure

```
~/.hindsight/               # Runtime (created by install.sh)
├── server.py               # Copied from repo
├── schema.sql              # Copied from repo
├── config.json             # Local config (preserved on update)
├── knowledge.db            # SQLite database
├── .venv/                  # Python virtual environment
├── logs/                   # Log files
└── backups/                # Database backups
```

### Running Tests

```bash
cd /path/to/hindsight-mcp

# Set up test environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# Run fast tests only
pytest tests/ -v -m "not slow"

# Run with coverage
pytest tests/ --cov=server --cov-report=html
```

### Loading Seed Data

```bash
sqlite3 ~/.hindsight/knowledge.db < test-data.sql
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Uses SQLite FTS5 for full-text search
