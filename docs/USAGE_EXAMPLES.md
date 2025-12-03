# Hindsight Usage Examples

Practical examples of using the Hindsight MCP Server with Claude.

## Adding Knowledge

### Recording a Lesson Learned

When you discover something useful during development:

```
Please add this lesson to the knowledge base:
- Title: "SwiftUI NavigationStack Deep Linking"
- Content: "Use a NavigationPath binding to enable programmatic navigation and deep linking. Append values to navigate forward, remove to go back. Use .navigationDestination(for:) to handle each type."
- Category: pattern
- Technology: swift
- Tags: swiftui, navigation, deep-linking
```

### Recording a Gotcha

When you encounter a tricky issue:

```
Add a gotcha to hindsight:
- Title: "Core Data Background Context Crash"
- Content: "Never pass managed objects between contexts. Use objectID to fetch in the target context. Passing objects directly causes 'object belongs to a different context' crashes."
- Category: gotcha
- Technology: swift
- Tags: core-data, concurrency, crashes
```

### Recording an Error and Solution

When you solve an error:

```
Add this common error to hindsight:
- Technology: xcode
- Error pattern: "Command PhaseScriptExecution failed with a nonzero exit code"
- Root cause: "A build phase script is failing, often due to missing dependencies or incorrect paths"
- Solution: "Check the build log for the specific script error. Common fixes: ensure script has correct permissions (chmod +x), check paths are absolute not relative, verify required tools are installed"
- Code example: "chmod +x \"${SRCROOT}/Scripts/build-phase.sh\""
```

### Recording a Swift Pattern

When you develop a useful pattern:

```
Add this Swift pattern to hindsight:
- Pattern name: "Task-Based Debouncing"
- Description: "Debounce user input using structured concurrency without Combine"
- Code example:
  ```swift
  @MainActor
  class SearchViewModel: ObservableObject {
      private var searchTask: Task<Void, Never>?

      func search(_ query: String) {
          searchTask?.cancel()
          searchTask = Task {
              try? await Task.sleep(for: .milliseconds(300))
              guard !Task.isCancelled else { return }
              await performSearch(query)
          }
      }
  }
  ```
- When to use: "Text field search with network requests"
- When not to use: "Simple operations that don't need debouncing"
- Related APIs: Task, Task.sleep, structured concurrency
- iOS version: 15.0
- Swift version: 5.5
```

## Querying Knowledge

### General Search

```
Search hindsight for "memory management"
```

```
What do I have in hindsight about SwiftUI state?
```

### Filtered Search

```
Search hindsight for errors related to "signing" in xcode
```

```
Find swift patterns for iOS 17 or later
```

```
Show me all gotchas tagged with "concurrency"
```

### Finding Solutions

```
I'm getting "Publishing changes from background threads is not allowed" - check hindsight for solutions
```

```
Search errors in hindsight for "cannot convert value"
```

### Browsing

```
List all technologies in hindsight
```

```
Show me all tags in the knowledge base
```

```
Get hindsight statistics
```

## Session Management

### Recording a Session

At the end of a development session:

```
Add a session context to hindsight:
- Date: 2025-12-03
- Project: MyApp
- Summary: "Implemented user authentication with biometrics and keychain storage"
```

### Reviewing Recent Work

```
Export recent lessons from hindsight for swift
```

## Maintenance

### Track Error Frequency

When you encounter a known error again:

```
I hit that "database is locked" error again - increment its count in hindsight
```

### Update Existing Knowledge

```
Update lesson 15 in hindsight - change the content to include the new iOS 18 approach
```

### Export for Backup

```
Export all knowledge from hindsight as JSON
```

```
Export only swift patterns from hindsight
```

## Workflow Integration

### Start of Session

```
What patterns do I have in hindsight for the technology I'm working with today?
```

### During Development

When you hit an error:
```
Search hindsight for this error: [paste error message]
```

When you're about to implement something:
```
Do I have any patterns in hindsight for [feature you're implementing]?
```

### End of Session

```
Add these learnings from today's session to hindsight:

1. Lesson: [what you learned]
   Category: [pattern/practice/gotcha/decision]
   Technology: [tech]

2. Error: [error you encountered]
   Solution: [how you fixed it]
   Technology: [tech]
```

## Tips

### Effective Searching

- Use specific technical terms: "URLSession async" not just "networking"
- Combine with filters: technology, category, tags
- Start broad, then narrow down

### Good Knowledge Entries

- **Titles**: Short and searchable
- **Content**: Include context, not just the solution
- **Categories**: Choose accurately
  - `pattern` - Reusable code patterns
  - `practice` - Best practices and workflows
  - `gotcha` - Tricky issues and pitfalls
  - `decision` - Architectural decisions and rationale
- **Tags**: Use consistent naming (lowercase, hyphens)

### Building Your Knowledge Base

- Record learnings immediately while context is fresh
- Include error messages verbatim for better searchability
- Add code examples when relevant
- Link related entries through tags
- Review and update periodically
