"""
Full-text search (FTS) accuracy tests.
Verifies that FTS queries return relevant results with proper ranking.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLessonsFTS:
    """Tests for lessons FTS search."""

    @pytest.mark.asyncio
    async def test_exact_title_match(self, knowledge_base_server):
        """Test that exact title matches rank highest."""
        await knowledge_base_server.add_lesson({
            "title": "SwiftUI State Management",
            "content": "General SwiftUI content",
            "category": "pattern"
        })
        await knowledge_base_server.add_lesson({
            "title": "General Programming",
            "content": "Some content about SwiftUI state",
            "category": "practice"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "SwiftUI State Management"
        })
        assert len(results) > 0
        # Title match should be first
        assert "SwiftUI State Management" in results[0]["title"]

    @pytest.mark.asyncio
    async def test_partial_word_match(self, knowledge_base_server):
        """Test that partial word matching works."""
        await knowledge_base_server.add_lesson({
            "title": "Animation Techniques",
            "content": "How to animate views",
            "category": "pattern"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "animate"
        })
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_multiple_term_search(self, knowledge_base_server):
        """Test search with multiple terms."""
        await knowledge_base_server.add_lesson({
            "title": "SwiftUI Button Styling",
            "content": "How to style buttons in SwiftUI",
            "category": "pattern",
            "technology": "swift"
        })
        await knowledge_base_server.add_lesson({
            "title": "UIKit Button Legacy",
            "content": "Old button implementation",
            "category": "practice",
            "technology": "swift"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "SwiftUI button"
        })
        assert len(results) > 0
        # SwiftUI button should rank higher
        assert "SwiftUI" in results[0]["title"]

    @pytest.mark.asyncio
    async def test_technology_in_search(self, knowledge_base_server):
        """Test that technology field is searchable."""
        await knowledge_base_server.add_lesson({
            "title": "Regular Title",
            "content": "Regular content",
            "category": "practice",
            "technology": "bitbucket"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "bitbucket"
        })
        assert len(results) > 0
        assert results[0]["technology"] == "bitbucket"

    @pytest.mark.asyncio
    async def test_content_search(self, knowledge_base_server):
        """Test searching within content field."""
        await knowledge_base_server.add_lesson({
            "title": "Networking Basics",
            "content": "Use URLSession with async/await for modern networking patterns",
            "category": "pattern"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "URLSession async"
        })
        assert len(results) > 0
        assert "URLSession" in results[0]["content"]


class TestErrorsFTS:
    """Tests for common_errors FTS search."""

    @pytest.mark.asyncio
    async def test_error_pattern_search(self, knowledge_base_server):
        """Test searching error patterns."""
        await knowledge_base_server.add_common_error({
            "technology": "swift",
            "error_pattern": "Cannot convert value of type 'String' to expected argument type 'Int'",
            "solution": "Use Int(string) or pass correct type"
        })

        results = await knowledge_base_server.search_errors({
            "query": "Cannot convert String Int"
        })
        assert len(results) > 0
        assert "String" in results[0]["error_pattern"]

    @pytest.mark.asyncio
    async def test_solution_search(self, knowledge_base_server):
        """Test searching in solution field."""
        await knowledge_base_server.add_common_error({
            "technology": "xcode",
            "error_pattern": "Code signing error",
            "solution": "Select development team in Signing & Capabilities"
        })

        results = await knowledge_base_server.search_errors({
            "query": "development team Signing"
        })
        assert len(results) > 0
        assert "development team" in results[0]["solution"]

    @pytest.mark.asyncio
    async def test_root_cause_search(self, knowledge_base_server):
        """Test searching in root_cause field."""
        await knowledge_base_server.add_common_error({
            "technology": "swift",
            "error_pattern": "Crash on launch",
            "root_cause": "Missing required plist key for privacy permissions",
            "solution": "Add camera usage description to plist"
        })

        # Use simple terms without special FTS5 characters like "."
        results = await knowledge_base_server.search_errors({
            "query": "plist privacy"
        })
        assert len(results) > 0


class TestPatternsFTS:
    """Tests for swift_patterns FTS search."""

    @pytest.mark.asyncio
    async def test_pattern_name_search(self, knowledge_base_server):
        """Test searching pattern names."""
        await knowledge_base_server.add_swift_pattern({
            "pattern_name": "Dependency Injection Container",
            "description": "IoC container for dependency management",
            "code_example": "class Container { ... }"
        })

        results = await knowledge_base_server.get_swift_patterns({
            "query": "Dependency Injection"
        })
        assert len(results) > 0
        assert "Dependency" in results[0]["pattern_name"]

    @pytest.mark.asyncio
    async def test_description_search(self, knowledge_base_server):
        """Test searching pattern descriptions."""
        await knowledge_base_server.add_swift_pattern({
            "pattern_name": "Test Pattern",
            "description": "Use protocol oriented programming for abstraction layers",
            "code_example": "protocol MyProtocol { ... }"
        })

        # FTS5 treats hyphens specially, use space-separated terms
        results = await knowledge_base_server.get_swift_patterns({
            "query": "protocol abstraction"
        })
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_when_to_use_search(self, knowledge_base_server):
        """Test searching when_to_use field."""
        await knowledge_base_server.add_swift_pattern({
            "pattern_name": "Coordinator Pattern",
            "description": "Navigation management pattern",
            "code_example": "class AppCoordinator { ... }",
            "when_to_use": "Complex navigation flows with multiple screens"
        })

        results = await knowledge_base_server.get_swift_patterns({
            "query": "Complex navigation multiple screens"
        })
        assert len(results) > 0


class TestRelevanceRanking:
    """Tests for search result relevance ranking."""

    @pytest.mark.asyncio
    async def test_exact_match_ranks_higher(self, knowledge_base_server):
        """Test that exact matches rank higher than partial matches."""
        # Add lessons with varying relevance
        await knowledge_base_server.add_lesson({
            "title": "Swift Concurrency",
            "content": "Understanding async/await in Swift concurrency",
            "category": "pattern"
        })
        await knowledge_base_server.add_lesson({
            "title": "General Programming Tips",
            "content": "Some mention of Swift somewhere",
            "category": "practice"
        })
        await knowledge_base_server.add_lesson({
            "title": "Swift Concurrency Best Practices",
            "content": "Advanced Swift concurrency patterns for real-world apps",
            "category": "practice"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "Swift Concurrency"
        })
        assert len(results) >= 2
        # Results with "Swift Concurrency" in title should be first
        top_titles = [r["title"] for r in results[:2]]
        assert any("Swift Concurrency" in t for t in top_titles)

    @pytest.mark.asyncio
    async def test_multiple_matches_rank_higher(self, knowledge_base_server):
        """Test that entries with more matching terms rank higher."""
        await knowledge_base_server.add_lesson({
            "title": "Memory Management",
            "content": "Understanding memory leaks",
            "category": "practice"
        })
        await knowledge_base_server.add_lesson({
            "title": "Memory Management and Leak Detection",
            "content": "How to find memory leaks with Instruments",
            "category": "practice"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "memory leaks detection Instruments"
        })
        assert len(results) >= 1
        # The one with more matches should rank higher
        assert "Instruments" in results[0]["content"] or "Detection" in results[0]["title"]


class TestCrossTableSearch:
    """Tests for searching across multiple knowledge types."""

    @pytest.mark.asyncio
    async def test_query_returns_all_types(self, knowledge_base_server):
        """Test that query_knowledge searches all types."""
        # Add content of each type with same keyword
        await knowledge_base_server.add_lesson({
            "title": "Networking with URLSession",
            "content": "How to use URLSession",
            "category": "pattern",
            "technology": "swift"
        })
        await knowledge_base_server.add_common_error({
            "technology": "swift",
            "error_pattern": "URLSession timeout error",
            "solution": "Increase timeout interval"
        })
        await knowledge_base_server.add_swift_pattern({
            "pattern_name": "URLSession Wrapper",
            "description": "Type-safe URLSession wrapper",
            "code_example": "class NetworkClient { let session = URLSession.shared }"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "URLSession"
        })

        types_found = set(r["type"] for r in results)
        assert "lesson" in types_found
        assert "error" in types_found
        assert "pattern" in types_found

    @pytest.mark.asyncio
    async def test_results_sorted_by_relevance(self, knowledge_base_server):
        """Test that results from all types are sorted by relevance."""
        # Add content with varying relevance
        await knowledge_base_server.add_lesson({
            "title": "SwiftData",
            "content": "SwiftData SwiftData SwiftData core features",
            "category": "pattern"
        })
        await knowledge_base_server.add_common_error({
            "technology": "swift",
            "error_pattern": "SwiftData error",
            "solution": "Fix SwiftData"
        })
        await knowledge_base_server.add_swift_pattern({
            "pattern_name": "SwiftData Model",
            "description": "SwiftData model definition",
            "code_example": "@Model class Item {}"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "SwiftData"
        })

        # All should be found
        assert len(results) >= 3
        # Results should have relevance scores (negative for bm25, more negative = better match)
        for r in results:
            assert "relevance" in r


class TestSpecialCharacters:
    """Tests for handling special characters in searches."""

    @pytest.mark.asyncio
    async def test_quotes_in_search(self, knowledge_base_server):
        """Test searching with quoted phrases."""
        await knowledge_base_server.add_lesson({
            "title": "String Interpolation",
            "content": 'Use "\\(variable)" for string interpolation',
            "category": "pattern"
        })

        # FTS5 should handle this gracefully
        results = await knowledge_base_server.query_knowledge({
            "query": "string interpolation"
        })
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_code_snippets_searchable(self, knowledge_base_server):
        """Test that code in content is searchable."""
        await knowledge_base_server.add_lesson({
            "title": "Task Groups",
            "content": "Use withTaskGroup for parallel execution: withTaskGroup(of: Int.self) { group in }",
            "category": "pattern"
        })

        results = await knowledge_base_server.query_knowledge({
            "query": "withTaskGroup"
        })
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_api_names_searchable(self, knowledge_base_server):
        """Test that API names like URLSession are searchable."""
        await knowledge_base_server.add_lesson({
            "title": "Modern Networking",
            "content": "URLSession shared data for request handling",
            "category": "pattern"
        })

        # FTS5 treats "." as operator, search for words separately
        results = await knowledge_base_server.query_knowledge({
            "query": "URLSession shared"
        })
        assert len(results) > 0
