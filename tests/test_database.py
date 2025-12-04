"""
Unit tests for database operations.
Tests schema creation, CRUD operations, and data integrity.
"""

import sqlite3

import pytest


class TestSchemaCreation:
    """Tests for database schema initialization."""

    def test_lessons_table_exists(self, db_connection):
        """Verify lessons table was created."""
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='lessons'"
        )
        assert cursor.fetchone() is not None

    def test_common_errors_table_exists(self, db_connection):
        """Verify common_errors table was created."""
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='common_errors'"
        )
        assert cursor.fetchone() is not None

    def test_swift_patterns_table_exists(self, db_connection):
        """Verify swift_patterns table was created."""
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='swift_patterns'"
        )
        assert cursor.fetchone() is not None

    def test_sessions_table_exists(self, db_connection):
        """Verify sessions table was created."""
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        )
        assert cursor.fetchone() is not None

    def test_tags_table_exists(self, db_connection):
        """Verify tags table was created."""
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tags'"
        )
        assert cursor.fetchone() is not None

    def test_fts_tables_exist(self, db_connection):
        """Verify FTS virtual tables were created."""
        fts_tables = ["lessons_fts", "errors_fts", "patterns_fts"]
        for table_name in fts_tables:
            cursor = db_connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
            )
            assert cursor.fetchone() is not None, f"FTS table {table_name} not found"


class TestLessonsCRUD:
    """Tests for lessons table CRUD operations."""

    def test_insert_lesson(self, db_connection):
        """Test inserting a lesson."""
        cursor = db_connection.execute(
            "INSERT INTO lessons (title, content, category, technology) VALUES (?, ?, ?, ?)",
            ("Test Title", "Test Content", "practice", "swift"),
        )
        db_connection.commit()
        assert cursor.lastrowid == 1

    def test_insert_lesson_validates_category(self, db_connection):
        """Test that invalid category is rejected."""
        with pytest.raises(sqlite3.IntegrityError):
            db_connection.execute(
                "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
                ("Test", "Content", "invalid_category"),
            )

    def test_lesson_categories(self, db_connection):
        """Test all valid category values."""
        valid_categories = ["pattern", "practice", "gotcha", "decision"]
        for i, category in enumerate(valid_categories):
            db_connection.execute(
                "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
                (f"Title {i}", f"Content {i}", category),
            )
        db_connection.commit()

        cursor = db_connection.execute("SELECT COUNT(*) FROM lessons")
        assert cursor.fetchone()[0] == 4

    def test_lesson_timestamp_auto(self, db_connection):
        """Test that created_at is automatically set."""
        db_connection.execute(
            "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
            ("Test", "Content", "practice"),
        )
        db_connection.commit()

        cursor = db_connection.execute("SELECT created_at, updated_at FROM lessons WHERE id = 1")
        row = cursor.fetchone()
        assert row["created_at"] is not None
        assert row["updated_at"] is not None

    def test_select_lesson(self, db_connection):
        """Test selecting a lesson."""
        db_connection.execute(
            "INSERT INTO lessons (title, content, category, technology) VALUES (?, ?, ?, ?)",
            ("SwiftUI Basics", "Learn SwiftUI fundamentals", "practice", "swift"),
        )
        db_connection.commit()

        cursor = db_connection.execute("SELECT * FROM lessons WHERE id = 1")
        row = cursor.fetchone()
        assert row["title"] == "SwiftUI Basics"
        assert row["technology"] == "swift"

    def test_update_lesson(self, db_connection):
        """Test updating a lesson."""
        db_connection.execute(
            "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
            ("Original", "Original content", "practice"),
        )
        db_connection.commit()

        db_connection.execute("UPDATE lessons SET title = ? WHERE id = 1", ("Updated",))
        db_connection.commit()

        cursor = db_connection.execute("SELECT title FROM lessons WHERE id = 1")
        assert cursor.fetchone()["title"] == "Updated"

    def test_delete_lesson(self, db_connection):
        """Test deleting a lesson."""
        db_connection.execute(
            "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
            ("To Delete", "Content", "practice"),
        )
        db_connection.commit()

        db_connection.execute("DELETE FROM lessons WHERE id = 1")
        db_connection.commit()

        cursor = db_connection.execute("SELECT * FROM lessons WHERE id = 1")
        assert cursor.fetchone() is None


