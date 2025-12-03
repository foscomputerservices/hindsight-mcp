-- Hindsight MCP Server - Test/Seed Data
-- This file contains sample data covering multiple technologies
-- Run with: sqlite3 knowledge.db < test-data.sql

-- ============================================
-- LESSONS (40 entries covering multiple technologies)
-- ============================================

-- Swift/iOS Lessons (15)
INSERT INTO lessons (title, content, category, technology, project_context) VALUES
('SwiftUI State Management', 'Use @State for local view state, @Binding for child views, @StateObject for owned ObservableObject, and @ObservedObject for passed-in ObservableObjects. Choose based on ownership semantics.', 'pattern', 'swift', 'iOS Development'),
('Async/Await Error Handling', 'Use do-catch with async/await. Always handle CancellationError separately. Use Task { } for fire-and-forget async work from sync contexts.', 'practice', 'swift', 'Networking'),
('@Observable vs ObservableObject', 'Use @Observable (iOS 17+) for simpler syntax and better performance. Falls back to ObservableObject for iOS 16 support. Observable tracks property access automatically.', 'decision', 'swift', 'SwiftUI Migration'),
('Memory Leak Prevention', 'Use [weak self] in closures that outlive the object. Check for retain cycles with Instruments > Leaks. Use unowned only when you are certain the reference will exist.', 'gotcha', 'swift', 'Performance'),
('Protocol-Oriented Design', 'Prefer protocols over class inheritance. Use protocol extensions for default implementations. Combine protocols for composition: SomeProtocol & AnotherProtocol.', 'pattern', 'swift', 'Architecture'),
('SwiftData Model Definition', 'Use @Model macro for SwiftData classes. Use @Attribute(.unique) for unique constraints. Use @Relationship for associations with delete rules.', 'pattern', 'swift', 'Data Persistence'),
('Actor Isolation Patterns', 'Use actors for thread-safe mutable state. Mark non-isolated functions with nonisolated. Use MainActor for UI updates from background tasks.', 'pattern', 'swift', 'Concurrency'),
('Combine vs AsyncSequence', 'Use AsyncSequence for simple streams. Use Combine for complex transformations, debouncing, and merging multiple publishers. Both can interoperate.', 'decision', 'swift', 'Reactive Programming'),
('View Modifier Best Practices', 'Create custom ViewModifiers for reusable styling. Chain modifiers in logical order: layout, appearance, interaction. Use .modifier() for conditional modifiers.', 'practice', 'swift', 'SwiftUI'),
('Dependency Injection in SwiftUI', 'Use @Environment for system values. Use .environment() for custom objects. Prefer EnvironmentObject over passing through many views.', 'pattern', 'swift', 'Architecture'),
('Structured Concurrency Tasks', 'Use TaskGroup for parallel work. Use withThrowingTaskGroup for error-prone operations. Cancel parent task to cancel children automatically.', 'pattern', 'swift', 'Concurrency'),
('Core Data to SwiftData Migration', 'Use NSManagedObject subclasses during migration. Map relationships carefully. Test with production-size datasets before shipping.', 'practice', 'swift', 'Data Migration'),
('App Intents for Shortcuts', 'Use @Parameter for intent inputs. Implement perform() for execution. Use IntentDialog for Siri responses. Test with Shortcuts app.', 'pattern', 'swift', 'System Integration'),
('Widget Timeline Optimization', 'Return future timeline entries to reduce refreshes. Use TimelineReloadPolicy.after() for time-sensitive data. Minimize network calls in timeline provider.', 'practice', 'swift', 'Widgets'),
('Navigation Stack Patterns', 'Use NavigationStack with path binding for programmatic navigation. Use NavigationLink(value:) for type-safe navigation. Handle deep links via path manipulation.', 'pattern', 'swift', 'Navigation');

