# Lessons Learned

Architectural patterns and design decisions established during Hindsight MCP Server development.

## FTS5 External Content Tables

**Issue**: FTS5 with `content='table_name'` doesn't automatically sync deletes.

**Solution**: Triggers handle INSERT/UPDATE, but DELETE requires explicit FTS rebuild:
```sql
INSERT INTO lessons_fts(lessons_fts) VALUES('rebuild');
```

**Lesson**: For production use, consider periodic FTS index rebuilds or use contentless FTS tables.

## FTS5 Query Syntax

**Issue**: Special characters like `.` and `-` are FTS5 operators, causing syntax errors.

**Solution**:
- Avoid using `.` in search terms (e.g., "URLSession.shared" fails)
- Hyphens create column references (e.g., "protocol-oriented" looks for column "oriented")
- Use space-separated terms or quote phrases

**Lesson**: Document FTS5 query limitations for users; consider query preprocessing.

## MCP Server Configuration

**Pattern**: Support multiple configuration methods for flexibility:
1. Config file with defaults (`config.json`)
2. Environment variable overrides (`HINDSIGHT_*`)
3. Command-line for MCP client configuration

**Lesson**: Layer configuration sources with clear precedence.

## Database Retry Logic

**Pattern**: Exponential backoff for database connections:
```python
retry_delay = 0.5
for attempt in range(retries + 1):
    try:
        return connect()
    except:
        time.sleep(retry_delay)
        retry_delay *= 2  # Exponential backoff
```

**Lesson**: SQLite busy timeout alone isn't sufficient; retry logic handles transient failures.

## Test Organization

**Pattern**: Separate tests by concern:
- `test_database.py` - Low-level database operations
- `test_tools.py` - MCP tool integration
- `test_fts.py` - Search accuracy
- `test_performance.py` - Performance benchmarks

**Lesson**: Use pytest markers (`@pytest.mark.slow`) for selective test execution.

## Documentation Structure

**Pattern**: Separate documentation by audience:
- `README.md` - Quick start for users
- `TROUBLESHOOTING.md` - Problem resolution
- `CONTRIBUTING.md` - Developer guidelines
- `docs/USAGE_EXAMPLES.md` - Practical examples

**Lesson**: Keep README focused; move details to separate files.

## Installation vs Repository Location

**Issue**: Built directly in install location (`~/.hindsight/`) instead of source repository.

**Lesson**: Always develop in repository location, then document install paths for users. The shebang should use `#!/usr/bin/env python3` for portability.

## Agentic Open Source Projects

**Pattern**: For projects built with AI assistance, explicitly welcome AI-assisted contributions in CONTRIBUTING.md.

**Benefits**:
- Signals that AI-generated PRs are first-class citizens
- Provides context hints (e.g., `.claude/` directory) for AI assistants
- Embraces the collaborative human+AI development model

**Lesson**: AI-built projects should be transparent about their origins and welcoming to similar contribution styles.