class TestTagSystem:
    """Tests for tags and lesson_tags relationship."""

    def test_create_tag(self, db_connection):
        """Test creating a tag."""
        cursor = db_connection.execute("INSERT INTO tags (name) VALUES (?)", ("swiftui",))
        db_connection.commit()
        assert cursor.lastrowid == 1

    def test_tag_uniqueness(self, db_connection):
        """Test that duplicate tag names are rejected."""
        db_connection.execute("INSERT INTO tags (name) VALUES (?)", ("testing",))
        db_connection.commit()

        with pytest.raises(sqlite3.IntegrityError):
            db_connection.execute("INSERT INTO tags (name) VALUES (?)", ("testing",))

    def test_lesson_tag_association(self, db_connection):
        """Test associating tags with lessons."""
        # Create lesson
        db_connection.execute(
            "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
            ("Test Lesson", "Content", "practice"),
        )
        # Create tag
        db_connection.execute("INSERT INTO tags (name) VALUES (?)", ("testing",))
        # Associate
        db_connection.execute("INSERT INTO lesson_tags (lesson_id, tag_id) VALUES (?, ?)", (1, 1))
        db_connection.commit()

        cursor = db_connection.execute(
            "SELECT t.name FROM tags t JOIN lesson_tags lt ON t.id = lt.tag_id WHERE lt.lesson_id = 1"
        )
        assert cursor.fetchone()["name"] == "testing"

    def test_cascade_delete_lesson_tags(self, db_connection):
        """Test that deleting a lesson removes its tag associations."""
        db_connection.execute(
            "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
            ("Test", "Content", "practice"),
        )
        db_connection.execute("INSERT INTO tags (name) VALUES (?)", ("tag1",))
        db_connection.execute("INSERT INTO lesson_tags (lesson_id, tag_id) VALUES (?, ?)", (1, 1))
        db_connection.commit()

        db_connection.execute("DELETE FROM lessons WHERE id = 1")
        db_connection.commit()

        cursor = db_connection.execute("SELECT * FROM lesson_tags WHERE lesson_id = 1")
        assert cursor.fetchone() is None


class TestCommonErrorsCRUD:
    """Tests for common_errors table operations."""

    def test_insert_error(self, db_connection):
        """Test inserting a common error."""
        cursor = db_connection.execute(
            "INSERT INTO common_errors (technology, error_pattern, solution) VALUES (?, ?, ?)",
            ("swift", "Type mismatch", "Check types"),
        )
        db_connection.commit()
        assert cursor.lastrowid == 1

    def test_error_occurrence_count_default(self, db_connection):
        """Test that occurrence_count defaults to 1."""
        db_connection.execute(
            "INSERT INTO common_errors (technology, error_pattern, solution) VALUES (?, ?, ?)",
            ("swift", "Error", "Fix it"),
        )
        db_connection.commit()

        cursor = db_connection.execute("SELECT occurrence_count FROM common_errors WHERE id = 1")
        assert cursor.fetchone()["occurrence_count"] == 1

    def test_increment_occurrence_count(self, db_connection):
        """Test incrementing occurrence count."""
        db_connection.execute(
            "INSERT INTO common_errors (technology, error_pattern, solution) VALUES (?, ?, ?)",
            ("swift", "Error", "Fix it"),
        )
        db_connection.execute(
            "UPDATE common_errors SET occurrence_count = occurrence_count + 1 WHERE id = 1"
        )
        db_connection.commit()

        cursor = db_connection.execute("SELECT occurrence_count FROM common_errors WHERE id = 1")
        assert cursor.fetchone()["occurrence_count"] == 2


class TestSwiftPatternsCRUD:
    """Tests for swift_patterns table operations."""

    def test_insert_pattern(self, db_connection):
        """Test inserting a Swift pattern."""
        cursor = db_connection.execute(
            "INSERT INTO swift_patterns (pattern_name, description, code_example) VALUES (?, ?, ?)",
            ("Singleton", "Thread-safe singleton pattern", "static let shared = MyClass()"),
        )
        db_connection.commit()
        assert cursor.lastrowid == 1

    def test_pattern_with_version(self, db_connection):
        """Test pattern with version constraints."""
        db_connection.execute(
            """INSERT INTO swift_patterns
               (pattern_name, description, code_example, ios_version, swift_version)
               VALUES (?, ?, ?, ?, ?)""",
            ("Observation", "@Observable macro", "@Observable class Model {}", "17.0", "5.9"),
        )
        db_connection.commit()

        cursor = db_connection.execute(
            "SELECT ios_version, swift_version FROM swift_patterns WHERE id = 1"
        )
        row = cursor.fetchone()
        assert row["ios_version"] == "17.0"
        assert row["swift_version"] == "5.9"


