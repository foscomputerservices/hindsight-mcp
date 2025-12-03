"""
Pytest configuration and fixtures for Hindsight MCP Server tests.
"""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Read schema and create tables
    schema_path = Path(__file__).parent.parent / "schema.sql"
    schema_sql = schema_path.read_text()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def db_connection(temp_db):
    """Get a connection to the temporary database."""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


@pytest.fixture
def sample_lesson():
    """Sample lesson data for testing."""
    return {
        "title": "Test Lesson",
        "content": "This is test content for the lesson.",
        "category": "practice",
        "technology": "swift",
        "tags": ["testing", "sample"]
    }


@pytest.fixture
def sample_error():
    """Sample error data for testing."""
    return {
        "technology": "swift",
        "error_pattern": "Cannot convert value of type 'String' to expected argument type 'Int'",
        "root_cause": "Type mismatch in function call",
        "solution": "Use Int(string) or pass the correct type",
        "code_example": "let value = Int(stringValue) ?? 0"
    }


@pytest.fixture
def sample_pattern():
    """Sample Swift pattern data for testing."""
    return {
        "pattern_name": "Result Type Error Handling",
        "description": "Use Result type for async error handling in Swift",
        "code_example": """
func fetchData() -> Result<Data, Error> {
    // Implementation
}
""",
        "when_to_use": "When you need explicit error handling without throwing",
        "when_not_to_use": "Simple operations where try/catch is cleaner",
        "related_apis": ["URLSession", "Combine"],
        "ios_version": "13.0",
        "swift_version": "5.0"
    }


@pytest.fixture
def populated_db(db_connection):
    """Database with sample data for testing queries."""
    cursor = db_connection.cursor()

    # Add lessons
    lessons = [
        ("SwiftUI State Management", "Use @State for local view state", "pattern", "swift"),
        ("Bitbucket Pipeline Caching", "Cache dependencies to speed up builds", "practice", "bitbucket"),
        ("Xcode Build Settings", "Understand build settings inheritance", "practice", "xcode"),
        ("Memory Leak Detection", "Use Instruments to find memory leaks", "practice", "swift"),
        ("Async/Await Migration", "How to migrate from completion handlers", "pattern", "swift"),
    ]
    for title, content, category, tech in lessons:
        cursor.execute(
            "INSERT INTO lessons (title, content, category, technology) VALUES (?, ?, ?, ?)",
            (title, content, category, tech)
        )

    # Add errors
    errors = [
        ("swift", "Type 'X' does not conform to protocol 'Y'", "Missing protocol conformance", "Add protocol conformance"),
        ("xcode", "Signing requires a development team", "No team selected", "Select a development team in Signing settings"),
        ("swift", "Cannot find 'X' in scope", "Missing import or typo", "Check imports and spelling"),
    ]
    for tech, pattern, cause, solution in errors:
        cursor.execute(
            "INSERT INTO common_errors (technology, error_pattern, root_cause, solution) VALUES (?, ?, ?, ?)",
            (tech, pattern, cause, solution)
        )

    # Add patterns
    patterns = [
        ("Observable Object", "Use ObservableObject for SwiftUI data", "class MyModel: ObservableObject { @Published var data: [Item] = [] }", "15.0", "5.5"),
        ("Actor Isolation", "Use actors for thread-safe data", "actor DataManager { var items: [Item] = [] }", "15.0", "5.5"),
    ]
    for name, desc, code, ios, swift in patterns:
        cursor.execute(
            "INSERT INTO swift_patterns (pattern_name, description, code_example, ios_version, swift_version) VALUES (?, ?, ?, ?, ?)",
            (name, desc, code, ios, swift)
        )

    db_connection.commit()
    return db_connection


@pytest.fixture
def knowledge_base_server(temp_db, monkeypatch):
    """Create a KnowledgeBaseServer instance with temp database."""
    from server import KnowledgeBaseServer, CONFIG

    # Patch the database path
    monkeypatch.setattr("server.DB_PATH", Path(temp_db))

    # Create server instance (this will use the temp db)
    server = KnowledgeBaseServer()
    server.db_path = Path(temp_db)

    return server
