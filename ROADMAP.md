# Hindsight Roadmap

This document outlines planned improvements for future releases, organized by priority and complexity.

## Version 1.1 - Performance & Reliability

### Database Indexes
**Priority: High | Complexity: Low**

Add indexes for frequently filtered columns to improve query performance at scale.

```sql
-- Add to schema.sql
CREATE INDEX IF NOT EXISTS idx_lessons_technology ON lessons(technology);
CREATE INDEX IF NOT EXISTS idx_errors_technology ON common_errors(technology);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON lessons(category);
CREATE INDEX IF NOT EXISTS idx_patterns_ios_version ON swift_patterns(ios_version);
```

**Files to modify:**
- `schema.sql` - Add index definitions
- `install.sh` - Ensure indexes created on upgrade (already runs schema.sql)

---

### Transaction Safety for Multi-Step Operations
**Priority: High | Complexity: Medium**

Wrap operations that touch multiple tables in explicit transactions to prevent partial failures.

**Affected methods in `server.py`:**
- `add_lesson()` - Inserts lesson + creates/links tags
- `update_lesson()` - Updates lesson + may modify tag links

**Implementation:**
```python
async def add_lesson(self, ...):
    conn = self._get_connection()
    try:
        conn.execute("BEGIN TRANSACTION")
        # ... insert lesson
        # ... handle tags
        conn.execute("COMMIT")
    except Exception as e:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
```

**Files to modify:**
- `server.py` - Wrap multi-step operations
- `tests/test_tools.py` - Add tests for partial failure scenarios

---

### Optimize Tag Filtering in Search
**Priority: High | Complexity: Medium**

Currently tag filtering happens in Python after FTS query returns results. Move to SQL for efficiency with large datasets.

**Current approach (`server.py:~309`):**
```python
# Filters in Python - inefficient
if tags:
    results = [r for r in results if has_matching_tags(r)]
```

**Improved approach:**
```sql
-- Filter in SQL using subquery
SELECT ... FROM lessons l
JOIN lessons_fts ON lessons_fts.rowid = l.id
WHERE lessons_fts MATCH ?
  AND EXISTS (
    SELECT 1 FROM lesson_tags lt
    JOIN tags t ON lt.tag_id = t.id
    WHERE lt.lesson_id = l.id AND t.name IN (?, ?, ?)
  )
```

**Files to modify:**
- `server.py` - Refactor `_search_lessons()` method
- `tests/test_fts.py` - Add performance test for tag-filtered searches

---

## Version 1.2 - Code Organization

### Modularize server.py
**Priority: Medium | Complexity: Medium**

Split the 1,495-line `server.py` into focused modules for better maintainability and testability.

**Proposed structure:**
```
hindsight/
├── __init__.py
├── config.py          # Configuration loading and validation
├── database.py        # Connection management, retry logic, base operations
├── models.py          # Data classes for lessons, errors, patterns
├── tools/
│   ├── __init__.py
│   ├── query.py       # query_knowledge, search_errors, get_swift_patterns
│   ├── mutation.py    # add_lesson, add_error, add_pattern, update_lesson
│   ├── stats.py       # get_statistics, list_technologies, list_tags
│   └── export.py      # export_knowledge
└── server.py          # MCP server setup, tool registration (thin wrapper)
```

**Migration strategy:**
1. Create new module structure alongside existing `server.py`
2. Move code incrementally with tests passing at each step
3. Keep `server.py` as the entry point, importing from modules
4. Update `install.sh` to copy module directory

**Files to create:**
- `hindsight/` directory with modules
- Update `install.sh` for new structure

---

## Version 1.3 - Test Coverage Expansion

### Concurrency Testing
**Priority: Medium | Complexity: Medium**

Add tests for race conditions and concurrent access patterns.

**New tests to add:**
```python
# tests/test_concurrency.py

@pytest.mark.asyncio
async def test_concurrent_lesson_inserts():
    """Multiple simultaneous inserts should all succeed."""

@pytest.mark.asyncio
async def test_concurrent_tag_creation():
    """Same tag created by multiple inserts should not duplicate."""

@pytest.mark.asyncio
async def test_read_during_write():
    """Reads should not block during writes."""

@pytest.mark.asyncio
async def test_concurrent_error_increment():
    """Multiple increments should all be counted."""
```

**Files to create:**
- `tests/test_concurrency.py`

---

### Configuration and Retry Logic Tests
**Priority: Medium | Complexity: Low**

Add explicit tests for configuration loading and database retry behavior.

**New tests to add:**
```python
# tests/test_config.py

def test_default_config_loading():
    """Default config values are applied."""

def test_config_file_override():
    """config.json values override defaults."""

def test_env_var_override():
    """Environment variables override config file."""

def test_env_var_precedence():
    """Env vars take precedence over all other sources."""

# tests/test_database.py (additions)

def test_retry_on_busy_database():
    """Retries with exponential backoff on SQLITE_BUSY."""

def test_max_retries_exceeded():
    """Raises after max_retries attempts."""

def test_retry_delay_progression():
    """Delay doubles between retry attempts."""
```

