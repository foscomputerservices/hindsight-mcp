"""
Performance tests for Hindsight MCP Server.
Verifies query times stay under 100ms even with large datasets.
"""

import random
import string
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_random_text(min_words=10, max_words=50):
    """Generate random text content."""
    words = [
        "swift", "swiftui", "xcode", "ios", "development", "pattern", "error",
        "solution", "code", "function", "class", "struct", "protocol", "async",
        "await", "actor", "task", "memory", "performance", "debug", "test",
        "build", "deploy", "api", "network", "database", "cache", "state",
        "view", "model", "controller", "navigation", "animation", "gesture"
    ]
    num_words = random.randint(min_words, max_words)
    return " ".join(random.choices(words, k=num_words))


def generate_random_title(max_words=5):
    """Generate random title."""
    words = [
        "Swift", "SwiftUI", "Xcode", "iOS", "Pattern", "Error", "Solution",
        "Best", "Practice", "Guide", "Tips", "Tricks", "Advanced", "Basic",
        "Modern", "Classic", "New", "Updated", "Fixed", "Improved"
    ]
    num_words = random.randint(2, max_words)
    return " ".join(random.choices(words, k=num_words))


class TestQueryPerformance:
    """Tests for query performance."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_query_under_100ms_small_dataset(self, knowledge_base_server):
        """Test query time with small dataset (100 entries)."""
        # Add 100 lessons
        for i in range(100):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}: {generate_random_title()}",
                "content": generate_random_text(),
                "category": random.choice(["pattern", "practice", "gotcha", "decision"]),
                "technology": random.choice(["swift", "xcode", "python", "bitbucket"])
            })

        # Run queries and measure time
        queries = ["swift development", "error solution", "async await", "performance"]
        for query in queries:
            start = time.perf_counter()
            await knowledge_base_server.query_knowledge({"query": query, "limit": 10})
            elapsed_ms = (time.perf_counter() - start) * 1000

            assert elapsed_ms < 100, f"Query '{query}' took {elapsed_ms:.2f}ms (>100ms)"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_query_under_100ms_medium_dataset(self, knowledge_base_server):
        """Test query time with medium dataset (1000 entries)."""
        # Add 1000 lessons
        for i in range(1000):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}: {generate_random_title()}",
                "content": generate_random_text(20, 100),
                "category": random.choice(["pattern", "practice", "gotcha", "decision"]),
                "technology": random.choice(["swift", "xcode", "python", "bitbucket"])
            })

        queries = ["swift pattern", "error code", "database cache"]
        for query in queries:
            start = time.perf_counter()
            await knowledge_base_server.query_knowledge({"query": query, "limit": 10})
            elapsed_ms = (time.perf_counter() - start) * 1000

            assert elapsed_ms < 100, f"Query '{query}' took {elapsed_ms:.2f}ms with 1K entries"

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_query_under_100ms_large_dataset(self, knowledge_base_server):
        """Test query time with large dataset (10000+ entries)."""
        categories = ["pattern", "practice", "gotcha", "decision"]
        technologies = ["swift", "xcode", "python", "bitbucket", "git", "api", "database"]

        # Add 10000 lessons in batches for performance
        print("\nPopulating 10,000 entries...")
        for batch in range(100):
            for i in range(100):
                await knowledge_base_server.add_lesson({
                    "title": f"L{batch*100+i}: {generate_random_title()}",
                    "content": generate_random_text(30, 150),
                    "category": random.choice(categories),
                    "technology": random.choice(technologies)
                })

        # Add 500 errors
        for i in range(500):
            await knowledge_base_server.add_common_error({
                "technology": random.choice(technologies),
                "error_pattern": f"Error {i}: {generate_random_text(5, 15)}",
                "solution": generate_random_text(10, 30)
            })

        # Add 200 patterns
        for i in range(200):
            await knowledge_base_server.add_swift_pattern({
                "pattern_name": f"Pattern {i}: {generate_random_title(3)}",
                "description": generate_random_text(10, 30),
                "code_example": f"// Code example {i}\nfunc example{i}() {{}}"
            })

        print("Testing queries on 10,700+ entries...")

        # Test various query types
        test_cases = [
            ("swift development pattern", "Full-text multi-word"),
            ("error", "Single common word"),
            ("async await concurrency", "Technical terms"),
            ("xcode build", "Tool-specific"),
            ("network api database", "Multi-technology"),
        ]

        results = []
        for query, description in test_cases:
            times = []
            for _ in range(5):  # Run each query 5 times
                start = time.perf_counter()
                await knowledge_base_server.query_knowledge({"query": query, "limit": 10})
                elapsed_ms = (time.perf_counter() - start) * 1000
                times.append(elapsed_ms)

            avg_time = sum(times) / len(times)
            max_time = max(times)
            results.append((description, query, avg_time, max_time))
            print(f"  {description}: avg={avg_time:.2f}ms, max={max_time:.2f}ms")

            assert max_time < 100, f"Query '{query}' max time {max_time:.2f}ms exceeds 100ms"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_filtered_query_performance(self, knowledge_base_server):
        """Test performance of filtered queries."""
        # Add diverse entries
        for i in range(500):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}",
                "content": generate_random_text(),
                "category": random.choice(["pattern", "practice", "gotcha", "decision"]),
                "technology": random.choice(["swift", "xcode", "python"])
            })

        # Test with technology filter
        start = time.perf_counter()
        await knowledge_base_server.query_knowledge({
            "query": "pattern code",
            "technology": "swift",
            "limit": 10
        })
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 100, f"Filtered query took {elapsed_ms:.2f}ms"

        # Test with category filter
        start = time.perf_counter()
        await knowledge_base_server.query_knowledge({
            "query": "development",
            "category": "pattern",
            "limit": 10
        })
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 100, f"Category filtered query took {elapsed_ms:.2f}ms"


class TestStatisticsPerformance:
    """Tests for statistics query performance."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_statistics_under_100ms(self, knowledge_base_server):
        """Test that get_statistics is fast even with large dataset."""
        # Add 1000 entries of various types
        for i in range(500):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}",
                "content": generate_random_text(),
                "category": random.choice(["pattern", "practice", "gotcha", "decision"]),
                "technology": random.choice(["swift", "xcode", "python"])
            })
        for i in range(300):
            await knowledge_base_server.add_common_error({
                "technology": random.choice(["swift", "xcode", "python"]),
                "error_pattern": f"Error {i}",
                "solution": "Solution"
            })
        for i in range(200):
            await knowledge_base_server.add_swift_pattern({
                "pattern_name": f"Pattern {i}",
                "description": "Description",
                "code_example": "Code"
            })

        start = time.perf_counter()
        await knowledge_base_server.get_statistics({})
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 100, f"Statistics took {elapsed_ms:.2f}ms"


