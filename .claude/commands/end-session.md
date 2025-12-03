# End Session

Wrap up this session by updating documentation, capturing knowledge, and creating a session log.

## Required Steps

1. **Check `.claude/sessions/README.md`** for the established directory structure before creating any files

2. **Update documentation** if any user-facing features changed

3. **Update `.claude/LESSONS_LEARNED.md`** if new architectural patterns or design decisions were established

4. **Create session log** following the established structure:
   - Location: `.claude/sessions/YYYY-MM-DD/<descriptive-name>.md`
   - NOT flat files with date prefixes
   - Review existing session logs for format consistency
   - Include: Objective, Context, Design Decisions, Implementation, Testing, Outcome

5. **Update `.claude/sessions/README.md`** to list the new session log in the appropriate section

## Hindsight Knowledge Base Integration

If lessons, errors, or patterns were discovered during this session, add them to Hindsight using the MCP tools:

### For Lessons Learned
Use the `add_lesson` tool with:
- `title`: Descriptive title
- `content`: What was learned
- `category`: One of `pattern`, `practice`, `gotcha`, `decision`
- `technology`: Primary technology (Swift, Python, etc.)
- `tags`: Relevant tags (array)

### For Common Errors
Use the `add_common_error` tool with:
- `technology`: Where the error occurs
- `error_pattern`: The error message or pattern
- `solution`: How to fix it
- `root_cause`: Why it happens (optional)
- `code_example`: Fix example (optional)

### For Swift Patterns
Use the `add_swift_pattern` tool with:
- `pattern_name`: Descriptive name
- `description`: When and how to use
- `code_example`: Working code example
- `swift_version`: Minimum version (optional)
- `ios_version`: Minimum iOS version (optional)

## Format Reference

Check existing session logs in `.claude/sessions/` for format consistency and level of detail.

See `docs/session-kb-format.md` for detailed KB entry format if adding a `## Knowledge Base Entries` section to your session log.