**Files to modify/create:**
- `tests/test_config.py` (new)
- `tests/test_database.py` (additions)

---

### Max Limit Enforcement Tests
**Priority: Low | Complexity: Low**

Verify that search results respect the configured `max_limit` (100).

```python
# tests/test_tools.py (additions)

@pytest.mark.slow
async def test_query_respects_max_limit(large_populated_db):
    """Queries never return more than max_limit results."""
    result = await server.call_tool("query_knowledge", {"query": "test", "limit": 500})
    assert len(result) <= 100
```

---

## Version 1.4 - Input Validation & Safety

### Enhanced Input Validation
**Priority: Medium | Complexity: Low**

Add comprehensive validation for all inputs.

**Validations to add:**
- Title length limit (e.g., 500 characters)
- Content size limit (e.g., 100KB)
- Technology value validation against allowed list
- URL format validation for `session_log_path`
- Tag name validation (alphanumeric, hyphens, max length)

**Implementation:**
```python
# In server.py or new validation.py

MAX_TITLE_LENGTH = 500
MAX_CONTENT_SIZE = 100 * 1024  # 100KB
ALLOWED_TECHNOLOGIES = ["swift", "python", "javascript", ...]  # or dynamic from DB

def validate_lesson(title: str, content: str, technology: str | None) -> list[str]:
    errors = []
    if len(title) > MAX_TITLE_LENGTH:
        errors.append(f"Title exceeds {MAX_TITLE_LENGTH} characters")
    if len(content) > MAX_CONTENT_SIZE:
        errors.append(f"Content exceeds {MAX_CONTENT_SIZE} bytes")
    # ... more validations
    return errors
```

**Files to modify:**
- `server.py` - Add validation calls before database operations
- `tests/test_tools.py` - Add validation error tests

---

## Version 1.5 - Features

### Soft Delete with Recovery
**Priority: Low | Complexity: Medium**

Add ability to recover deleted entries.

**Schema changes:**
```sql
-- Add to each main table
ALTER TABLE lessons ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL;
ALTER TABLE common_errors ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL;
ALTER TABLE swift_patterns ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL;

-- Modify queries to exclude deleted
-- WHERE deleted_at IS NULL
```

**New tools:**
- `delete_lesson` - Sets deleted_at timestamp
- `restore_lesson` - Clears deleted_at timestamp
- `purge_deleted` - Permanently removes entries deleted > 30 days ago

**Files to modify:**
- `schema.sql` - Add deleted_at columns
- `server.py` - Add delete/restore tools, modify queries
- `tests/test_tools.py` - Add deletion/restoration tests

---

### Search Pagination
**Priority: Low | Complexity: Low**

Add offset parameter for paginated results.

**Tool changes:**
```python
# query_knowledge gains offset parameter
{
    "query": "async",
    "limit": 10,
    "offset": 20  # Skip first 20 results
}

# Response includes pagination info
{
    "results": [...],
    "total_count": 150,
    "offset": 20,
    "limit": 10,
    "has_more": True
}
```

**Files to modify:**
- `server.py` - Add offset to search methods, return total count
- `tests/test_tools.py` - Add pagination tests

---

## Version 2.0 - Platform & Architecture

### Cross-Platform Script Improvements
**Priority: Low | Complexity: Low**

Make shell scripts work reliably on macOS, Linux, and WSL.

**Changes to `backup.sh`:**
- Use portable `stat` syntax or pure shell alternatives
- Add `numfmt` fallback for Linux systems without it
- Test on Ubuntu, Fedora, WSL2

**Consider adding:**
- `backup.ps1` for native Windows support
- Docker-based backup for containerized deployments

---

### Health Check Tool
**Priority: Low | Complexity: Low**

Add MCP tool for monitoring deployments.

```python
# New tool: health_check
{
    "database_status": "ok",
    "database_size_bytes": 1048576,
    "entry_counts": {
        "lessons": 150,
        "errors": 45,
        "patterns": 23
    },
    "fts_status": "ok",
    "last_backup": "2024-01-15T03:00:00Z",
    "uptime_seconds": 86400
}
```

---

### Metrics Logging
**Priority: Low | Complexity: Medium**

Add structured metrics for performance monitoring.

**Metrics to track:**
- Queries per minute
- Average query response time
- Insert rate
- Error rate
- Database size over time

**Implementation options:**
- Structured JSON logging
- Optional StatsD/Prometheus integration
- Local metrics file for analysis

---

## Contributing

When working on roadmap items:

1. Create a feature branch: `git checkout -b feature/transaction-safety`
2. Implement with tests passing at each step
3. Update CHANGELOG.md with changes
4. Submit PR referencing the roadmap item

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Version History

| Version | Focus | Status |
|---------|-------|--------|
| 1.0.0 | Initial release | ✅ Complete |
| 1.1 | Performance & Reliability | 📋 Planned |
| 1.2 | Code Organization | 📋 Planned |
| 1.3 | Test Coverage | 📋 Planned |
| 1.4 | Input Validation | 📋 Planned |
| 1.5 | Features | 📋 Planned |
| 2.0 | Platform & Architecture | 📋 Planned |
