# Contributing to Hindsight MCP Server

Thank you for your interest in contributing to Hindsight! This document provides guidelines for contributing to the project.

## Agentic Development Welcome

This project was built with [Claude Code](https://claude.ai/code) and we enthusiastically welcome contributions made with AI assistance. Whether you're:

- Using Claude Code or other AI coding assistants
- Pair programming with an LLM
- Generating tests, documentation, or code with AI help

**All contributions are welcome!** We believe AI-assisted development is the future, and this project is proof of concept. The entire codebase, tests, and documentation were developed collaboratively between human and AI.

### Tips for Agentic Contributors

- Let your AI assistant read `CONTRIBUTING.md` and `README.md` for context
- The `.claude/` directory contains session logs and lessons learned that provide architectural context
- Run `pytest tests/ -v` to verify changes work correctly
- AI-generated commit messages are fine - just ensure they accurately describe the changes

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment:
   ```bash
   cd ~/.hindsight
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov
   ```

## Development Workflow

### Making Changes

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines below

3. Run the tests to ensure nothing is broken:
   ```bash
   pytest tests/ -v
   ```

4. Commit your changes with a clear message:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

5. Push to your fork and create a pull request

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass before submitting
- Write a clear PR description explaining the changes

## Code Style

### Python

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Keep functions focused and under 50 lines when possible
- Use descriptive variable and function names
- Add docstrings to public functions

Example:
```python
async def add_lesson(self, args: dict) -> dict:
    """
    Add a new lesson to the knowledge base.

    Args:
        args: Dictionary containing:
            - title: Lesson title (required)
            - content: Lesson content (required)
            - category: One of 'pattern', 'practice', 'gotcha', 'decision'

    Returns:
        Dictionary with 'success', 'id', and 'message' keys
    """
    # Implementation
```

### SQL

- Use uppercase for SQL keywords
- Use snake_case for table and column names
- Add comments for complex queries
- Use parameterized queries (never string formatting)

### Tests

- Test file names should start with `test_`
- Test function names should describe what they test
- Use pytest fixtures for shared setup
- Include both positive and negative test cases

## Project Structure

```
├── server.py          # Main MCP server - all tool implementations
├── schema.sql         # Database schema and triggers
├── config.json        # Default configuration
├── tests/
│   ├── conftest.py    # Shared fixtures
│   ├── test_database.py   # Database unit tests
│   ├── test_tools.py      # MCP tool integration tests
│   ├── test_fts.py        # Full-text search tests
│   └── test_performance.py # Performance benchmarks
```

## Adding New Features

### Adding a New MCP Tool

1. Add the tool method to `KnowledgeBaseServer` class in `server.py`
2. Add the tool definition to `list_tools()` function
3. Add the tool handler to `call_tool()` function
4. Write tests in `tests/test_tools.py`
5. Update README.md with documentation

### Adding Database Tables

1. Add table definition to `schema.sql`
2. If using FTS, add virtual table and triggers
3. Update seed data in `test-data.sql`
4. Add unit tests in `test_database.py`

## Running Tests

```bash
# All tests
pytest tests/ -v

# Fast tests only (excludes slow performance tests)
pytest tests/ -v -m "not slow"

# Specific test file
pytest tests/test_tools.py -v

# With coverage report
pytest tests/ --cov=server --cov-report=html
open htmlcov/index.html
```

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Steps to reproduce**: How to trigger the issue
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: OS, Python version, Claude Desktop version
6. **Logs**: Relevant log output from `~/.hindsight/logs/`

## Feature Requests

Feature requests are welcome! Please include:

1. **Use case**: Why you need this feature
2. **Proposed solution**: How you envision it working
3. **Alternatives considered**: Other approaches you thought of

## Questions

If you have questions:

1. Check existing issues and discussions
2. Review the documentation
3. Open a new discussion if needed

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
