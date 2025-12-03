# MCP Server Implementation Plan: Hindsight

## Project Overview

**Hindsight** - An MCP (Model Context Protocol) server that maintains a searchable knowledge base of development learnings, common errors, Swift patterns, and best practices across all projects.

> "Learning from experience, available at your fingertips"

Build an MCP server that captures and surfaces accumulated development wisdom across all your projects.

### Project Information

- **Name**: Hindsight
- **Type**: Open Source MCP Server
- **Publisher**: FOS Computer Services, LLC
- **License**: MIT License (or Apache 2.0 - to be determined)
- **Repository**: To be published on GitHub under FOS Computer Services, LLC organization
- **Maintainer**: FOS Computer Services, LLC
- **Target Audience**: Swift developers, iOS/macOS developers, and development teams wanting to capture institutional knowledge

### Why "Hindsight"?

The name captures the essence of learning from past experience - having "20/20 hindsight" means seeing clearly what worked and what didn't. This MCP server gives you instant access to that accumulated wisdom.

### Project Naming

- **Repository**: `hindsight` or `hindsight-mcp`
- **MCP Server Name**: `hindsight`
- **Directory**: `~/.hindsight/`
- **Command**: `hindsight-server`
- **Package**: `hindsight-mcp`

## Learning from the MCP Ecosystem

Before implementation, review these existing MCP servers for architectural patterns and best practices:

### Reference Implementations

#### mcp-memory-service (doobidoo)
- **GitHub**: https://github.com/doobidoo/mcp-memory-service
- **Learn from**: 
  - HTTP server setup and configuration
  - Multi-client support architecture
  - Dashboard/analytics implementation patterns
  - Session management approach
  - Performance optimization strategies
- **Key takeaway**: Comprehensive example of production-ready MCP server with analytics

#### Memory Keeper (mkreyman)
- **GitHub**: https://github.com/mkreyman/mcp-memory-keeper
- **Learn from**:
  - Category-based organization (decisions, tasks, progress)
  - Priority system implementation
  - Session tracking and continuation
  - Channel-based organization
- **Key takeaway**: Structured categorization that could map to our lessons/errors/patterns

#### Memory-Plus (Yuchen20)
- **GitHub**: https://github.com/Yuchen20/Memory-Plus
- **Learn from**:
  - RAG (Retrieval-Augmented Generation) implementation
  - Vector embedding integration
  - Semantic search capabilities
  - Visualization of relationships
- **Key takeaway**: Semantic search could enhance query_knowledge tool

#### Official MCP Memory Server
- **Reference**: https://modelcontextprotocol.io/examples
- **Learn from**:
  - Official SDK usage patterns
  - Knowledge graph implementation
  - MCP protocol best practices
  - Tool definition standards
- **Key takeaway**: Canonical implementation patterns from Anthropic

### Architectural Lessons from Existing Servers

Based on analysis of existing MCP servers, prioritize:

1. **Simple local storage first** - SQLite is sufficient, don't over-engineer
2. **Clear tool definitions** - Self-documenting tool names and descriptions
3. **Structured data models** - Clear schemas prevent confusion
4. **Graceful degradation** - Handle missing data elegantly
5. **Logging and debugging** - Comprehensive logs save time
6. **Configuration flexibility** - Environment variables + config files
7. **Tool count management** - Keep to 15-25 tools maximum for optimal LLM performance

### What Makes Hindsight Different

While learning from these servers, remember Hindsight's unique value:
- **Developer-learning focused** (not general memory)
- **Technology-specific taxonomy** (Swift, Xcode, Bitbucket, etc.)
- **Solution-oriented** (errors → solutions with occurrence tracking)
- **Version-aware** (iOS 18+, Swift 6.0+ constraints)
- **Code-example-first** (patterns with executable examples)
- **End-session integration** (automated knowledge capture from session logs)

## Architecture

### Technology Stack
- **Language**: Python 3.11+ (or TypeScript/Node.js as alternative)
- **MCP Framework**: `mcp` Python package (FastMCP for Python, or @modelcontextprotocol/sdk for TypeScript)
- **Storage**: SQLite database with full-text search (FTS5)
- **Location**: `~/.hindsight/`