-- Xcode Lessons (8)
INSERT INTO lessons (title, content, category, technology, project_context) VALUES
('Build Configuration Management', 'Use xcconfig files for build settings. Create Debug/Release/Staging configurations. Use User-Defined settings for custom values.', 'practice', 'xcode', 'CI/CD'),
('Scheme Organization', 'Create separate schemes for different build purposes. Use scheme environment variables for configuration. Archive only from Release scheme.', 'practice', 'xcode', 'Build System'),
('Xcode Cloud Setup', 'Configure ci_scripts for custom build steps. Use environment groups for secrets. Set up TestFlight deployment from main branch.', 'practice', 'xcode', 'Automation'),
('Debugging Memory Issues', 'Use Instruments > Allocations for memory tracking. Enable Zombie Objects to find use-after-free. Use Memory Graph Debugger for retain cycles.', 'practice', 'xcode', 'Debugging'),
('Asset Catalog Best Practices', 'Use app thinning for multiple device sizes. Organize assets by feature. Use named colors for consistent theming.', 'practice', 'xcode', 'Resources'),
('Swift Package Dependencies', 'Use exact version for stability. Use branch for development dependencies. Resolve conflicts by checking Package.resolved.', 'practice', 'xcode', 'Dependencies'),
('Previews Not Loading Fix', 'Clean build folder if previews fail. Check for runtime crashes in preview code. Use #Preview with explicit device selection.', 'gotcha', 'xcode', 'SwiftUI Development'),
('Code Signing Troubleshooting', 'Let Xcode manage signing for most cases. Use manual signing for enterprise distribution. Check provisioning profile expiration dates.', 'gotcha', 'xcode', 'Distribution');

-- Bitbucket/Git Lessons (8)
INSERT INTO lessons (title, content, category, technology, project_context) VALUES
('Pipeline Cache Optimization', 'Cache derived data and SPM packages. Use caches with keys based on resolved package files. Clear cache when dependencies update.', 'practice', 'bitbucket', 'CI/CD'),
('Branch Protection Rules', 'Require pull request reviews for main branch. Enable status checks for required pipelines. Prevent force push to protected branches.', 'practice', 'bitbucket', 'Repository Management'),
('Pipeline Parallel Steps', 'Use parallel steps for independent jobs. Limit parallelism based on agent availability. Share artifacts between parallel steps.', 'pattern', 'bitbucket', 'CI/CD'),
('Git Hooks for Quality', 'Use pre-commit for linting and formatting. Use commit-msg for conventional commits. Store hooks in repository with setup script.', 'practice', 'git', 'Code Quality'),
('Monorepo Pipeline Strategy', 'Use conditions to run only affected components. Cache each component separately. Use deployment triggers per component.', 'decision', 'bitbucket', 'Repository Structure'),
('Pull Request Templates', 'Create PULL_REQUEST_TEMPLATE.md for consistent PR descriptions. Include testing checklist. Add reviewer assignment suggestions.', 'practice', 'bitbucket', 'Collaboration'),
('Git LFS for Large Files', 'Use LFS for binary assets over 100KB. Configure .gitattributes for file patterns. Ensure CI has LFS credentials.', 'practice', 'git', 'Repository Management'),
('Rebase vs Merge Strategy', 'Use rebase for feature branches to keep history clean. Use merge commits for main to preserve context. Avoid rebasing shared branches.', 'decision', 'git', 'Workflow');

-- Python Lessons (5)
INSERT INTO lessons (title, content, category, technology, project_context) VALUES
('Virtual Environment Best Practices', 'Create venv per project. Use requirements.txt or pyproject.toml for dependencies. Add .venv to .gitignore.', 'practice', 'python', 'Project Setup'),
('Type Hints for Documentation', 'Use type hints for function signatures. Use Optional for nullable types. Run mypy for static type checking.', 'practice', 'python', 'Code Quality'),
('Async with aiohttp', 'Use aiohttp for async HTTP requests. Create ClientSession once and reuse. Use asyncio.gather for parallel requests.', 'pattern', 'python', 'Networking'),
('Pytest Fixtures and Mocking', 'Use fixtures for test setup. Use pytest-mock for mocking. Use conftest.py for shared fixtures.', 'practice', 'python', 'Testing'),
('FastAPI Best Practices', 'Use Pydantic models for request/response. Use dependency injection for shared resources. Use BackgroundTasks for async work.', 'practice', 'python', 'API Development');

-- General/Cross-Platform Lessons (4)
INSERT INTO lessons (title, content, category, technology, project_context) VALUES
('API Error Response Design', 'Return consistent error format with code, message, and details. Use HTTP status codes correctly. Include request ID for debugging.', 'pattern', 'api', 'API Design'),
('Database Migration Strategy', 'Always create reversible migrations. Test migrations on copy of production data. Run migrations separately from deployments.', 'practice', 'database', 'Data Management'),
('Logging Best Practices', 'Log at appropriate levels: DEBUG for development, INFO for operations, ERROR for failures. Include context like request IDs. Rotate logs to prevent disk fill.', 'practice', 'general', 'Operations'),
('Documentation as Code', 'Keep docs in repository with code. Use markdown for portability. Update docs in same PR as code changes.', 'practice', 'general', 'Documentation');

