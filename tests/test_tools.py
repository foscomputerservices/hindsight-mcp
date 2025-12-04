"""
Integration tests for MCP tool calls.
Tests the KnowledgeBaseServer methods that implement each MCP tool.
"""

import sys
from pathlib import Path

import pytest

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAddLesson:
    """Tests for add_lesson tool."""

    @pytest.mark.asyncio
    async def test_add_lesson_success(self, knowledge_base_server, sample_lesson):
        """Test adding a lesson successfully."""
        result = await knowledge_base_server.add_lesson(sample_lesson)
        assert result["success"] is True
        assert "id" in result
        assert result["id"] > 0

    @pytest.mark.asyncio
    async def test_add_lesson_missing_title(self, knowledge_base_server):
        """Test that missing title returns error."""
        result = await knowledge_base_server.add_lesson(
            {"content": "Content", "category": "practice"}
        )
        assert "error" in result
        assert "title" in result["error"]

    @pytest.mark.asyncio
    async def test_add_lesson_missing_content(self, knowledge_base_server):
        """Test that missing content returns error."""
        result = await knowledge_base_server.add_lesson({"title": "Title", "category": "practice"})
        assert "error" in result
        assert "content" in result["error"]

    @pytest.mark.asyncio
    async def test_add_lesson_invalid_category(self, knowledge_base_server):
        """Test that invalid category returns error."""
        result = await knowledge_base_server.add_lesson(
            {"title": "Title", "content": "Content", "category": "invalid"}
        )
        assert "error" in result
        assert "category" in result["error"]

    @pytest.mark.asyncio
    async def test_add_lesson_with_tags(self, knowledge_base_server):
        """Test adding a lesson with tags."""
        result = await knowledge_base_server.add_lesson(
            {
                "title": "Test",
                "content": "Content",
                "category": "practice",
                "tags": ["tag1", "tag2"],
            }
        )
        assert result["success"] is True

        # Verify tags were created
        tags_result = await knowledge_base_server.list_tags({})
        tag_names = [t["tag"] for t in tags_result]
        assert "tag1" in tag_names
        assert "tag2" in tag_names


class TestAddCommonError:
    """Tests for add_common_error tool."""

    @pytest.mark.asyncio
    async def test_add_error_success(self, knowledge_base_server, sample_error):
        """Test adding an error successfully."""
        result = await knowledge_base_server.add_common_error(sample_error)
        assert result["success"] is True
        assert "id" in result

    @pytest.mark.asyncio
    async def test_add_error_missing_required(self, knowledge_base_server):
        """Test that missing required fields return errors."""
        result = await knowledge_base_server.add_common_error({"technology": "swift"})
        assert "error" in result


class TestAddSwiftPattern:
    """Tests for add_swift_pattern tool."""

    @pytest.mark.asyncio
    async def test_add_pattern_success(self, knowledge_base_server, sample_pattern):
        """Test adding a Swift pattern successfully."""
        result = await knowledge_base_server.add_swift_pattern(sample_pattern)
        assert result["success"] is True
        assert "id" in result

    @pytest.mark.asyncio
    async def test_add_pattern_with_apis(self, knowledge_base_server):
        """Test adding pattern with related APIs."""
        result = await knowledge_base_server.add_swift_pattern(
            {
                "pattern_name": "Test Pattern",
                "description": "A test pattern",
                "code_example": "// code",
                "related_apis": ["API1", "API2"],
            }
        )
        assert result["success"] is True

        # Verify APIs are stored
        patterns = await knowledge_base_server.get_swift_patterns({"query": "Test Pattern"})
        assert len(patterns) > 0
        assert "API1" in patterns[0]["related_apis"]


class TestAddSessionContext:
    """Tests for add_session_context tool."""

    @pytest.mark.asyncio
    async def test_add_session_success(self, knowledge_base_server):
        """Test adding a session context."""
        result = await knowledge_base_server.add_session_context(
            {"date": "2025-12-03", "project_name": "TestProject", "summary": "Test session"}
        )
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_add_session_invalid_date(self, knowledge_base_server):
        """Test that invalid date format returns error."""
        result = await knowledge_base_server.add_session_context(
            {
                "date": "12-03-2025"  # Wrong format
            }
        )
        assert "error" in result
        assert "YYYY-MM-DD" in result["error"]