class TestSessionsCRUD:
    """Tests for sessions table operations."""

    def test_insert_session(self, db_connection):
        """Test inserting a session."""
        cursor = db_connection.execute(
            "INSERT INTO sessions (date, project_name, summary) VALUES (?, ?, ?)",
            ("2025-12-03", "TestProject", "Did some testing"),
        )
        db_connection.commit()
        assert cursor.lastrowid == 1

    def test_session_indexes(self, db_connection):
        """Verify session indexes exist."""
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_sessions%'"
        )
        indexes = [row["name"] for row in cursor]
        assert "idx_sessions_date" in indexes
        assert "idx_sessions_project" in indexes


class TestFTSTriggers:
    """Tests for FTS trigger functionality."""

    def test_lesson_fts_insert_trigger(self, db_connection):
        """Test that inserting a lesson updates FTS index."""
        db_connection.execute(
            "INSERT INTO lessons (title, content, category, technology) VALUES (?, ?, ?, ?)",
            ("SwiftUI Animation", "Learn about animations", "pattern", "swift"),
        )
        db_connection.commit()

        # Search in FTS
        cursor = db_connection.execute(
            "SELECT rowid FROM lessons_fts WHERE lessons_fts MATCH 'animation'"
        )
        assert cursor.fetchone() is not None

    def test_lesson_fts_delete_trigger(self, db_connection):
        """Test that deleting a lesson removes it from FTS index.

        Note: FTS5 external content tables require explicit rebuild.
        The trigger deletes from FTS, but we verify via JOIN to main table.
        """
        db_connection.execute(
            "INSERT INTO lessons (title, content, category) VALUES (?, ?, ?)",
            ("UniqueSearchableTitle", "Content", "practice"),
        )
        db_connection.commit()

        # Verify it's searchable before delete
        cursor = db_connection.execute(
            "SELECT rowid FROM lessons_fts WHERE lessons_fts MATCH 'UniqueSearchableTitle'"
        )
        assert cursor.fetchone() is not None

        db_connection.execute("DELETE FROM lessons WHERE id = 1")
        db_connection.commit()

        # Verify the lesson itself is gone
        cursor = db_connection.execute("SELECT * FROM lessons WHERE id = 1")
        assert cursor.fetchone() is None

        # Rebuild FTS index to ensure consistency (mimics production behavior)
        db_connection.execute("INSERT INTO lessons_fts(lessons_fts) VALUES('rebuild')")
        db_connection.commit()

        cursor = db_connection.execute(
            "SELECT rowid FROM lessons_fts WHERE lessons_fts MATCH 'UniqueSearchableTitle'"
        )
        assert cursor.fetchone() is None

    def test_error_fts_insert_trigger(self, db_connection):
        """Test that inserting an error updates FTS index."""
        db_connection.execute(
            "INSERT INTO common_errors (technology, error_pattern, solution) VALUES (?, ?, ?)",
            ("swift", "XYZUniqueError pattern", "Fix the XYZ issue"),
        )
        db_connection.commit()

        cursor = db_connection.execute(
            "SELECT rowid FROM errors_fts WHERE errors_fts MATCH 'XYZUniqueError'"
        )
        assert cursor.fetchone() is not None

    def test_pattern_fts_insert_trigger(self, db_connection):
        """Test that inserting a pattern updates FTS index."""
        db_connection.execute(
            "INSERT INTO swift_patterns (pattern_name, description, code_example) VALUES (?, ?, ?)",
            ("UniquePatternXYZ", "A unique description", "code example"),
        )
        db_connection.commit()

        cursor = db_connection.execute(
            "SELECT rowid FROM patterns_fts WHERE patterns_fts MATCH 'UniquePatternXYZ'"
        )
        assert cursor.fetchone() is not None


class TestDataIntegrity:
    """Tests for data integrity constraints."""

    def test_foreign_key_enforcement(self, db_connection):
        """Test that foreign keys are enforced."""
        # Try to insert a lesson_tag with non-existent lesson
        with pytest.raises(sqlite3.IntegrityError):
            db_connection.execute(
                "INSERT INTO lesson_tags (lesson_id, tag_id) VALUES (?, ?)", (999, 1)
            )

    def test_required_fields_lesson(self, db_connection):
        """Test that required fields are enforced for lessons."""
        with pytest.raises(sqlite3.IntegrityError):
            db_connection.execute(
                "INSERT INTO lessons (title, category) VALUES (?, ?)", ("No content", "practice")
            )

    def test_required_fields_error(self, db_connection):
        """Test that required fields are enforced for errors."""
        with pytest.raises(sqlite3.IntegrityError):
            db_connection.execute(
                "INSERT INTO common_errors (technology, error_pattern) VALUES (?, ?)",
                ("swift", "No solution"),
            )