-- ============================================
-- COMMON ERRORS (25 entries)
-- ============================================

-- Swift Errors (12)
INSERT INTO common_errors (technology, error_pattern, root_cause, solution, code_example) VALUES
('swift', 'Cannot convert value of type ''String'' to expected argument type ''Int''', 'Type mismatch in function call', 'Use Int(string) or pass the correct type. Check if the API changed.', 'let value = Int(stringValue) ?? 0'),
('swift', 'Type ''X'' does not conform to protocol ''Codable''', 'Missing Codable conformance on a nested type', 'Ensure all properties of the type conform to Codable. Use custom encode/decode for non-Codable types.', 'struct MyType: Codable { let nested: NestedCodable }'),
('swift', 'Actor-isolated property cannot be referenced from a non-isolated context', 'Accessing actor state from outside the actor', 'Use await when accessing actor properties or mark the calling function with the same actor.', 'await myActor.someProperty'),
('swift', 'Task-isolated value of type ''X'' passed as a strongly transferred parameter', 'Passing non-Sendable type across task boundary', 'Make the type Sendable or use @unchecked Sendable carefully. Prefer restructuring to avoid passing mutable state.', '@unchecked Sendable or copy the data'),
('swift', 'Reference to captured var ''self'' in concurrently-executing code', 'Using self in async context that requires Sendable', 'Capture self explicitly with [self] or use Task { @MainActor in }.', 'Task { [self] in await self.doWork() }'),
('swift', 'Publishing changes from background threads is not allowed', 'Updating ObservableObject from non-main thread', 'Use MainActor.run or @MainActor annotation on the property or function.', '@MainActor func updateUI() { state = newValue }'),
('swift', 'Cannot find ''X'' in scope', 'Missing import, typo, or scope issue', 'Check imports at file top. Verify spelling. Check if type is internal to another module.', 'import MyFramework'),
('swift', 'Modifying state during view update', 'Changing @State during body computation', 'Move state changes to onAppear, task, or action handlers. Never modify state directly in body.', 'onAppear { state = newValue }'),
('swift', 'Expression too complex to solve in reasonable time', 'Type checker struggling with complex expression', 'Break expression into smaller parts with explicit type annotations. Use intermediate variables.', 'let intermediate: Int = a + b; let result = intermediate * c'),
('swift', 'Ambiguous use of ''X''', 'Multiple matches for function or property name', 'Add explicit type annotation or use full module path to disambiguate.', 'let x: ModuleA.TypeName = ...'),
('swift', 'Failed to produce diagnostic for expression', 'Compiler bug or extremely complex type inference', 'Simplify the expression. Add explicit type annotations. Try breaking into multiple statements.', 'Split complex closures into named functions'),
('swift', 'Result of call is unused', 'Ignoring return value of non-Void function', 'Assign to _ if intentionally ignoring. Use @discardableResult on function if return is optional.', '_ = functionWithReturn()');

-- Xcode Errors (8)
INSERT INTO common_errors (technology, error_pattern, root_cause, solution, code_example) VALUES
('xcode', 'Signing requires a development team', 'No team selected in Signing & Capabilities', 'Select your team in project settings > Signing & Capabilities. Use automatic signing for personal development.', NULL),
('xcode', 'The sandbox is not in sync with the Podfile.lock', 'CocoaPods dependency mismatch', 'Run pod install. Delete Pods directory if persists. Check Podfile.lock is committed.', 'pod install --repo-update'),
('xcode', 'Command PhaseScriptExecution failed with a nonzero exit code', 'Build phase script error', 'Check script in Build Phases. Look at build log for specific error. Ensure script has correct permissions.', 'chmod +x script.sh'),
('xcode', 'Library not loaded: @rpath/Framework.framework', 'Framework not embedded correctly', 'Add framework to Embed Frameworks build phase. Check Runpath Search Paths.', 'Add to Embed Frameworks phase'),
('xcode', 'Unable to install "App"', 'Device trust or provisioning issue', 'Trust developer certificate on device. Check provisioning profile includes device UDID.', 'Settings > General > Device Management > Trust'),
('xcode', 'error: Multiple commands produce', 'Duplicate output files in build', 'Remove duplicate file references. Check Copy Bundle Resources for duplicates.', 'Remove from one target'),
('xcode', 'Preview crashed', 'Runtime error in preview code', 'Check for force unwraps and missing preview data. Use try? in preview context. Check Diagnostics window.', '#Preview { ContentView() }'),
('xcode', 'Could not resolve package dependencies', 'SPM version conflicts', 'Delete Package.resolved and retry. Check version requirements are compatible. Use exact versions to debug.', 'File > Packages > Reset Package Caches');

