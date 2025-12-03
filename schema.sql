-- Hindsight MCP Server - Database Schema
-- Copyright (c) 2025 FOS Computer Services, LLC
-- Licensed under the MIT License

-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('pattern', 'practice', 'gotcha', 'decision')),
    technology TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_context TEXT,
    source_session TEXT
);

-- Full-text search for lessons
CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
    title, content, technology,
    content='lessons',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS lessons_ai AFTER INSERT ON lessons BEGIN
    INSERT INTO lessons_fts(rowid, title, content, technology)
    VALUES (new.id, new.title, new.content, new.technology);
END;

CREATE TRIGGER IF NOT EXISTS lessons_ad AFTER DELETE ON lessons BEGIN
    DELETE FROM lessons_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS lessons_au AFTER UPDATE ON lessons BEGIN
    UPDATE lessons_fts SET title = new.title, content = new.content,
                          technology = new.technology WHERE rowid = new.id;
END;

-- Update timestamp trigger
CREATE TRIGGER IF NOT EXISTS lessons_update_timestamp
AFTER UPDATE ON lessons
BEGIN
    UPDATE lessons SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS lesson_tags (
    lesson_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (lesson_id, tag_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lesson_tags_lesson ON lesson_tags(lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_tags_tag ON lesson_tags(tag_id);

-- Common Errors
CREATE TABLE IF NOT EXISTS common_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technology TEXT NOT NULL,
    error_pattern TEXT NOT NULL,
    root_cause TEXT,
    solution TEXT NOT NULL,
    code_example TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1
);

CREATE VIRTUAL TABLE IF NOT EXISTS errors_fts USING fts5(
    technology, error_pattern, root_cause, solution,
    content='common_errors',
    content_rowid='id'
);

-- Triggers for errors FTS
CREATE TRIGGER IF NOT EXISTS errors_ai AFTER INSERT ON common_errors BEGIN
    INSERT INTO errors_fts(rowid, technology, error_pattern, root_cause, solution)
    VALUES (new.id, new.technology, new.error_pattern, new.root_cause, new.solution);
END;

CREATE TRIGGER IF NOT EXISTS errors_ad AFTER DELETE ON common_errors BEGIN
    DELETE FROM errors_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS errors_au AFTER UPDATE ON common_errors BEGIN
    UPDATE errors_fts SET technology = new.technology, error_pattern = new.error_pattern,
                         root_cause = new.root_cause, solution = new.solution
    WHERE rowid = new.id;
END;

-- Swift Patterns
CREATE TABLE IF NOT EXISTS swift_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    description TEXT NOT NULL,
    code_example TEXT NOT NULL,
    when_to_use TEXT,
    when_not_to_use TEXT,
    related_apis TEXT,
    ios_version TEXT,
    swift_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
    pattern_name, description, when_to_use,
    content='swift_patterns',
    content_rowid='id'
);

-- Triggers for patterns FTS
CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON swift_patterns BEGIN
    INSERT INTO patterns_fts(rowid, pattern_name, description, when_to_use)
    VALUES (new.id, new.pattern_name, new.description, new.when_to_use);
END;

CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON swift_patterns BEGIN
    DELETE FROM patterns_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON swift_patterns BEGIN
    UPDATE patterns_fts SET pattern_name = new.pattern_name,
                           description = new.description,
                           when_to_use = new.when_to_use
    WHERE rowid = new.id;
END;

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    project_name TEXT,
    session_log_path TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_name);