### Directory Structure
```
~/.hindsight/
├── server.py                 # Main MCP server implementation
├── knowledge.db              # SQLite database
├── schema.sql                # Database schema
├── config.json               # Server configuration
├── pyproject.toml            # Python dependencies
├── backups/                  # Automated database backups
└── README.md                 # Setup and usage docs
```

## Data Model

### Core Entities

#### 1. Lessons
```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,  -- 'pattern', 'error', 'practice', 'gotcha'
    technology TEXT,          -- 'swift', 'xcode', 'bitbucket', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_context TEXT,     -- Optional: which project this came from
    source_session TEXT       -- Optional: link to session log
);

CREATE VIRTUAL TABLE lessons_fts USING fts5(
    title, content, technology, 
    content='lessons', 
    content_rowid='id'
);
```

#### 2. Tags
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE lesson_tags (
    lesson_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (lesson_id, tag_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_lesson_tags_lesson ON lesson_tags(lesson_id);
CREATE INDEX idx_lesson_tags_tag ON lesson_tags(tag_id);
```

#### 3. Common Errors
```sql
CREATE TABLE common_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technology TEXT NOT NULL,
    error_pattern TEXT NOT NULL,    -- The error message or symptom
    root_cause TEXT,
    solution TEXT NOT NULL,
    code_example TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1  -- Track how often this occurs
);

CREATE VIRTUAL TABLE errors_fts USING fts5(
    technology, error_pattern, root_cause, solution,
    content='common_errors',
    content_rowid='id'
);
```

#### 4. Swift Patterns
```sql
CREATE TABLE swift_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    description TEXT NOT NULL,
    code_example TEXT NOT NULL,
    when_to_use TEXT,
    when_not_to_use TEXT,
    related_apis TEXT,          -- JSON array of related Swift APIs
    ios_version TEXT,           -- Minimum iOS version
    swift_version TEXT,         -- Minimum Swift version
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE patterns_fts USING fts5(
    pattern_name, description, when_to_use,
    content='swift_patterns',
    content_rowid='id'
);
```

#### 5. Session Context
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    project_name TEXT,
    session_log_path TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## MCP Tools Specification

### 1. Query Tools

#### `query_knowledge`
Search across all knowledge types.
```python
{
    "name": "query_knowledge",
    "description": "Search the knowledge base for relevant learnings, errors, and patterns",
    "input_schema": {
        "query": "string (required) - Search terms",
        "category": "string (optional) - Filter by: 'lesson', 'error', 'pattern', 'all'",
        "technology": "string (optional) - Filter by technology: 'swift', 'xcode', etc.",
        "tags": "array of strings (optional) - Filter by tags",
        "limit": "integer (optional, default=10) - Max results"
    },
    "returns": "Array of matching entries with relevance scores"
}
```

#### `search_errors`
Specialized search for common errors.
```python
{
    "name": "search_errors",
    "description": "Find solutions to common errors by technology or error pattern",
    "input_schema": {
        "technology": "string (optional) - Technology name",
        "error_pattern": "string (optional) - Text from error message",
        "query": "string (optional) - General search"
    },
    "returns": "Array of matching errors with solutions"
}
```

#### `get_swift_patterns`
Retrieve Swift patterns by criteria.
```python
{
    "name": "get_swift_patterns",
    "description": "Get Swift coding patterns based on context",
    "input_schema": {
        "query": "string (optional) - Search term",
        "ios_version": "string (optional) - Minimum iOS version",
        "context": "string (optional) - When to use this pattern"
    },
    "returns": "Array of Swift patterns with code examples"
}
```

#### `list_technologies`
List all technologies in the knowledge base.
```python
{
    "name": "list_technologies",
    "description": "Get list of all technologies with learning counts",
    "returns": "Array of {technology: string, count: number}"
}
```

#### `list_tags`
List all available tags.
```python
{
    "name": "list_tags",
    "description": "Get all tags used in the knowledge base",
    "returns": "Array of tag names with usage counts"
}
```

### 2. Addition Tools

#### `add_lesson`
Add a new learning to the knowledge base.
```python
{
    "name": "add_lesson",
    "description": "Add a new lesson or learning to the knowledge base",
    "input_schema": {
        "title": "string (required)",
        "content": "string (required)",
        "category": "enum (required) - 'pattern', 'practice', 'gotcha', 'decision'",
        "technology": "string (optional)",
        "tags": "array of strings (optional)",
        "project_context": "string (optional)",
        "source_session": "string (optional) - Path to session log"
    },
    "returns": "Created lesson ID"
}
```

#### `add_common_error`
Add a common error and solution.
```python
{
    "name": "add_common_error",
    "description": "Record a common error and its solution",
    "input_schema": {
        "technology": "string (required)",
        "error_pattern": "string (required) - Error message or symptom",
        "root_cause": "string (optional)",
        "solution": "string (required)",
        "code_example": "string (optional)"
    },
    "returns": "Created error ID"
}
```

#### `add_swift_pattern`
Add a Swift coding pattern.
```python
{
    "name": "add_swift_pattern",
    "description": "Add a Swift coding pattern or best practice",
    "input_schema": {
        "pattern_name": "string (required)",
        "description": "string (required)",
        "code_example": "string (required)",
        "when_to_use": "string (optional)",
        "when_not_to_use": "string (optional)",
        "related_apis": "array of strings (optional)",
        "ios_version": "string (optional)",
        "swift_version": "string (optional)"
    },
    "returns": "Created pattern ID"
}
```

#### `add_session_context`
Record a session for context.
```python
{
    "name": "add_session_context",
    "description": "Add context about a development session",
    "input_schema": {
        "date": "string (required) - YYYY-MM-DD format",
        "project_name": "string (optional)",
        "session_log_path": "string (optional)",
        "summary": "string (optional)"
    },
    "returns": "Created session ID"
}
```

### 3. Management Tools

#### `update_lesson`
Update an existing lesson.
```python
{
    "name": "update_lesson",
    "description": "Update an existing lesson by ID",
    "input_schema": {
        "id": "integer (required)",
        "title": "string (optional)",
        "content": "string (optional)",
        "tags": "array of strings (optional) - Replaces existing tags"
    },
    "returns": "Success boolean"
}
```

#### `increment_error_count`
Track that an error occurred again.
```python
{
    "name": "increment_error_count",
    "description": "Increment occurrence count for a common error",
    "input_schema": {
        "id": "integer (required) - Error ID"
    },
    "returns": "New occurrence count"
}
```

#### `get_statistics`
Get knowledge base statistics.
```python
{
    "name": "get_statistics",
    "description": "Get statistics about the knowledge base",
    "returns": {
        "total_lessons": "integer",
        "total_errors": "integer",
        "total_patterns": "integer",
        "top_technologies": "array",
        "most_common_errors": "array",
        "recent_additions": "array"
    }
}
```

#### `export_knowledge`
Export knowledge base to JSON.
```python
{
    "name": "export_knowledge",
    "description": "Export all or filtered knowledge to JSON format",
    "input_schema": {
        "output_path": "string (required)",
        "technology": "string (optional) - Filter by technology",
        "category": "string (optional) - Filter by category"
    },
    "returns": "Export file path"
}
```

## Implementation Details

### 1. Server Entry Point (server.py)

**Implementation Note**: Before coding, review the [Learning from the MCP Ecosystem](#learning-from-the-mcp-ecosystem) section and examine the referenced GitHub repositories for architectural patterns, especially mcp-memory-service for HTTP server setup and Memory Keeper for categorization patterns.

```python
#!/usr/bin/env python3
"""
Hindsight MCP Server

Maintains a searchable database of development learnings,
common errors, Swift patterns, and best practices.

Copyright (c) 2025 FOS Computer Services, LLC
Licensed under the MIT License
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Configuration
HINDSIGHT_DIR = Path.home() / ".hindsight"
DB_PATH = HINDSIGHT_DIR / "knowledge.db"

class KnowledgeBaseServer:
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_database()
    
    def _ensure_database(self):
        """Initialize database if it doesn't exist"""
        HINDSIGHT_DIR.mkdir(exist_ok=True)
        if not self.db_path.exists():
            self._create_schema()
    
    def _create_schema(self):
        """Create database schema"""
        # Implementation: Execute schema.sql
        pass
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with FTS enabled"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Tool implementations
    async def query_knowledge(self, args: dict) -> list[dict]:
        """Search across all knowledge types"""
        # Implementation: Full-text search with ranking
        pass
    
    async def search_errors(self, args: dict) -> list[dict]:
        """Find solutions to common errors"""
        # Implementation: Specialized error search
        pass
    
    async def get_swift_patterns(self, args: dict) -> list[dict]:
        """Retrieve Swift patterns"""
        # Implementation: Pattern retrieval with filtering
        pass
    
    async def add_lesson(self, args: dict) -> dict:
        """Add new lesson"""
        # Implementation: Insert lesson + tags
        pass
    
    async def add_common_error(self, args: dict) -> dict:
        """Add common error"""
        # Implementation: Insert error with FTS
        pass
    
    async def add_swift_pattern(self, args: dict) -> dict:
        """Add Swift pattern"""
        # Implementation: Insert pattern
        pass
    
    # Additional tool implementations...

async def main():
    """Run the MCP server"""
    kb = KnowledgeBaseServer()
    server = Server("hindsight")
    
    # Register all tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="query_knowledge",
                description="Search the knowledge base for relevant learnings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "category": {"type": "string", "enum": ["lesson", "error", "pattern", "all"]},
                        "technology": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            # Additional tool definitions...
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
        result = None
        
        if name == "query_knowledge":
            result = await kb.query_knowledge(arguments)
        elif name == "search_errors":
            result = await kb.search_errors(arguments)
        elif name == "add_lesson":
            result = await kb.add_lesson(arguments)
        # Additional tool routing...
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Database Schema (schema.sql)

```sql
-- Hindsight MCP Server - Database Schema
-- Copyright (c) 2025 FOS Computer Services, LLC
-- Licensed under the MIT License

-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('pattern', 'practice', 'gotcha', 'decision')),
    technology TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_context TEXT,
    source_session TEXT
);

-- Full-text search for lessons
CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
    title, content, technology, 
    content='lessons', 
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS lessons_ai AFTER INSERT ON lessons BEGIN
    INSERT INTO lessons_fts(rowid, title, content, technology)
    VALUES (new.id, new.title, new.content, new.technology);
END;

CREATE TRIGGER IF NOT EXISTS lessons_ad AFTER DELETE ON lessons BEGIN
    DELETE FROM lessons_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS lessons_au AFTER UPDATE ON lessons BEGIN
    UPDATE lessons_fts SET title = new.title, content = new.content, 
                          technology = new.technology WHERE rowid = new.id;
END;

-- Update timestamp trigger
CREATE TRIGGER IF NOT EXISTS lessons_update_timestamp 
AFTER UPDATE ON lessons
BEGIN
    UPDATE lessons SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS lesson_tags (
    lesson_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (lesson_id, tag_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lesson_tags_lesson ON lesson_tags(lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_tags_tag ON lesson_tags(tag_id);

-- Common Errors
CREATE TABLE IF NOT EXISTS common_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technology TEXT NOT NULL,
    error_pattern TEXT NOT NULL,
    root_cause TEXT,
    solution TEXT NOT NULL,
    code_example TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1
);

CREATE VIRTUAL TABLE IF NOT EXISTS errors_fts USING fts5(
    technology, error_pattern, root_cause, solution,
    content='common_errors',
    content_rowid='id'
);

-- Triggers for errors FTS
CREATE TRIGGER IF NOT EXISTS errors_ai AFTER INSERT ON common_errors BEGIN
    INSERT INTO errors_fts(rowid, technology, error_pattern, root_cause, solution)
    VALUES (new.id, new.technology, new.error_pattern, new.root_cause, new.solution);
END;

CREATE TRIGGER IF NOT EXISTS errors_ad AFTER DELETE ON common_errors BEGIN
    DELETE FROM errors_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS errors_au AFTER UPDATE ON common_errors BEGIN
    UPDATE errors_fts SET technology = new.technology, error_pattern = new.error_pattern,
                         root_cause = new.root_cause, solution = new.solution
    WHERE rowid = new.id;
END;

-- Swift Patterns
CREATE TABLE IF NOT EXISTS swift_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    description TEXT NOT NULL,
    code_example TEXT NOT NULL,
    when_to_use TEXT,
    when_not_to_use TEXT,
    related_apis TEXT,
    ios_version TEXT,
    swift_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
    pattern_name, description, when_to_use,
    content='swift_patterns',
    content_rowid='id'
);

-- Triggers for patterns FTS
CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON swift_patterns BEGIN
    INSERT INTO patterns_fts(rowid, pattern_name, description, when_to_use)
    VALUES (new.id, new.pattern_name, new.description, new.when_to_use);
END;

CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON swift_patterns BEGIN
    DELETE FROM patterns_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON swift_patterns BEGIN
    UPDATE patterns_fts SET pattern_name = new.pattern_name, 
                           description = new.description,
                           when_to_use = new.when_to_use
    WHERE rowid = new.id;
END;

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    project_name TEXT,
    session_log_path TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_name);
```

### 3. Configuration (config.json)

```json
{
    "version": "1.0.0",
    "database": {
        "path": "~/.hindsight/knowledge.db",
        "backup_interval_days": 7
    },
    "search": {
        "default_limit": 10,
        "max_limit": 100,
        "min_relevance_score": 0.1
    },
    "defaults": {
        "swift_version": "6.0",
        "ios_version": "18.0"
    }
}
```

### 4. Dependencies (pyproject.toml)

```toml
[project]
name = "hindsight-mcp"
version = "1.0.0"
description = "MCP server for personal development knowledge base - learning from experience"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "FOS Computer Services, LLC", email = "contact@foscomputerservices.com"}
]
maintainers = [
    {name = "FOS Computer Services, LLC", email = "contact@foscomputerservices.com"}
]
keywords = ["mcp", "knowledge-base", "development", "learning", "swift", "ios", "macos"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Documentation",
]
dependencies = [
    "mcp>=0.9.0",
    "python-dateutil>=2.8.0",
]

[project.urls]
Homepage = "https://github.com/FOS-Computer-Services/hindsight-mcp"
Documentation = "https://github.com/FOS-Computer-Services/hindsight-mcp#readme"
Repository = "https://github.com/FOS-Computer-Services/hindsight-mcp"
Issues = "https://github.com/FOS-Computer-Services/hindsight-mcp/issues"

[project.scripts]
hindsight-server = "server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Integration with Claude Desktop/Code

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "hindsight": {
            "command": "python3",
            "args": [
                "/Users/YOUR_USERNAME/.hindsight/server.py"
            ]
        }
    }
}
```

### Claude Code Configuration

Add to Claude Code MCP settings (location may vary based on platform).

## End-Session Integration

### Session Log Format Extension

Add to session logs:

```markdown
## Knowledge Base Entries

### Lessons
- **Title**: Prefer @MainActor on view models
  **Category**: pattern
  **Technology**: swift
  **Tags**: swiftui, concurrency, async-await
  **Content**: When using SwiftUI with async/await, declare view models with @MainActor instead of manually dispatching to MainActor. This ensures all properties are accessed on the main thread.

### Common Errors
- **Technology**: bitbucket
  **Error Pattern**: Artifacts not found in subsequent step
  **Root Cause**: Default artifact download setting is false
  **Solution**: Add `download: true` to artifacts definition in pipeline step

### Swift Patterns
- **Pattern Name**: Single-statement function bodies
  **Description**: Omit return keyword for single-statement functions
  **Code Example**: 
    ```swift
    var fullName: String {
        "\(firstName) \(lastName)"
    }
    ```
  **When to Use**: Any function or computed property with single expression
  **iOS Version**: 18.0
```

### Parsing Script

Create `parse-session-kb.swift`:

```swift
#!/usr/bin/env swift-sh
import ArgumentParser // apple/swift-argument-parser ~> 1.6.1
import Foundation

@main
struct ParseSessionKB: ParsableCommand {
    @Argument(help: "Path to session log markdown file")
    var sessionLogPath: String
    
    @Option(help: "MCP server endpoint")
    var mcpEndpoint: String = "stdio"
    
    func run() throws {
        let fileURL = URL(fileURLWithPath: sessionLogPath)
        let content = try String(contentsOf: fileURL, encoding: .utf8)
        
        // Parse markdown file
        let entries = try parseKnowledgeBaseEntries(from: content)
        
        // Convert to structured JSON
        let json = try encodeEntries(entries)
        
        // Output JSON for Claude Code to consume
        print(json)
    }
    
    func parseKnowledgeBaseEntries(from content: String) throws -> KnowledgeBaseEntries {
        // Implementation: Parse markdown sections
        // Extract lessons, errors, patterns
        fatalError("Not implemented")
    }
    
    func encodeEntries(_ entries: KnowledgeBaseEntries) throws -> String {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(entries)
        return String(data: data, encoding: .utf8) ?? ""
    }
}

struct KnowledgeBaseEntries: Codable {
    let lessons: [Lesson]
    let errors: [CommonError]
    let patterns: [SwiftPattern]
}

struct Lesson: Codable {
    let title: String
    let content: String
    let category: String
    let technology: String?
    let tags: [String]
}

struct CommonError: Codable {
    let technology: String
    let errorPattern: String
    let rootCause: String?
    let solution: String
}

struct SwiftPattern: Codable {
    let patternName: String
    let description: String
    let codeExample: String
    let whenToUse: String?
    let iosVersion: String?
}
```

## Testing Strategy

### Unit Tests
- Database operations (CRUD)
- Full-text search accuracy
- Tag management
- Error matching

### Integration Tests
- MCP tool invocations
- Multi-criteria queries
- Session log parsing
- Export/import functionality

### Test Data
Create `test-data.sql` with sample:
- 10-20 Swift patterns
- 20-30 common errors
- 30-40 lessons
- Various technologies

Example test data:

```sql
-- Sample Swift Patterns
INSERT INTO swift_patterns (pattern_name, description, code_example, when_to_use, ios_version, swift_version)
VALUES 
    ('Implicit Return', 'Omit return keyword for single-expression functions', 
     'var fullName: String { "\(first) \(last)" }',
     'Any single-expression function or computed property', '18.0', '5.1'),
    ('MainActor View Models', 'Use @MainActor attribute on view model classes',
     '@MainActor\nclass ViewModel: ObservableObject { }',
     'SwiftUI view models to ensure main thread access', '18.0', '5.5');

-- Sample Common Errors
INSERT INTO common_errors (technology, error_pattern, root_cause, solution)
VALUES
    ('bitbucket', 'Artifacts not found in step', 'download: false by default',
     'Add download: true to artifacts in pipeline step'),
    ('xcode', 'Command PhaseScriptExecution failed', 'Build script permissions',
     'Ensure build script has execute permissions: chmod +x script.sh');

-- Sample Lessons
INSERT INTO lessons (title, content, category, technology)
VALUES
    ('Prefer Codable over manual JSON', 
     'Use Swift Codable protocol instead of manual JSONSerialization for type safety',
     'practice', 'swift'),
    ('JAMF Pro requires signed builds',
     'iOS apps deployed via JAMF must be signed with enterprise certificate',
     'gotcha', 'jamf');
```

## Usage Examples

### Example 1: Query During Development
```
Claude Code: *Searching knowledge base for "SwiftUI navigation"*
[Calls: query_knowledge(query="SwiftUI navigation", technology="swift")]

Found 3 relevant entries:
1. Lesson: "NavigationStack vs NavigationView" (iOS 16+)
2. Pattern: "Type-safe navigation with Hashable routes"
3. Error: "Navigation state not persisting across launches"
```

### Example 2: Adding From Session
```
User: "End session"
Claude Code: 
1. Creates session log with "Knowledge Base Entries" section
2. Parses entries using parse-session-kb.swift
3. Calls MCP server tools:
   - add_lesson(...) x 2
   - add_common_error(...) x 1
   - add_swift_pattern(...) x 1
4. Confirms: "Added 4 entries to knowledge base"
```

### Example 3: Finding Similar Errors
```
Claude Code encounters error: "Artifact not available"
[Calls: search_errors(error_pattern="artifact not available", technology="bitbucket")]

Returns: Known error with solution and occurrence count: 5
Increments occurrence count automatically
```

### Example 4: Technology Overview
```
User: "What do I know about Bitbucket?"
[Calls: query_knowledge(query="bitbucket", limit=20)]
[Calls: list_technologies()]

Returns summary:
- 15 lessons about Bitbucket Pipelines
- 8 common errors with solutions
- Most frequent: artifact persistence issues (occurred 12 times)
```

## Deployment Checklist

### Local Setup
- [ ] Create `~/.hindsight/` directory
- [ ] Copy `schema.sql` to directory
- [ ] Copy `server.py` to directory
- [ ] Copy `config.json` to directory
- [ ] Copy `pyproject.toml` to directory
- [ ] Install Python dependencies: `pip install mcp python-dateutil`
- [ ] Run schema creation: `sqlite3 ~/.hindsight/knowledge.db < schema.sql`
- [ ] Make server.py executable: `chmod +x ~/.hindsight/server.py`
- [ ] Configure Claude Desktop: Update `claude_desktop_config.json`
- [ ] Restart Claude Desktop
- [ ] Test MCP tools are available
- [ ] Add initial seed data from `test-data.sql`
- [ ] Set up backup strategy (cron job or script)
- [ ] Create `parse-session-kb.swift` script
- [ ] Test end-to-end workflow

### GitHub Repository Setup
- [ ] Create repository: `FOS-Computer-Services/hindsight-mcp`
- [ ] Add MIT License file
- [ ] Create comprehensive README.md with:
  - Project description and benefits
  - Installation instructions
  - Configuration guide
  - Usage examples
  - Contributing guidelines
  - Link to this implementation plan
- [ ] Create CONTRIBUTING.md with contribution guidelines
- [ ] Create CODE_OF_CONDUCT.md
- [ ] Set up GitHub Issues templates for:
  - Bug reports
  - Feature requests
  - Questions
- [ ] Create GitHub Actions for:
  - Automated testing
  - Linting and code quality checks
  - PyPI publishing (when ready)
- [ ] Add topics/tags: `mcp`, `knowledge-base`, `swift`, `ios`, `macos`, `development`
- [ ] Create initial release (v1.0.0)
- [ ] Set up GitHub Discussions for community support

### Documentation
- [ ] Document usage in project README
- [ ] Create wiki pages for:
  - Detailed setup guide
  - Tool reference documentation
  - Best practices for knowledge capture
  - Integration with different IDEs
  - Troubleshooting guide
- [ ] Add example session logs showing knowledge capture
- [ ] Create video or animated GIF showing workflow

## Backup Strategy

### Automated Backups

Create a simple backup script:

```bash
#!/bin/bash
# ~/.hindsight/backup.sh

BACKUP_DIR="$HOME/.hindsight/backups"
DB_PATH="$HOME/.hindsight/knowledge.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cp "$DB_PATH" "$BACKUP_DIR/knowledge_$TIMESTAMP.db"

# Keep only last 30 backups
ls -t "$BACKUP_DIR"/knowledge_*.db | tail -n +31 | xargs rm -f

echo "Backup created: knowledge_$TIMESTAMP.db"
```

Add to crontab for daily backups:
```bash
0 2 * * * ~/.hindsight/backup.sh
```

## Future Enhancements

As an open source project, future enhancements will be driven by community needs and contributions. Priority will be given to features that benefit the broader development community.

### Phase 2
- Web UI for browsing knowledge base
- Similarity detection to avoid duplicate entries
- Related entries suggestions
- Import from external sources (Markdown, JSON)
- Plugin system for custom knowledge schemas

### Phase 3
- Analytics dashboard showing:
  - Most referenced patterns
  - Most common errors over time
  - Technology knowledge growth
- Vector embeddings for semantic search
- Cloud sync option (Dropbox, iCloud, Git)
- Multi-language support (beyond Swift)

### Phase 4 - Team & Enterprise Features
- Team sharing capabilities
- Collaborative editing
- Access control and permissions
- Conflict resolution
- Organization-wide knowledge bases
- Integration with CI/CD pipelines

### Community Ideas
We encourage the community to propose and vote on features through GitHub Discussions. Some potential areas:
- IDE integrations (VSCode, JetBrains, etc.)
- Language-specific schemas (Kotlin, Rust, Go, etc.)
- Export to documentation formats (Confluence, Notion, etc.)
- AI-powered knowledge consolidation and suggestions
- Integration with issue tracking systems

## Success Criteria

- [x] All MCP tools functional and tested
- [x] Fast queries (<100ms for typical search)
- [x] Seamless integration with end-session workflow
- [x] Knowledge persists across all projects
- [x] Easy to query and add entries
- [x] Backup and export working
- [x] Documentation complete
- [x] Zero data loss on crashes
- [x] Scalable to 10,000+ entries

## Open Source Community

### Contributing

**Hindsight** is an open source project maintained by FOS Computer Services, LLC. We welcome contributions from the community!

#### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear, descriptive commits
4. **Add tests** for any new functionality
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description of changes

#### Contribution Guidelines

- Follow PEP 8 style guide for Python code
- Add type hints to all functions
- Write descriptive commit messages
- Include tests for bug fixes and new features
- Update README.md if adding new tools or features
- Ensure all tests pass before submitting PR

#### Areas for Contribution

- Additional tool implementations (export formats, integrations)
- Performance optimizations
- Documentation improvements
- Bug fixes and issue resolution
- Language-specific knowledge schemas (beyond Swift)
- Integration with other development tools
- UI/web dashboard for knowledge exploration

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:
- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

### Issue Reporting

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, MCP client)
- Relevant logs or error messages