-- Bitbucket/Git Errors (5)
INSERT INTO common_errors (technology, error_pattern, root_cause, solution, code_example) VALUES
('bitbucket', 'Pipeline failed: Docker pull rate limit exceeded', 'Docker Hub rate limiting', 'Use authenticated Docker pulls. Mirror images to private registry. Cache Docker images.', 'docker login before pull'),
('bitbucket', 'Pipeline: Out of memory', 'Build step using too much memory', 'Increase memory size in pipeline. Split large steps. Use swap if available.', 'size: 2x in pipeline config'),
('git', 'Your local changes would be overwritten by merge', 'Uncommitted changes conflict with merge', 'Stash changes, merge, then pop stash. Or commit changes first.', 'git stash && git merge && git stash pop'),
('git', 'fatal: refusing to merge unrelated histories', 'Merging repositories with no common ancestor', 'Use --allow-unrelated-histories flag. Only use when intentionally combining repos.', 'git merge branch --allow-unrelated-histories'),
('git', 'error: failed to push some refs', 'Remote has changes not in local', 'Pull with rebase first, then push. Resolve conflicts if any.', 'git pull --rebase && git push');

-- ============================================
-- SWIFT PATTERNS (15 entries)
-- ============================================

INSERT INTO swift_patterns (pattern_name, description, code_example, when_to_use, when_not_to_use, related_apis, ios_version, swift_version) VALUES
('Result Type Error Handling', 'Use Result type for async operations that can fail, especially in completion handlers.',
'func fetchData(completion: @escaping (Result<Data, Error>) -> Void) {
    URLSession.shared.dataTask(with: url) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }
        completion(.success(data!))
    }.resume()
}',
'When you need explicit error handling without throwing', 'Simple operations where try/catch is cleaner', '["Result", "URLSession"]', '13.0', '5.0'),

('Observable Macro Pattern', 'Use @Observable for simpler and more efficient state observation in SwiftUI.',
'@Observable
class UserSettings {
    var username: String = ""
    var isLoggedIn: Bool = false

    func login(as user: String) {
        username = user
        isLoggedIn = true
    }
}',
'New projects targeting iOS 17+', 'When supporting iOS 16 or earlier', '["Observable", "Observation"]', '17.0', '5.9'),

('Actor-Based Cache', 'Thread-safe caching using actors.',
'actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) -> UIImage? {
        cache[url]
    }

    func store(_ image: UIImage, for url: URL) {
        cache[url] = image
    }
}',
'Shared mutable state accessed from multiple tasks', 'Simple single-threaded scenarios', '["actor", "isolation"]', '15.0', '5.5'),

('Dependency Injection Container', 'Lightweight DI container using property wrappers.',
'@propertyWrapper
struct Injected<T> {
    var wrappedValue: T {
        Container.shared.resolve(T.self)
    }
}

class Container {
    static let shared = Container()
    private var factories: [ObjectIdentifier: Any] = [:]

    func register<T>(_ factory: @escaping () -> T) {
        factories[ObjectIdentifier(T.self)] = factory
    }

    func resolve<T>(_ type: T.Type) -> T {
        (factories[ObjectIdentifier(T.self)] as! () -> T)()
    }
}',
'Apps with testability requirements', 'Simple apps with few dependencies', '["PropertyWrapper"]', '13.0', '5.1'),

('Coordinator Navigation', 'Coordinator pattern for decoupled navigation.',
'protocol Coordinator: AnyObject {
    var childCoordinators: [Coordinator] { get set }
    func start()
}

class AppCoordinator: Coordinator {
    var childCoordinators: [Coordinator] = []
    private let navigationController: UINavigationController

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func start() {
        let homeVC = HomeViewController()
        homeVC.coordinator = self
        navigationController.pushViewController(homeVC, animated: false)
    }
}',
'Complex apps with multiple navigation flows', 'Simple single-screen apps', '["UINavigationController"]', '13.0', '5.0'),

('Type-Safe UserDefaults', 'Property wrapper for type-safe UserDefaults access.',
'@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T
    let container: UserDefaults = .standard

    var wrappedValue: T {
        get { container.object(forKey: key) as? T ?? defaultValue }
        set { container.set(newValue, forKey: key) }
    }
}