class TestQueryKnowledge:
    """Tests for query_knowledge tool."""

    @pytest.mark.asyncio
    async def test_query_returns_results(self, knowledge_base_server, sample_lesson):
        """Test that query returns added content."""
        await knowledge_base_server.add_lesson(sample_lesson)
        results = await knowledge_base_server.query_knowledge({"query": "test content"})
        assert len(results) > 0
        assert results[0]["type"] == "lesson"

    @pytest.mark.asyncio
    async def test_query_filter_by_category(
        self, knowledge_base_server, sample_lesson, sample_error
    ):
        """Test filtering by category."""
        await knowledge_base_server.add_lesson(sample_lesson)
        await knowledge_base_server.add_common_error(sample_error)

        # Query only lessons
        results = await knowledge_base_server.query_knowledge(
            {"query": "test", "category": "lesson"}
        )
        for r in results:
            assert r["type"] == "lesson"

    @pytest.mark.asyncio
    async def test_query_filter_by_technology(self, knowledge_base_server):
        """Test filtering by technology."""
        await knowledge_base_server.add_lesson(
            {
                "title": "Swift Lesson",
                "content": "Swift content",
                "category": "practice",
                "technology": "swift",
            }
        )
        await knowledge_base_server.add_lesson(
            {
                "title": "Python Lesson",
                "content": "Python content",
                "category": "practice",
                "technology": "python",
            }
        )

        results = await knowledge_base_server.query_knowledge(
            {"query": "content", "technology": "swift"}
        )
        for r in results:
            if "technology" in r:
                assert r["technology"] == "swift"

    @pytest.mark.asyncio
    async def test_query_respects_limit(self, knowledge_base_server):
        """Test that limit is respected."""
        # Add multiple lessons
        for i in range(10):
            await knowledge_base_server.add_lesson(
                {
                    "title": f"Lesson {i}",
                    "content": f"Content about testing {i}",
                    "category": "practice",
                }
            )

        results = await knowledge_base_server.query_knowledge({"query": "testing", "limit": 3})
        assert len(results) <= 3


class TestSearchErrors:
    """Tests for search_errors tool."""

    @pytest.mark.asyncio
    async def test_search_errors_basic(self, knowledge_base_server, sample_error):
        """Test basic error search."""
        await knowledge_base_server.add_common_error(sample_error)
        results = await knowledge_base_server.search_errors({"query": "String"})
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_errors_by_technology(self, knowledge_base_server):
        """Test error search filtered by technology."""
        await knowledge_base_server.add_common_error(
            {
                "technology": "xcode",
                "error_pattern": "Build failed",
                "solution": "Clean build folder",
            }
        )
        await knowledge_base_server.add_common_error(
            {"technology": "swift", "error_pattern": "Build failed", "solution": "Fix syntax"}
        )

        results = await knowledge_base_server.search_errors(
            {"query": "Build", "technology": "xcode"}
        )
        for r in results:
            assert r["technology"] == "xcode"


class TestGetSwiftPatterns:
    """Tests for get_swift_patterns tool."""

    @pytest.mark.asyncio
    async def test_get_patterns_basic(self, knowledge_base_server, sample_pattern):
        """Test basic pattern retrieval."""
        await knowledge_base_server.add_swift_pattern(sample_pattern)
        results = await knowledge_base_server.get_swift_patterns({"query": "Result"})
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_get_patterns_version_filter(self, knowledge_base_server):
        """Test version filtering."""
        await knowledge_base_server.add_swift_pattern(
            {
                "pattern_name": "Old Pattern",
                "description": "Works on old iOS",
                "code_example": "// code",
                "ios_version": "13.0",
            }
        )
        await knowledge_base_server.add_swift_pattern(
            {
                "pattern_name": "New Pattern",
                "description": "Requires new iOS",
                "code_example": "// code",
                "ios_version": "17.0",
            }
        )

        # Query for iOS 15 - should only get old pattern
        results = await knowledge_base_server.get_swift_patterns({"ios_version": "15.0"})
        for r in results:
            if r["ios_version"]:
                assert float(r["ios_version"]) <= 15.0


class TestUpdateLesson:
    """Tests for update_lesson tool."""

    @pytest.mark.asyncio
    async def test_update_lesson_title(self, knowledge_base_server, sample_lesson):
        """Test updating lesson title."""
        add_result = await knowledge_base_server.add_lesson(sample_lesson)
        lesson_id = add_result["id"]

        update_result = await knowledge_base_server.update_lesson(
            {"id": lesson_id, "title": "Updated Title"}
        )
        assert update_result["success"] is True

    @pytest.mark.asyncio
    async def test_update_lesson_not_found(self, knowledge_base_server):
        """Test updating non-existent lesson."""
        result = await knowledge_base_server.update_lesson({"id": 99999, "title": "New Title"})
        assert "error" in result
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_update_lesson_tags(self, knowledge_base_server, sample_lesson):
        """Test updating lesson tags."""
        add_result = await knowledge_base_server.add_lesson(sample_lesson)
        lesson_id = add_result["id"]

        await knowledge_base_server.update_lesson(
            {"id": lesson_id, "tags": ["new_tag1", "new_tag2"]}
        )

        # Query to verify tags
        results = await knowledge_base_server.query_knowledge({"query": sample_lesson["title"]})
        assert len(results) > 0
        assert "new_tag1" in results[0]["tags"]