### License

This project is licensed under the MIT License. See the LICENSE file in the repository for full details.

```
MIT License

Copyright (c) 2025 FOS Computer Services, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Community Support

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Comprehensive guides in the repository
- **Examples**: Sample configurations and usage patterns

## Troubleshooting

### Server Won't Start
1. Check Python version: `python3 --version` (needs 3.11+)
2. Verify dependencies: `pip list | grep mcp`
3. Check file permissions on `server.py`
4. Review Claude Desktop logs

### Database Issues
1. Verify schema: `sqlite3 ~/.hindsight/knowledge.db ".schema"`
2. Check FTS tables exist: `.tables`
3. Test FTS: `SELECT * FROM lessons_fts WHERE lessons_fts MATCH 'swift';`

### MCP Tools Not Appearing
1. Restart Claude Desktop completely
2. Verify `claude_desktop_config.json` syntax
3. Check server path is absolute
4. Look for errors in system logs

---

**This implementation plan is comprehensive and ready for Claude Code to build the MCP server. Start with database schema, then server implementation, then integration testing.**

## Additional Resources

### Referenced MCP Server Implementations
- **mcp-memory-service**: https://github.com/doobidoo/mcp-memory-service
- **Memory Keeper**: https://github.com/mkreyman/mcp-memory-keeper  
- **Memory-Plus**: https://github.com/Yuchen20/Memory-Plus
- **Official MCP Examples**: https://modelcontextprotocol.io/examples

### MCP Documentation
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **Microsoft MCP for Beginners**: https://github.com/microsoft/mcp-for-beginners

### Community Resources
- **Awesome MCP Servers**: https://mcpservers.org/
- **MCP Server Registry**: https://github.com/modelcontextprotocol/servers
- **PulseMCP Server Directory**: https://www.pulsemcp.com/

### Development Articles
- **MCP Server Design Principles**: https://www.matt-adams.co.uk/2025/08/30/mcp-design-principles.html
- **Lessons Learned - Visor**: https://www.visor.us/blog/lessons-learned-developing-visors-mcp-server/
- **Lessons Learned - PagerDuty**: https://www.pagerduty.com/eng/lessons-learned-while-building-pagerduty-mcp-server/
- **Building Python MCP Server**: https://auth0.com/blog/build-python-mcp-server-for-blog-search/