struct Preferences {
    @UserDefault(key: "hasOnboarded", defaultValue: false)
    static var hasOnboarded: Bool
}',
'Accessing UserDefaults throughout app', 'Complex data that should use SwiftData', '["UserDefaults", "PropertyWrapper"]', '13.0', '5.1'),

('Async Stream Publisher', 'Bridge between Combine and async/await.',
'extension Publisher {
    var values: AsyncThrowingStream<Output, Error> {
        AsyncThrowingStream { continuation in
            let cancellable = self.sink(
                receiveCompletion: { completion in
                    switch completion {
                    case .finished: continuation.finish()
                    case .failure(let error): continuation.finish(throwing: error)
                    }
                },
                receiveValue: { value in
                    continuation.yield(value)
                }
            )
            continuation.onTermination = { _ in cancellable.cancel() }
        }
    }
}',
'Consuming Combine publishers in async contexts', 'Pure async/await code without Combine', '["AsyncThrowingStream", "Publisher", "Combine"]', '15.0', '5.5'),

('View Modifier Factory', 'Reusable view modifiers with factory pattern.',
'struct CardStyle: ViewModifier {
    let cornerRadius: CGFloat
    let shadowRadius: CGFloat

    func body(content: Content) -> some View {
        content
            .background(Color(.systemBackground))
            .cornerRadius(cornerRadius)
            .shadow(radius: shadowRadius)
    }
}

extension View {
    func cardStyle(cornerRadius: CGFloat = 12, shadowRadius: CGFloat = 4) -> some View {
        modifier(CardStyle(cornerRadius: cornerRadius, shadowRadius: shadowRadius))
    }
}',
'Consistent styling across views', 'One-off styling needs', '["ViewModifier", "View"]', '13.0', '5.1'),

('Environment Key Pattern', 'Custom environment values for SwiftUI.',
'private struct ThemeKey: EnvironmentKey {
    static let defaultValue: Theme = .light
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

extension View {
    func theme(_ theme: Theme) -> some View {
        environment(\\.theme, theme)
    }
}',
'Passing values through view hierarchy', 'Local state that doesnt need propagation', '["EnvironmentKey", "EnvironmentValues"]', '13.0', '5.1'),

('Repository Pattern', 'Abstract data access with repository.',
'protocol UserRepository {
    func fetch(id: String) async throws -> User
    func save(_ user: User) async throws
}

class RemoteUserRepository: UserRepository {
    private let api: APIClient

    func fetch(id: String) async throws -> User {
        try await api.get("/users/\\(id)")
    }

    func save(_ user: User) async throws {
        try await api.post("/users", body: user)
    }
}',
'Clean separation of data access', 'Simple apps with single data source', '["Protocol", "async/await"]', '15.0', '5.5'),

('SwiftData Query Wrapper', 'Reusable query configurations for SwiftData.',
'extension Query {
    static func recentItems(limit: Int = 10) -> Query<[Item], [Item]> {
        Query(
            filter: #Predicate { !$0.isArchived },
            sort: \\.createdAt,
            order: .reverse
        )
    }
}

struct RecentItemsView: View {
    @Query(Item.recentItems()) var items: [Item]

    var body: some View {
        List(items) { item in ItemRow(item: item) }
    }
}',
'Reusable queries across views', 'Simple one-off queries', '["Query", "SwiftData", "Predicate"]', '17.0', '5.9'),

('Task Modifier Pattern', 'Structured task management in SwiftUI.',
'struct AsyncContent<T, Content: View>: View {
    let load: () async throws -> T
    @ViewBuilder let content: (T) -> Content

    @State private var result: Result<T, Error>?

    var body: some View {
        Group {
            switch result {
            case .none: ProgressView()
            case .success(let value): content(value)
            case .failure(let error): Text(error.localizedDescription)
            }
        }
        .task {
            result = await Result { try await load() }
        }
    }
}',
'Loading async data in views', 'Complex loading states with retry', '["task", "Result"]', '15.0', '5.5'),

('Sendable View Model', 'Making view models sendable for actor isolation.',
'@MainActor
final class SettingsViewModel: ObservableObject {
    @Published private(set) var settings: Settings

    nonisolated init() {
        // Use default settings
    }

    func loadSettings() async {
        settings = await SettingsService.shared.load()
    }
}',
'View models used with actors', 'Simple models without async requirements', '["MainActor", "Sendable", "ObservableObject"]', '15.0', '5.5'),

