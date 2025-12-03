# Session Knowledge Base Entry Format

This document defines the markdown format for capturing knowledge base entries at the end of development sessions. These entries are parsed by `parse-session-kb.swift` and inserted into the Hindsight knowledge base via MCP tools.

## Overview

Add a `## Knowledge Base Entries` section to your session log to capture lessons learned, common errors encountered, and useful patterns discovered during the session.

## Section Format

```markdown
## Knowledge Base Entries

### Lessons

#### [Lesson Title]
- **Category**: pattern | practice | gotcha | decision
- **Technology**: Swift, SwiftUI, Xcode, etc.
- **Tags**: tag1, tag2, tag3
- **Project**: optional project context

[Lesson content - can be multiple paragraphs]

---

### Errors

#### [Error Pattern or Message]
- **Technology**: Swift, Xcode, etc.
- **Root Cause**: Why this error occurs
- **Solution**: How to fix it

```swift
// Optional code example showing the fix
```

---

### Patterns

#### [Pattern Name]
- **Swift Version**: 6.0
- **iOS Version**: 18.0
- **When to Use**: Description of use cases
- **When NOT to Use**: Anti-patterns or limitations
- **Related APIs**: API1, API2, API3

```swift
// Required code example
```

[Optional additional description]
```

## Field Reference

### Lessons

| Field | Required | Description |
|-------|----------|-------------|
| Title | Yes | H4 heading becomes the lesson title |
| Category | Yes | One of: `pattern`, `practice`, `gotcha`, `decision` |
| Technology | No | Primary technology (e.g., Swift, SwiftUI) |
| Tags | No | Comma-separated list of tags |
| Project | No | Project context for this lesson |
| Content | Yes | All text after metadata until next entry |

### Errors

| Field | Required | Description |
|-------|----------|-------------|
| Error Pattern | Yes | H4 heading becomes the error pattern |
| Technology | Yes | Technology where this error occurs |
| Root Cause | No | Explanation of why the error occurs |
| Solution | Yes | How to resolve the error |
| Code Example | No | Code block showing the fix |

### Patterns

| Field | Required | Description |
|-------|----------|-------------|
| Pattern Name | Yes | H4 heading becomes the pattern name |
| Swift Version | No | Minimum Swift version required |
| iOS Version | No | Minimum iOS version required |
| When to Use | No | Use case description |
| When NOT to Use | No | Anti-patterns or limitations |
| Related APIs | No | Comma-separated list of related APIs |
| Code Example | Yes | Code block demonstrating the pattern |
| Description | No | Additional text after code block |

## Complete Example

```markdown
## Knowledge Base Entries

### Lessons

#### Use @Observable macro for simple state management
- **Category**: practice
- **Technology**: SwiftUI
- **Tags**: state-management, observation, iOS17

For simple view models that don't need Combine publishers, the `@Observable` macro
provides cleaner syntax and automatic dependency tracking. Views automatically
update when observed properties change without explicit `@Published` wrappers.

---

#### Always validate date formats before parsing
- **Category**: gotcha
- **Technology**: Swift
- **Tags**: dates, parsing, localization

DateFormatter with fixed formats can fail on devices with non-Gregorian calendars.
Always set `dateFormatter.locale = Locale(identifier: "en_US_POSIX")` before
parsing ISO 8601 dates.

---

### Errors

#### Type 'X' does not conform to protocol 'Sendable'
- **Technology**: Swift
- **Root Cause**: Swift 6 strict concurrency checking flags types that cross actor boundaries without Sendable conformance
- **Solution**: Add `@unchecked Sendable` for classes you control, or refactor to use actors

```swift
// Before: Compiler error
class MyManager { ... }

// After: Explicit Sendable conformance
final class MyManager: @unchecked Sendable { ... }
```

---

### Patterns

#### Task Group for Parallel Network Requests
- **Swift Version**: 5.9
- **iOS Version**: 17.0
- **When to Use**: Fetching multiple independent resources concurrently
- **When NOT to Use**: Sequential dependent requests, single request scenarios
- **Related APIs**: TaskGroup, withTaskGroup, async let

```swift
func fetchAllData() async throws -> [Data] {
    try await withTaskGroup(of: Data.self) { group in
        for url in urls {
            group.addTask {
                try await URLSession.shared.data(from: url).0
            }
        }
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

Prefer `async let` for a small fixed number of concurrent operations.
Use TaskGroup when the number of operations is dynamic.
```

## Parser Output

The `parse-session-kb.swift` script outputs JSON compatible with MCP tool inputs:

```json
{
  "lessons": [
    {
      "title": "Use @Observable macro for simple state management",
      "category": "practice",
      "technology": "SwiftUI",
      "tags": ["state-management", "observation", "iOS17"],
      "content": "For simple view models..."
    }
  ],
  "errors": [
    {
      "error_pattern": "Type 'X' does not conform to protocol 'Sendable'",
      "technology": "Swift",
      "root_cause": "Swift 6 strict concurrency...",
      "solution": "Add @unchecked Sendable...",
      "code_example": "// Before: Compiler error..."
    }
  ],
  "patterns": [
    {
      "pattern_name": "Task Group for Parallel Network Requests",
      "swift_version": "5.9",
      "ios_version": "17.0",
      "when_to_use": "Fetching multiple independent resources...",
      "when_not_to_use": "Sequential dependent requests...",
      "related_apis": ["TaskGroup", "withTaskGroup", "async let"],
      "code_example": "func fetchAllData()...",
      "description": "Prefer async let for..."
    }
  ]
}
```

## Integration

After creating a session log with KB entries:

1. Run the parser: `swift-sh parse-session-kb.swift session-log.md`
2. The script outputs JSON to stdout
3. Use the JSON with MCP tools (`add_lesson`, `add_common_error`, `add_swift_pattern`)

Or use the integrated workflow that automatically parses and inserts entries.
