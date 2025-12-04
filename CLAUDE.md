# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hindsight is an MCP (Model Context Protocol) server that maintains a searchable knowledge base of development learnings, common errors, Swift patterns, and best practices. It uses SQLite with FTS5 for full-text search and runs as a stdio-based MCP server for Claude Desktop and Claude Code.

## Commands

### Running Tests
```bash
# All tests
pytest tests/ -v

# Fast tests only (excludes slow performance benchmarks)
pytest tests/ -v -m "not slow"

# Single test file
pytest tests/test_tools.py -v

# With coverage
pytest tests/ --cov=server --cov-report=html
```

### Installation

**Homebrew (recommended)**
```bash
brew tap foscomputerservices/tap
brew install hindsight-mcp
hindsight-init  # Initialize database and configure Claude
```

**Manual**
```bash
./install.sh  # Copies to ~/.hindsight/, creates venv, initializes DB
```

### Manual Setup (Development)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Database Operations
```bash
# Initialize/reset database
sqlite3 ~/.hindsight/knowledge.db < schema.sql

# Load test data
sqlite3 ~/.hindsight/knowledge.db < test-data.sql

# Backup
~/.hindsight/backup.sh
```

## Architecture

### Single-File Server
All MCP tool implementations are in `server.py`. The `KnowledgeBaseServer` class handles database operations, and the MCP server is registered with `@server.list_tools()` and `@server.call_tool()` decorators.

### Database Schema
- **lessons** - Development learnings with categories (pattern, practice, gotcha, decision)
- **common_errors** - Error patterns with solutions and occurrence tracking
- **swift_patterns** - Swift/iOS patterns with version constraints
- **sessions** - Development session context
- **tags** / **lesson_tags** - Flexible tagging system

Each main table has a corresponding FTS5 virtual table (`lessons_fts`, `errors_fts`, `patterns_fts`) with triggers to keep them synchronized.

### Configuration Layers
1. `config.json` - Default configuration
2. Environment variables (`HINDSIGHT_DB_PATH`, `HINDSIGHT_LOG_LEVEL`, `HINDSIGHT_LOG_FILE`) override config
3. Runtime directory: `~/.hindsight/`

### Test Structure
- `conftest.py` - Fixtures including `temp_db`, `knowledge_base_server`, `populated_db`
- `test_database.py` - Low-level database CRUD operations
- `test_tools.py` - MCP tool integration tests
- `test_fts.py` - Full-text search accuracy tests
- `test_performance.py` - Benchmarks (marked with `@pytest.mark.slow`)

## Key Patterns

### FTS5 Query Syntax Limitations
FTS5 treats `.` and `-` as operators. Queries like "URLSession.shared" or "protocol-oriented" will fail. Use space-separated terms or quote phrases.

### Database Retry Logic
Connection uses exponential backoff (0.5s, 1s, 2s) for transient failures. SQLite busy_timeout alone is insufficient.

### Adding New MCP Tools
1. Add method to `KnowledgeBaseServer` class
2. Add `Tool()` definition in `list_tools()`
3. Add handler case in `call_tool()`
4. Write tests in `tests/test_tools.py`

## Development Notes

- The `.claude/` directory contains session logs and lessons learned that provide architectural context
- This project welcomes AI-assisted contributions (see CONTRIBUTING.md)
- Always develop in repository, then install with `./install.sh` to `~/.hindsight/`
- Remember that hindsight is now installed via homebrew and we don't want to break it when working with this repo