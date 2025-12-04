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
import logging
import os
import sqlite3
import time
from collections.abc import Sequence
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configuration with environment variable overrides
HINDSIGHT_DIR = Path.home() / ".hindsight"
CONFIG_PATH = HINDSIGHT_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from config.json with defaults."""
    defaults = {
        "database": {
            "path": str(HINDSIGHT_DIR / "knowledge.db"),
            "connection_timeout": 30,
            "busy_timeout": 5000,
            "max_retries": 3,
            "retry_delay": 0.5,
        },
        "search": {"default_limit": 10, "max_limit": 100, "min_relevance_score": 0.1},
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": str(HINDSIGHT_DIR / "logs" / "hindsight.log"),
            "max_size_mb": 10,
            "backup_count": 5,
        },
    }

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user_config = json.load(f)
                # Deep merge user config into defaults
                for key in defaults:
                    if key in user_config and isinstance(defaults[key], dict):
                        defaults[key].update(user_config[key])
                    elif key in user_config:
                        defaults[key] = user_config[key]
        except (OSError, json.JSONDecodeError):
            pass  # Use defaults on error

    return defaults


def apply_env_overrides(config: dict) -> dict:
    """Apply environment variable overrides to config."""
    # Database path override
    if os.environ.get("HINDSIGHT_DB_PATH"):
        config["database"]["path"] = os.environ["HINDSIGHT_DB_PATH"]

    # Logging overrides
    if os.environ.get("HINDSIGHT_LOG_LEVEL"):
        config["logging"]["level"] = os.environ["HINDSIGHT_LOG_LEVEL"].upper()

    if os.environ.get("HINDSIGHT_LOG_FILE"):
        config["logging"]["file"] = os.environ["HINDSIGHT_LOG_FILE"]

    return config


def setup_logging(config: dict) -> logging.Logger:
    """Configure logging with rotating file handler."""
    log_config = config["logging"]
    log_level = getattr(logging, log_config["level"], logging.INFO)

    # Create logger
    logger = logging.getLogger("hindsight")
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (stderr for MCP compatibility)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_config["format"]))
    logger.addHandler(console_handler)

    # File handler with rotation
    log_file = Path(log_config["file"].replace("~", str(Path.home())))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config["max_size_mb"] * 1024 * 1024,
            backupCount=log_config["backup_count"],
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_config["format"]))
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        logger.warning("Could not create log file %s: %s", log_file, e)

    return logger


# Load configuration
CONFIG = apply_env_overrides(load_config())
logger = setup_logging(CONFIG)

# Resolve paths
DB_PATH = Path(CONFIG["database"]["path"].replace("~", str(Path.home())))
SCHEMA_PATH = HINDSIGHT_DIR / "schema.sql"


class KnowledgeBaseServer:
    """MCP Server for managing development knowledge base."""

    def __init__(self):
        self.db_path = DB_PATH
        self.config = CONFIG
        self.db_config = CONFIG["database"]
        self._ensure_database()

    def _ensure_database(self):
        """Initialize database if it doesn't exist."""
        HINDSIGHT_DIR.mkdir(exist_ok=True)
        if not self.db_path.exists():
            logger.info("Creating new database at %s", self.db_path)
            self._create_schema()
        else:
            logger.info("Using existing database at %s", self.db_path)

    def _create_schema(self):
        """Create database schema from schema.sql file."""
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

        schema_sql = SCHEMA_PATH.read_text()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(schema_sql)
            conn.commit()
            logger.info("Database schema created successfully")
        finally:
            conn.close()

    def _get_connection(self, retries: int = None) -> sqlite3.Connection:
        """Get database connection with retry logic and row factory enabled."""
        if retries is None:
            retries = self.db_config.get("max_retries", 3)
        retry_delay = self.db_config.get("retry_delay", 0.5)
        busy_timeout = self.db_config.get("busy_timeout", 5000)

        last_error = None
        for attempt in range(retries + 1):
            try:
                conn = sqlite3.connect(
                    self.db_path, timeout=self.db_config.get("connection_timeout", 30)
                )
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute(f"PRAGMA busy_timeout = {busy_timeout}")
                return conn
            except sqlite3.Error as e:
                last_error = e
                if attempt < retries:
                    logger.warning(
                        "Database connection attempt %d failed: %s. Retrying in %ss...",
                        attempt + 1,
                        e,
                        retry_delay,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

        logger.error("Failed to connect to database after %d attempts", retries + 1)
        raise last_error

    def _safe_execute(self, operation: str, func, *args, default=None, **kwargs):
        """Execute a database operation with error handling and graceful degradation."""
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error("Database error during %s: %s", operation, e)
            if default is not None:
                logger.info("Returning default value for %s due to error", operation)
                return default
            return {"error": f"Database error: {str(e)}"}

    async def query_knowledge(self, args: dict) -> list[dict]:
        """
        Search across all knowledge types using full-text search.

        Args:
            query: Search terms (required)
            category: Filter by 'lesson', 'error', 'pattern', or 'all'
            technology: Filter by technology name
            tags: Filter by tag names (array)
            limit: Maximum results (default 10)

        Returns:
            Array of matching entries with relevance scores
        """
        query = args.get("query", "")
        category = args.get("category", "all")
        technology = args.get("technology")
        tags = args.get("tags", [])
        limit = min(args.get("limit", 10), 100)

        results = []
        conn = self._get_connection()

        try:
            # Search lessons
            if category in ("all", "lesson"):
                lesson_results = self._search_lessons(conn, query, technology, tags, limit)
                results.extend(lesson_results)

            # Search errors
            if category in ("all", "error"):
                error_results = self._search_errors(conn, query, technology, limit)
                results.extend(error_results)

            # Search patterns
            if category in ("all", "pattern"):
                pattern_results = self._search_patterns(conn, query, limit)
                results.extend(pattern_results)

            # Sort by relevance score and limit
            results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            return results[:limit]

        finally:
            conn.close()

    def _search_lessons(
        self,
        conn: sqlite3.Connection,
        query: str,
        technology: str | None,
        tags: list[str],
        limit: int,
    ) -> list[dict]:
        """Search lessons using FTS."""
        results = []

        if query:
            # Use FTS for text search
            sql = """
                SELECT l.*, bm25(lessons_fts) as relevance
                FROM lessons l
                JOIN lessons_fts ON l.id = lessons_fts.rowid
                WHERE lessons_fts MATCH ?
            """
            params = [query]
        else:
            sql = "SELECT l.*, 1.0 as relevance FROM lessons l WHERE 1=1"
            params = []

        if technology:
            sql += " AND l.technology = ?"
            params.append(technology)

        sql += f" ORDER BY relevance LIMIT {limit}"

        cursor = conn.execute(sql, params)
        for row in cursor:
            result = dict(row)
            result["type"] = "lesson"
            # Fetch tags for this lesson
            tag_cursor = conn.execute(
                """
                SELECT t.name FROM tags t
                JOIN lesson_tags lt ON t.id = lt.tag_id
                WHERE lt.lesson_id = ?
            """,
                (result["id"],),
            )
            result["tags"] = [t["name"] for t in tag_cursor]

            # Filter by tags if specified
            if tags and not any(tag in result["tags"] for tag in tags):
                continue

            results.append(result)

        return results

    def _search_errors(
        self, conn: sqlite3.Connection, query: str, technology: str | None, limit: int
    ) -> list[dict]:
        """Search common errors using FTS."""
        results = []

        if query:
            sql = """
                SELECT e.*, bm25(errors_fts) as relevance
                FROM common_errors e
                JOIN errors_fts ON e.id = errors_fts.rowid
                WHERE errors_fts MATCH ?
            """
            params = [query]
        else:
            sql = "SELECT e.*, 1.0 as relevance FROM common_errors e WHERE 1=1"
            params = []

        if technology:
            sql += " AND e.technology = ?"
            params.append(technology)

        sql += f" ORDER BY relevance LIMIT {limit}"

        cursor = conn.execute(sql, params)
        for row in cursor:
            result = dict(row)
            result["type"] = "error"
            results.append(result)

        return results

    def _search_patterns(self, conn: sqlite3.Connection, query: str, limit: int) -> list[dict]:
        """Search Swift patterns using FTS."""
        results = []

        if query:
            sql = """
                SELECT p.*, bm25(patterns_fts) as relevance
                FROM swift_patterns p
                JOIN patterns_fts ON p.id = patterns_fts.rowid
                WHERE patterns_fts MATCH ?
                ORDER BY relevance LIMIT ?
            """
            params = [query, limit]
        else:
            sql = "SELECT p.*, 1.0 as relevance FROM swift_patterns p LIMIT ?"
            params = [limit]

        cursor = conn.execute(sql, params)
        for row in cursor:
            result = dict(row)
            result["type"] = "pattern"
            # Parse related_apis JSON if present
            if result.get("related_apis"):
                try:
                    result["related_apis"] = json.loads(result["related_apis"])
                except json.JSONDecodeError:
                    pass
            results.append(result)

        return results

    async def search_errors(self, args: dict) -> list[dict]:
        """
        Search for common errors by pattern or technology.

        Args:
            query: Search terms (optional)
            technology: Filter by technology (optional)
            limit: Maximum results (default 10)

        Returns:
            Array of matching errors with solutions
        """
        query = args.get("query", "")
        technology = args.get("technology")
        limit = min(args.get("limit", 10), 100)

        conn = self._get_connection()
        try:
            if query:
                sql = """
                    SELECT e.*, bm25(errors_fts) as relevance
                    FROM common_errors e
                    JOIN errors_fts ON e.id = errors_fts.rowid
                    WHERE errors_fts MATCH ?
                """
                params = [query]
            else:
                sql = "SELECT e.*, 1.0 as relevance FROM common_errors e WHERE 1=1"
                params = []

            if technology:
                sql += " AND e.technology = ?"
                params.append(technology)

            sql += " ORDER BY relevance, occurrence_count DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor:
                result = dict(row)
                result["type"] = "error"
                results.append(result)

            return results
        finally:
            conn.close()

    async def get_swift_patterns(self, args: dict) -> list[dict]:
        """
        Retrieve Swift patterns with optional version filtering.

        Args:
            query: Search terms (optional)
            ios_version: Filter by minimum iOS version (optional)
            swift_version: Filter by minimum Swift version (optional)
            limit: Maximum results (default 10)

        Returns:
            Array of Swift patterns with code examples
        """
        query = args.get("query", "")
        ios_version = args.get("ios_version")
        swift_version = args.get("swift_version")
        limit = min(args.get("limit", 10), 100)

        conn = self._get_connection()
        try:
            if query:
                sql = """
                    SELECT p.*, bm25(patterns_fts) as relevance
                    FROM swift_patterns p
                    JOIN patterns_fts ON p.id = patterns_fts.rowid
                    WHERE patterns_fts MATCH ?
                """
                params = [query]
            else:
                sql = "SELECT p.*, 1.0 as relevance FROM swift_patterns p WHERE 1=1"
                params = []

            # Version filtering - patterns are included if their version <= requested version
            if ios_version:
                sql += " AND (p.ios_version IS NULL OR p.ios_version <= ?)"
                params.append(ios_version)

            if swift_version:
                sql += " AND (p.swift_version IS NULL OR p.swift_version <= ?)"
                params.append(swift_version)

            sql += " ORDER BY relevance LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor:
                result = dict(row)
                result["type"] = "pattern"
                # Parse related_apis JSON if present
                if result.get("related_apis"):
                    try:
                        result["related_apis"] = json.loads(result["related_apis"])
                    except json.JSONDecodeError:
                        pass
                results.append(result)

            return results
        finally:
            conn.close()

    async def list_technologies(self, args: dict) -> list[dict]:
        """
        List all technologies with entry counts.

        Returns:
            Array of technologies with counts by category
        """
        conn = self._get_connection()
        try:
            # Get counts from lessons
            lesson_counts = {}
            cursor = conn.execute("""
                SELECT technology, COUNT(*) as count
                FROM lessons
                WHERE technology IS NOT NULL
                GROUP BY technology
            """)
            for row in cursor:
                tech = row["technology"]
                lesson_counts[tech] = row["count"]

            # Get counts from errors
            error_counts = {}
            cursor = conn.execute("""
                SELECT technology, COUNT(*) as count
                FROM common_errors
                GROUP BY technology
            """)
            for row in cursor:
                tech = row["technology"]
                error_counts[tech] = row["count"]

            # Combine results
            all_techs = set(lesson_counts.keys()) | set(error_counts.keys())
            results = []
            for tech in sorted(all_techs):
                results.append(
                    {
                        "technology": tech,
                        "lesson_count": lesson_counts.get(tech, 0),
                        "error_count": error_counts.get(tech, 0),
                        "total_count": lesson_counts.get(tech, 0) + error_counts.get(tech, 0),
                    }
                )

            return results
        finally:
            conn.close()

    async def list_tags(self, args: dict) -> list[dict]:
        """
        List all tags with usage counts.

        Returns:
            Array of tags with lesson counts
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT t.name, COUNT(lt.lesson_id) as usage_count
                FROM tags t
                LEFT JOIN lesson_tags lt ON t.id = lt.tag_id
                GROUP BY t.id, t.name
                ORDER BY usage_count DESC, t.name ASC
            """)

            results = []
            for row in cursor:
                results.append({"tag": row["name"], "usage_count": row["usage_count"]})

            return results
        finally:
            conn.close()

    async def add_lesson(self, args: dict) -> dict:
        """
        Add a new lesson to the knowledge base.

        Args:
            title: Lesson title (required)
            content: Lesson content (required)
            category: 'pattern', 'practice', 'gotcha', or 'decision' (required)
            technology: Technology name (optional)
            tags: Array of tag names (optional)
            project_context: Project context (optional)
            source_session: Path to session log (optional)

        Returns:
            Created lesson ID and success status
        """
        title = args.get("title")
        content = args.get("content")
        category = args.get("category")
        technology = args.get("technology")
        tags = args.get("tags", [])
        project_context = args.get("project_context")
        source_session = args.get("source_session")

        # Validate required fields
        if not title:
            return {"error": "title is required"}
        if not content:
            return {"error": "content is required"}
        if category not in ("pattern", "practice", "gotcha", "decision"):
            return {"error": "category must be one of: pattern, practice, gotcha, decision"}

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO lessons (title, content, category, technology, project_context, source_session)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (title, content, category, technology, project_context, source_session),
            )

            lesson_id = cursor.lastrowid

            # Add tags
            for tag_name in tags:
                # Insert or get tag
                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                tag_cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_id = tag_cursor.fetchone()["id"]

                # Link tag to lesson
                conn.execute(
                    "INSERT OR IGNORE INTO lesson_tags (lesson_id, tag_id) VALUES (?, ?)",
                    (lesson_id, tag_id),
                )

            conn.commit()
            logger.info("Added lesson %d: %s", lesson_id, title)

            return {
                "success": True,
                "id": lesson_id,
                "message": f"Lesson '{title}' added successfully",
            }

        except sqlite3.Error as e:
            logger.error("Failed to add lesson: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def add_common_error(self, args: dict) -> dict:
        """
        Add a common error to the knowledge base.

        Args:
            technology: Technology this error applies to (required)
            error_pattern: Error message or pattern (required)
            solution: How to fix this error (required)
            root_cause: What causes this error (optional)
            code_example: Code example showing the fix (optional)

        Returns:
            Created error ID and success status
        """
        technology = args.get("technology")
        error_pattern = args.get("error_pattern")
        solution = args.get("solution")
        root_cause = args.get("root_cause")
        code_example = args.get("code_example")

        # Validate required fields
        if not technology:
            return {"error": "technology is required"}
        if not error_pattern:
            return {"error": "error_pattern is required"}
        if not solution:
            return {"error": "solution is required"}

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO common_errors (technology, error_pattern, root_cause, solution, code_example)
                VALUES (?, ?, ?, ?, ?)
            """,
                (technology, error_pattern, root_cause, solution, code_example),
            )

            error_id = cursor.lastrowid
            conn.commit()
            logger.info("Added common error %d: %s", error_id, error_pattern[:50])

            return {"success": True, "id": error_id, "message": "Common error added successfully"}

        except sqlite3.Error as e:
            logger.error("Failed to add common error: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def add_swift_pattern(self, args: dict) -> dict:
        """
        Add a Swift pattern to the knowledge base.

        Args:
            pattern_name: Name of the pattern (required)
            description: What this pattern does (required)
            code_example: Code example demonstrating the pattern (required)
            when_to_use: When to use this pattern (optional)
            when_not_to_use: When NOT to use this pattern (optional)
            related_apis: Array of related API names (optional)
            ios_version: Minimum iOS version required (optional)
            swift_version: Minimum Swift version required (optional)

        Returns:
            Created pattern ID and success status
        """
        pattern_name = args.get("pattern_name")
        description = args.get("description")
        code_example = args.get("code_example")
        when_to_use = args.get("when_to_use")
        when_not_to_use = args.get("when_not_to_use")
        related_apis = args.get("related_apis", [])
        ios_version = args.get("ios_version")
        swift_version = args.get("swift_version")

        # Validate required fields
        if not pattern_name:
            return {"error": "pattern_name is required"}
        if not description:
            return {"error": "description is required"}
        if not code_example:
            return {"error": "code_example is required"}

        # Serialize related_apis as JSON
        related_apis_json = json.dumps(related_apis) if related_apis else None

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO swift_patterns
                (pattern_name, description, code_example, when_to_use, when_not_to_use,
                 related_apis, ios_version, swift_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pattern_name,
                    description,
                    code_example,
                    when_to_use,
                    when_not_to_use,
                    related_apis_json,
                    ios_version,
                    swift_version,
                ),
            )

            pattern_id = cursor.lastrowid
            conn.commit()
            logger.info("Added Swift pattern %d: %s", pattern_id, pattern_name)

            return {
                "success": True,
                "id": pattern_id,
                "message": f"Swift pattern '{pattern_name}' added successfully",
            }

        except sqlite3.Error as e:
            logger.error("Failed to add Swift pattern: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def add_session_context(self, args: dict) -> dict:
        """
        Add a session context linking to the knowledge base.

        Args:
            date: Session date in YYYY-MM-DD format (required)
            project_name: Name of the project (optional)
            session_log_path: Path to the session log file (optional)
            summary: Brief summary of what was accomplished (optional)

        Returns:
            Created session ID and success status
        """
        date_str = args.get("date")
        project_name = args.get("project_name")
        session_log_path = args.get("session_log_path")
        summary = args.get("summary")

        # Validate required fields
        if not date_str:
            return {"error": "date is required (YYYY-MM-DD format)"}

        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return {"error": "date must be in YYYY-MM-DD format"}

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO sessions (date, project_name, session_log_path, summary)
                VALUES (?, ?, ?, ?)
            """,
                (date_str, project_name, session_log_path, summary),
            )

            session_id = cursor.lastrowid
            conn.commit()
            logger.info("Added session %d: %s", session_id, date_str)

            return {
                "success": True,
                "id": session_id,
                "message": f"Session for {date_str} added successfully",
            }

        except sqlite3.Error as e:
            logger.error("Failed to add session: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def update_lesson(self, args: dict) -> dict:
        """
        Update an existing lesson with partial updates.

        Args:
            id: Lesson ID to update (required)
            title: New title (optional)
            content: New content (optional)
            category: New category (optional)
            technology: New technology (optional)
            tags: New tags - replaces existing tags (optional)
            project_context: New project context (optional)

        Returns:
            Success status and updated lesson ID
        """
        lesson_id = args.get("id")
        if not lesson_id:
            return {"error": "id is required"}

        conn = self._get_connection()
        try:
            # Check lesson exists
            cursor = conn.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,))
            if not cursor.fetchone():
                return {"error": f"Lesson with id {lesson_id} not found"}

            # Build update query dynamically for provided fields
            updates = []
            params = []

            if "title" in args:
                updates.append("title = ?")
                params.append(args["title"])
            if "content" in args:
                updates.append("content = ?")
                params.append(args["content"])
            if "category" in args:
                category = args["category"]
                if category not in ("pattern", "practice", "gotcha", "decision"):
                    return {"error": "category must be one of: pattern, practice, gotcha, decision"}
                updates.append("category = ?")
                params.append(category)
            if "technology" in args:
                updates.append("technology = ?")
                params.append(args["technology"])
            if "project_context" in args:
                updates.append("project_context = ?")
                params.append(args["project_context"])

            # Execute update if there are field updates
            if updates:
                params.append(lesson_id)
                sql = f"UPDATE lessons SET {', '.join(updates)} WHERE id = ?"
                conn.execute(sql, params)

            # Handle tags replacement if provided
            if "tags" in args:
                tags = args["tags"]
                # Remove existing tags
                conn.execute("DELETE FROM lesson_tags WHERE lesson_id = ?", (lesson_id,))

                # Add new tags
                for tag_name in tags:
                    conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                    tag_cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_id = tag_cursor.fetchone()["id"]
                    conn.execute(
                        "INSERT OR IGNORE INTO lesson_tags (lesson_id, tag_id) VALUES (?, ?)",
                        (lesson_id, tag_id),
                    )

            conn.commit()
            logger.info("Updated lesson %d", lesson_id)

            return {
                "success": True,
                "id": lesson_id,
                "message": f"Lesson {lesson_id} updated successfully",
            }

        except sqlite3.Error as e:
            logger.error("Failed to update lesson: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def increment_error_count(self, args: dict) -> dict:
        """
        Increment the occurrence count for a common error.

        Args:
            id: Error ID to increment (required)

        Returns:
            Success status and new occurrence count
        """
        error_id = args.get("id")
        if not error_id:
            return {"error": "id is required"}

        conn = self._get_connection()
        try:
            # Check error exists and get current count
            cursor = conn.execute(
                "SELECT id, occurrence_count FROM common_errors WHERE id = ?", (error_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {"error": f"Error with id {error_id} not found"}

            new_count = row["occurrence_count"] + 1
            conn.execute(
                "UPDATE common_errors SET occurrence_count = ? WHERE id = ?", (new_count, error_id)
            )
            conn.commit()
            logger.info("Incremented error %d count to %d", error_id, new_count)

            return {
                "success": True,
                "id": error_id,
                "occurrence_count": new_count,
                "message": f"Error occurrence count incremented to {new_count}",
            }

        except sqlite3.Error as e:
            logger.error("Failed to increment error count: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def get_statistics(self, args: dict) -> dict:
        """
        Get dashboard-style statistics about the knowledge base.

        Returns:
            Statistics including counts by category, technology, and recent activity
        """
        conn = self._get_connection()
        try:
            stats = {}

            # Total counts
            cursor = conn.execute("SELECT COUNT(*) as count FROM lessons")
            stats["total_lessons"] = cursor.fetchone()["count"]

            cursor = conn.execute("SELECT COUNT(*) as count FROM common_errors")
            stats["total_errors"] = cursor.fetchone()["count"]

            cursor = conn.execute("SELECT COUNT(*) as count FROM swift_patterns")
            stats["total_patterns"] = cursor.fetchone()["count"]

            cursor = conn.execute("SELECT COUNT(*) as count FROM sessions")
            stats["total_sessions"] = cursor.fetchone()["count"]

            cursor = conn.execute("SELECT COUNT(*) as count FROM tags")
            stats["total_tags"] = cursor.fetchone()["count"]

            # Lessons by category
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM lessons
                GROUP BY category
            """)
            stats["lessons_by_category"] = {row["category"]: row["count"] for row in cursor}

            # Top technologies
            cursor = conn.execute("""
                SELECT technology, COUNT(*) as count
                FROM lessons
                WHERE technology IS NOT NULL
                GROUP BY technology
                ORDER BY count DESC
                LIMIT 10
            """)
            stats["top_technologies"] = [
                {"technology": row["technology"], "count": row["count"]} for row in cursor
            ]

            # Most common errors (by occurrence)
            cursor = conn.execute("""
                SELECT id, technology, error_pattern, occurrence_count
                FROM common_errors
                ORDER BY occurrence_count DESC
                LIMIT 5
            """)
            stats["most_common_errors"] = [
                {
                    "id": row["id"],
                    "technology": row["technology"],
                    "error_pattern": row["error_pattern"][:100],
                    "occurrence_count": row["occurrence_count"],
                }
                for row in cursor
            ]

            # Recent lessons (last 5)
            cursor = conn.execute("""
                SELECT id, title, category, technology, created_at
                FROM lessons
                ORDER BY created_at DESC
                LIMIT 5
            """)
            stats["recent_lessons"] = [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "category": row["category"],
                    "technology": row["technology"],
                    "created_at": row["created_at"],
                }
                for row in cursor
            ]

            # Total error occurrences
            cursor = conn.execute("SELECT SUM(occurrence_count) as total FROM common_errors")
            stats["total_error_occurrences"] = cursor.fetchone()["total"] or 0

            return stats

        except sqlite3.Error as e:
            logger.error("Failed to get statistics: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

    async def export_knowledge(self, args: dict) -> dict:
        """
        Export knowledge base entries as JSON.

        Args:
            category: Filter by 'lesson', 'error', 'pattern', or 'all' (default: all)
            technology: Filter by technology (optional)
            include_sessions: Include session data (default: false)

        Returns:
            Exported data as JSON structure
        """
        category = args.get("category", "all")
        technology = args.get("technology")
        include_sessions = args.get("include_sessions", False)

        conn = self._get_connection()
        try:
            export = {"exported_at": datetime.now().isoformat(), "version": "1.0"}

            # Export lessons
            if category in ("all", "lesson"):
                if technology:
                    cursor = conn.execute(
                        "SELECT * FROM lessons WHERE technology = ?", (technology,)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM lessons")

                lessons = []
                for row in cursor:
                    lesson = dict(row)
                    # Get tags for this lesson
                    tag_cursor = conn.execute(
                        """
                        SELECT t.name FROM tags t
                        JOIN lesson_tags lt ON t.id = lt.tag_id
                        WHERE lt.lesson_id = ?
                    """,
                        (lesson["id"],),
                    )
                    lesson["tags"] = [t["name"] for t in tag_cursor]
                    lessons.append(lesson)
                export["lessons"] = lessons

            # Export errors
            if category in ("all", "error"):
                if technology:
                    cursor = conn.execute(
                        "SELECT * FROM common_errors WHERE technology = ?", (technology,)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM common_errors")

                export["errors"] = [dict(row) for row in cursor]

            # Export patterns
            if category in ("all", "pattern"):
                cursor = conn.execute("SELECT * FROM swift_patterns")
                patterns = []
                for row in cursor:
                    pattern = dict(row)
                    if pattern.get("related_apis"):
                        try:
                            pattern["related_apis"] = json.loads(pattern["related_apis"])
                        except json.JSONDecodeError:
                            pass
                    patterns.append(pattern)
                export["patterns"] = patterns

            # Export sessions if requested
            if include_sessions:
                cursor = conn.execute("SELECT * FROM sessions ORDER BY date DESC")
                export["sessions"] = [dict(row) for row in cursor]

            return export

        except sqlite3.Error as e:
            logger.error("Failed to export knowledge: %s", e)
            return {"error": str(e)}
        finally:
            conn.close()


# Create server instance
# kb is lazily initialized to support testing without ~/.hindsight/
_kb_instance = None


def get_kb() -> KnowledgeBaseServer:
    """Get or create the KnowledgeBaseServer instance."""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBaseServer()
    return _kb_instance


server = Server("hindsight")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="query_knowledge",
            description="Search the knowledge base for relevant learnings, errors, and patterns. "
            "Use this to find solutions to problems, best practices, and coding patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search terms to find relevant knowledge",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["lesson", "error", "pattern", "all"],
                        "description": "Filter by category: lesson, error, pattern, or all",
                        "default": "all",
                    },
                    "technology": {
                        "type": "string",
                        "description": "Filter by technology (e.g., swift, xcode, bitbucket)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10, max: 100)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="add_lesson",
            description="Add a new lesson or learning to the knowledge base. "
            "Use this to record insights, patterns, practices, gotchas, or decisions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Brief title for the lesson"},
                    "content": {
                        "type": "string",
                        "description": "Detailed description of the lesson or learning",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["pattern", "practice", "gotcha", "decision"],
                        "description": "Category: pattern (code pattern), practice (best practice), gotcha (common pitfall), decision (architectural decision)",
                    },
                    "technology": {
                        "type": "string",
                        "description": "Technology this applies to (e.g., swift, xcode, bitbucket)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization",
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Optional project this lesson came from",
                    },
                    "source_session": {
                        "type": "string",
                        "description": "Optional path to the session log where this was learned",
                    },
                },
                "required": ["title", "content", "category"],
            },
        ),
        Tool(
            name="search_errors",
            description="Search for common errors and their solutions. "
            "Use this to find fixes for error messages or known issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Error message or description to search for",
                    },
                    "technology": {
                        "type": "string",
                        "description": "Filter by technology (e.g., swift, xcode, python)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10, max: 100)",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="get_swift_patterns",
            description="Retrieve Swift coding patterns with code examples. "
            "Use this to find idiomatic Swift patterns for common tasks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Pattern name or description to search for",
                    },
                    "ios_version": {
                        "type": "string",
                        "description": "Filter patterns available for this iOS version (e.g., '17.0')",
                    },
                    "swift_version": {
                        "type": "string",
                        "description": "Filter patterns available for this Swift version (e.g., '5.9')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10, max: 100)",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="list_technologies",
            description="List all technologies in the knowledge base with entry counts. "
            "Use this to see what technologies have documented knowledge.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_tags",
            description="List all tags in the knowledge base with usage counts. "
            "Use this to browse available categories and find related lessons.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="add_common_error",
            description="Add a common error and its solution to the knowledge base. "
            "Use this to record error patterns you've encountered and how to fix them.",
            inputSchema={
                "type": "object",
                "properties": {
                    "technology": {
                        "type": "string",
                        "description": "Technology this error applies to (e.g., swift, xcode, python)",
                    },
                    "error_pattern": {
                        "type": "string",
                        "description": "The error message or pattern to match",
                    },
                    "solution": {"type": "string", "description": "How to fix this error"},
                    "root_cause": {
                        "type": "string",
                        "description": "What causes this error (optional)",
                    },
                    "code_example": {
                        "type": "string",
                        "description": "Code example showing the fix (optional)",
                    },
                },
                "required": ["technology", "error_pattern", "solution"],
            },
        ),
        Tool(
            name="add_swift_pattern",
            description="Add a Swift coding pattern to the knowledge base. "
            "Use this to record reusable Swift patterns with code examples.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern_name": {"type": "string", "description": "Name of the pattern"},
                    "description": {"type": "string", "description": "What this pattern does"},
                    "code_example": {
                        "type": "string",
                        "description": "Code example demonstrating the pattern",
                    },
                    "when_to_use": {
                        "type": "string",
                        "description": "When to use this pattern (optional)",
                    },
                    "when_not_to_use": {
                        "type": "string",
                        "description": "When NOT to use this pattern (optional)",
                    },
                    "related_apis": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Related API names (optional)",
                    },
                    "ios_version": {
                        "type": "string",
                        "description": "Minimum iOS version required (e.g., '17.0')",
                    },
                    "swift_version": {
                        "type": "string",
                        "description": "Minimum Swift version required (e.g., '5.9')",
                    },
                },
                "required": ["pattern_name", "description", "code_example"],
            },
        ),
        Tool(
            name="add_session_context",
            description="Add a development session context to the knowledge base. "
            "Use this to record session metadata and link to session logs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Session date in YYYY-MM-DD format"},
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (optional)",
                    },
                    "session_log_path": {
                        "type": "string",
                        "description": "Path to the session log file (optional)",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Brief summary of what was accomplished (optional)",
                    },
                },
                "required": ["date"],
            },
        ),
        Tool(
            name="update_lesson",
            description="Update an existing lesson in the knowledge base. "
            "Use this to modify lesson content, tags, or metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Lesson ID to update"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "content": {"type": "string", "description": "New content (optional)"},
                    "category": {
                        "type": "string",
                        "enum": ["pattern", "practice", "gotcha", "decision"],
                        "description": "New category (optional)",
                    },
                    "technology": {"type": "string", "description": "New technology (optional)"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags - replaces existing tags (optional)",
                    },
                    "project_context": {
                        "type": "string",
                        "description": "New project context (optional)",
                    },
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="increment_error_count",
            description="Increment the occurrence count for a common error. "
            "Use this when you encounter a known error again.",
            inputSchema={
                "type": "object",
                "properties": {"id": {"type": "integer", "description": "Error ID to increment"}},
                "required": ["id"],
            },
        ),
        Tool(
            name="get_statistics",
            description="Get dashboard-style statistics about the knowledge base. "
            "Use this to see an overview of stored knowledge.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="export_knowledge",
            description="Export knowledge base entries as JSON. "
            "Use this to backup or transfer knowledge data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["lesson", "error", "pattern", "all"],
                        "description": "Filter by category (default: all)",
                    },
                    "technology": {
                        "type": "string",
                        "description": "Filter by technology (optional)",
                    },
                    "include_sessions": {
                        "type": "boolean",
                        "description": "Include session data (default: false)",
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool invocations."""
    logger.info("Tool called: %s with args: %s", name, arguments)

    kb = get_kb()
    result = None
    args = arguments or {}

    if name == "query_knowledge":
        result = await kb.query_knowledge(args)
    elif name == "add_lesson":
        result = await kb.add_lesson(args)
    elif name == "search_errors":
        result = await kb.search_errors(args)
    elif name == "get_swift_patterns":
        result = await kb.get_swift_patterns(args)
    elif name == "list_technologies":
        result = await kb.list_technologies(args)
    elif name == "list_tags":
        result = await kb.list_tags(args)
    elif name == "add_common_error":
        result = await kb.add_common_error(args)
    elif name == "add_swift_pattern":
        result = await kb.add_swift_pattern(args)
    elif name == "add_session_context":
        result = await kb.add_session_context(args)
    elif name == "update_lesson":
        result = await kb.update_lesson(args)
    elif name == "increment_error_count":
        result = await kb.increment_error_count(args)
    elif name == "get_statistics":
        result = await kb.get_statistics(args)
    elif name == "export_knowledge":
        result = await kb.export_knowledge(args)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


async def main():
    """Run the MCP server."""
    logger.info("Starting Hindsight MCP Server")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