class TestExportPerformance:
    """Tests for export operation performance."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_export_performance(self, knowledge_base_server):
        """Test export performance with medium dataset."""
        # Add 200 entries
        for i in range(200):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}",
                "content": generate_random_text(50, 200),
                "category": random.choice(["pattern", "practice", "gotcha", "decision"]),
                "technology": "swift",
                "tags": [f"tag{i % 10}"]
            })

        start = time.perf_counter()
        export = await knowledge_base_server.export_knowledge({})
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 500, f"Export took {elapsed_ms:.2f}ms (>500ms)"
        assert len(export["lessons"]) == 200


class TestInsertPerformance:
    """Tests for insert operation performance."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_bulk_insert_performance(self, knowledge_base_server):
        """Test performance of bulk inserts."""
        start = time.perf_counter()

        # Insert 100 lessons
        for i in range(100):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}",
                "content": generate_random_text(),
                "category": "practice",
                "technology": "swift"
            })

        elapsed_ms = (time.perf_counter() - start) * 1000
        per_insert_ms = elapsed_ms / 100

        print(f"\nBulk insert: {elapsed_ms:.2f}ms total, {per_insert_ms:.2f}ms per insert")
        assert per_insert_ms < 10, f"Per-insert time {per_insert_ms:.2f}ms is too slow"

    @pytest.mark.asyncio
    async def test_insert_with_tags_performance(self, knowledge_base_server):
        """Test that inserts with tags are performant."""
        start = time.perf_counter()

        for i in range(50):
            await knowledge_base_server.add_lesson({
                "title": f"Tagged Lesson {i}",
                "content": "Content",
                "category": "practice",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
            })

        elapsed_ms = (time.perf_counter() - start) * 1000
        per_insert_ms = elapsed_ms / 50

        assert per_insert_ms < 20, f"Insert with tags took {per_insert_ms:.2f}ms per insert"


class TestConcurrentOperations:
    """Tests for concurrent operation performance."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_reads(self, knowledge_base_server):
        """Test concurrent read operations."""
        import asyncio

        # Populate with some data
        for i in range(100):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}",
                "content": f"Content about topic {i} with swift and xcode",
                "category": "practice",
                "technology": "swift"
            })

        # Run 10 concurrent queries
        async def run_query(query):
            start = time.perf_counter()
            await knowledge_base_server.query_knowledge({"query": query})
            return (time.perf_counter() - start) * 1000

        queries = ["swift", "xcode", "pattern", "error", "content",
                   "topic", "practice", "development", "code", "function"]

        start = time.perf_counter()
        times = await asyncio.gather(*[run_query(q) for q in queries])
        total_time = (time.perf_counter() - start) * 1000

        avg_time = sum(times) / len(times)
        max_time = max(times)

        print(f"\nConcurrent reads: total={total_time:.2f}ms, avg={avg_time:.2f}ms, max={max_time:.2f}ms")
        assert max_time < 200, f"Concurrent query max time {max_time:.2f}ms too slow"


class TestMemoryUsage:
    """Tests for memory-efficient operations."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_large_result_memory(self, knowledge_base_server):
        """Test that large result sets don't cause memory issues."""
        # Add entries with large content
        for i in range(100):
            await knowledge_base_server.add_lesson({
                "title": f"Large Content Lesson {i}",
                "content": generate_random_text(200, 500),  # Large content
                "category": "practice",
                "technology": "swift"
            })

        # Query and get results
        results = await knowledge_base_server.query_knowledge({
            "query": "swift",
            "limit": 100
        })

        assert len(results) <= 100
        # If we get here without memory errors, the test passes

    @pytest.mark.asyncio
    async def test_limit_enforcement(self, knowledge_base_server):
        """Test that limit parameter is properly enforced."""
        # Add 50 entries
        for i in range(50):
            await knowledge_base_server.add_lesson({
                "title": f"Lesson {i}",
                "content": "Swift development content",
                "category": "practice"
            })

        # Request with small limit
        results = await knowledge_base_server.query_knowledge({
            "query": "development",
            "limit": 5
        })
        assert len(results) <= 5

        # Request with default limit
        results = await knowledge_base_server.query_knowledge({
            "query": "development"
        })
        assert len(results) <= 10  # Default limit