('Preview Provider Extensions', 'Reusable preview configurations.',
'extension PreviewDevice {
    static let iPhone15Pro = PreviewDevice("iPhone 15 Pro")
    static let iPadPro = PreviewDevice("iPad Pro (12.9-inch)")
}

extension View {
    func previewAllDevices() -> some View {
        Group {
            self.previewDevice(.iPhone15Pro)
                .previewDisplayName("iPhone")
            self.previewDevice(.iPadPro)
                .previewDisplayName("iPad")
        }
    }
}',
'Consistent preview configurations', 'Single device previews', '["PreviewDevice", "PreviewProvider"]', '13.0', '5.1'),

('Feature Flag System', 'Runtime feature toggles for gradual rollout.',
'actor FeatureFlags {
    static let shared = FeatureFlags()

    private var flags: [String: Bool] = [:]

    func isEnabled(_ flag: String) -> Bool {
        flags[flag] ?? false
    }

    func set(_ flag: String, enabled: Bool) {
        flags[flag] = enabled
    }

    func load(from config: RemoteConfig) async {
        flags = await config.fetchFlags()
    }
}

// Usage
if await FeatureFlags.shared.isEnabled("newCheckout") {
    // Show new checkout
}',
'Gradual feature rollout', 'Features that dont need runtime toggling', '["actor", "async/await"]', '15.0', '5.5');

-- ============================================
-- TAGS (for lesson tagging)
-- ============================================

INSERT INTO tags (name) VALUES
('swiftui'), ('concurrency'), ('networking'), ('architecture'), ('testing'),
('performance'), ('debugging'), ('ci-cd'), ('git'), ('best-practices'),
('error-handling'), ('data-persistence'), ('navigation'), ('security'), ('accessibility');

-- ============================================
-- LESSON TAGS (associate lessons with tags)
-- ============================================

-- SwiftUI lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 1, id FROM tags WHERE name = 'swiftui';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 1, id FROM tags WHERE name = 'architecture';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 9, id FROM tags WHERE name = 'swiftui';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 10, id FROM tags WHERE name = 'swiftui';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 10, id FROM tags WHERE name = 'architecture';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 15, id FROM tags WHERE name = 'swiftui';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 15, id FROM tags WHERE name = 'navigation';

-- Concurrency lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 2, id FROM tags WHERE name = 'concurrency';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 2, id FROM tags WHERE name = 'error-handling';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 7, id FROM tags WHERE name = 'concurrency';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 8, id FROM tags WHERE name = 'concurrency';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 11, id FROM tags WHERE name = 'concurrency';

-- Architecture lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 5, id FROM tags WHERE name = 'architecture';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 5, id FROM tags WHERE name = 'best-practices';

-- Data lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 6, id FROM tags WHERE name = 'data-persistence';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 12, id FROM tags WHERE name = 'data-persistence';

-- Performance lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 4, id FROM tags WHERE name = 'performance';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 4, id FROM tags WHERE name = 'debugging';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 14, id FROM tags WHERE name = 'performance';

-- CI/CD lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 16, id FROM tags WHERE name = 'ci-cd';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 18, id FROM tags WHERE name = 'ci-cd';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 24, id FROM tags WHERE name = 'ci-cd';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 26, id FROM tags WHERE name = 'ci-cd';

-- Git lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 27, id FROM tags WHERE name = 'git';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 28, id FROM tags WHERE name = 'git';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 30, id FROM tags WHERE name = 'git';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 31, id FROM tags WHERE name = 'git';

-- Testing lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 37, id FROM tags WHERE name = 'testing';

-- Debugging lessons
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 19, id FROM tags WHERE name = 'debugging';
INSERT INTO lesson_tags (lesson_id, tag_id) SELECT 22, id FROM tags WHERE name = 'debugging';

-- ============================================
-- SESSIONS (sample session entries)
-- ============================================

INSERT INTO sessions (date, project_name, session_log_path, summary) VALUES
('2025-12-01', 'iOS App', '~/.claude/sessions/2025-12-01-ios-app.md', 'Implemented SwiftUI navigation and fixed memory leaks'),
('2025-12-02', 'Backend API', '~/.claude/sessions/2025-12-02-backend.md', 'Added Python FastAPI endpoints and tests'),
('2025-12-03', 'Hindsight MCP', '~/.claude/sessions/2025-12-03-hindsight.md', 'Phase 6 testing and seed data implementation');