class TestIncrementErrorCount:
    """Tests for increment_error_count tool."""

    @pytest.mark.asyncio
    async def test_increment_success(self, knowledge_base_server, sample_error):
        """Test incrementing error count."""
        add_result = await knowledge_base_server.add_common_error(sample_error)
        error_id = add_result["id"]

        result = await knowledge_base_server.increment_error_count({"id": error_id})
        assert result["success"] is True
        assert result["occurrence_count"] == 2

    @pytest.mark.asyncio
    async def test_increment_not_found(self, knowledge_base_server):
        """Test incrementing non-existent error."""
        result = await knowledge_base_server.increment_error_count({"id": 99999})
        assert "error" in result


class TestGetStatistics:
    """Tests for get_statistics tool."""

    @pytest.mark.asyncio
    async def test_statistics_structure(self, knowledge_base_server):
        """Test that statistics has expected structure."""
        stats = await knowledge_base_server.get_statistics({})
        assert "total_lessons" in stats
        assert "total_errors" in stats
        assert "total_patterns" in stats
        assert "total_sessions" in stats
        assert "total_tags" in stats

    @pytest.mark.asyncio
    async def test_statistics_counts(self, knowledge_base_server, sample_lesson):
        """Test that counts reflect added content."""
        await knowledge_base_server.add_lesson(sample_lesson)
        stats = await knowledge_base_server.get_statistics({})
        assert stats["total_lessons"] >= 1


class TestListTechnologies:
    """Tests for list_technologies tool."""

    @pytest.mark.asyncio
    async def test_list_technologies(self, knowledge_base_server):
        """Test listing technologies."""
        await knowledge_base_server.add_lesson(
            {
                "title": "Swift Lesson",
                "content": "Content",
                "category": "practice",
                "technology": "swift",
            }
        )
        await knowledge_base_server.add_common_error(
            {"technology": "swift", "error_pattern": "Error", "solution": "Fix"}
        )

        techs = await knowledge_base_server.list_technologies({})
        swift_tech = next((t for t in techs if t["technology"] == "swift"), None)
        assert swift_tech is not None
        assert swift_tech["lesson_count"] >= 1
        assert swift_tech["error_count"] >= 1


class TestListTags:
    """Tests for list_tags tool."""

    @pytest.mark.asyncio
    async def test_list_tags_with_counts(self, knowledge_base_server):
        """Test listing tags with usage counts."""
        await knowledge_base_server.add_lesson(
            {
                "title": "Lesson 1",
                "content": "Content",
                "category": "practice",
                "tags": ["common_tag"],
            }
        )
        await knowledge_base_server.add_lesson(
            {
                "title": "Lesson 2",
                "content": "Content",
                "category": "practice",
                "tags": ["common_tag"],
            }
        )

        tags = await knowledge_base_server.list_tags({})
        common = next((t for t in tags if t["tag"] == "common_tag"), None)
        assert common is not None
        assert common["usage_count"] >= 2


class TestExportKnowledge:
    """Tests for export_knowledge tool."""

    @pytest.mark.asyncio
    async def test_export_all(
        self, knowledge_base_server, sample_lesson, sample_error, sample_pattern
    ):
        """Test exporting all knowledge."""
        await knowledge_base_server.add_lesson(sample_lesson)
        await knowledge_base_server.add_common_error(sample_error)
        await knowledge_base_server.add_swift_pattern(sample_pattern)

        export = await knowledge_base_server.export_knowledge({})
        assert "exported_at" in export
        assert "lessons" in export
        assert "errors" in export
        assert "patterns" in export
        assert len(export["lessons"]) >= 1
        assert len(export["errors"]) >= 1
        assert len(export["patterns"]) >= 1

    @pytest.mark.asyncio
    async def test_export_filter_category(self, knowledge_base_server, sample_lesson):
        """Test exporting filtered by category."""
        await knowledge_base_server.add_lesson(sample_lesson)

        export = await knowledge_base_server.export_knowledge({"category": "lesson"})
        assert "lessons" in export
        assert "errors" not in export
        assert "patterns" not in export

    @pytest.mark.asyncio
    async def test_export_includes_sessions(self, knowledge_base_server):
        """Test exporting with sessions included."""
        await knowledge_base_server.add_session_context({"date": "2025-12-03", "summary": "Test"})

        export = await knowledge_base_server.export_knowledge({"include_sessions": True})
        assert "sessions" in export
        assert len(export["sessions"]) >= 1
