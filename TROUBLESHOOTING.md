# Troubleshooting Guide

Common issues and solutions for the Hindsight MCP Server.

## Server Not Starting

### Tools not appearing in Claude Desktop

**Symptoms:** After configuring Claude Desktop, the Hindsight tools don't appear.

**Solutions:**

1. **Restart Claude Desktop** - Required after any config change
   ```bash
   # macOS
   pkill -f "Claude" && open -a "Claude"
   ```

2. **Check configuration path**
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Windows
   type %APPDATA%\Claude\claude_desktop_config.json
   ```

3. **Verify Python path is correct**
   ```bash
   # Should return Python version
   ~/.hindsight/.venv/bin/python --version
   ```

4. **Test server manually**
   ```bash
   ~/.hindsight/.venv/bin/python ~/.hindsight/server.py
   # Should start without errors (Ctrl+C to exit)
   ```

### "ModuleNotFoundError: No module named 'mcp'"

**Solution:** Install dependencies in the virtual environment:
```bash
source ~/.hindsight/.venv/bin/activate
pip install mcp python-dateutil
```

### "Permission denied" errors

**Solution:** Ensure files are executable:
```bash
chmod +x ~/.hindsight/server.py
chmod +x ~/.hindsight/backup.sh
```

## Database Issues

### "Database is locked"

**Symptoms:** Operations fail with "database is locked" error.

**Solutions:**

1. **Increase busy timeout** in `config.json`:
   ```json
   {
     "database": {
       "busy_timeout": 10000
     }
   }
   ```

2. **Close other connections** - Ensure no other process has the database open

3. **Check for stale lock files**:
   ```bash
   ls -la ~/.hindsight/knowledge.db*
   # Remove any .db-journal or .db-wal files if server isn't running
   ```

### "Database disk image is malformed"

**Solutions:**

1. **Try integrity check**:
   ```bash
   sqlite3 ~/.hindsight/knowledge.db "PRAGMA integrity_check;"
   ```

2. **Restore from backup**:
   ```bash
   # List available backups
   ls -lt ~/.hindsight/backups/

   # Restore (replace filename with actual backup)
   cp ~/.hindsight/backups/knowledge_20251203_030000.db ~/.hindsight/knowledge.db
   ```

3. **Rebuild from scratch**:
   ```bash
   rm ~/.hindsight/knowledge.db
   # Server will recreate on next start
   ```

### FTS search not returning expected results

**Symptoms:** Full-text search misses entries that should match.

**Solutions:**

1. **Rebuild FTS indexes**:
   ```bash
   sqlite3 ~/.hindsight/knowledge.db <<EOF
   INSERT INTO lessons_fts(lessons_fts) VALUES('rebuild');
   INSERT INTO errors_fts(errors_fts) VALUES('rebuild');
   INSERT INTO patterns_fts(patterns_fts) VALUES('rebuild');
   EOF
   ```

2. **Check FTS syntax** - Special characters need escaping:
   - Use `"quoted phrase"` for exact phrases
   - Avoid `.` and `-` in search terms (FTS5 operators)

## Connection Issues

### Server timing out

**Symptoms:** Operations take too long and fail.

**Solutions:**

1. **Increase timeouts** in `config.json`:
   ```json
   {
     "database": {
       "connection_timeout": 60,
       "busy_timeout": 10000
     }
   }
   ```

2. **Check database size**:
   ```bash
   ls -lh ~/.hindsight/knowledge.db
   # If over 100MB, consider archiving old entries
   ```

3. **Vacuum database**:
   ```bash
   sqlite3 ~/.hindsight/knowledge.db "VACUUM;"
   ```

## Logging and Debugging

### Enable debug logging

Set environment variable before starting Claude Desktop:
```bash
export HINDSIGHT_LOG_LEVEL=DEBUG
```

Or edit `config.json`:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### View logs

```bash
# Tail live logs
tail -f ~/.hindsight/logs/hindsight.log

# View recent errors
grep ERROR ~/.hindsight/logs/hindsight.log | tail -20
```

### Check server status

```bash
# Test database connection
sqlite3 ~/.hindsight/knowledge.db "SELECT COUNT(*) FROM lessons;"

# Test server import
~/.hindsight/.venv/bin/python -c "import sys; sys.path.insert(0, '$HOME/.hindsight'); from server import KnowledgeBaseServer; print('Import successful')"
```

## Backup Issues

### Backup script fails

**Solutions:**

1. **Check permissions**:
   ```bash
   chmod +x ~/.hindsight/backup.sh
   ```

2. **Create backup directory**:
   ```bash
   mkdir -p ~/.hindsight/backups
   ```

3. **Run manually to see errors**:
   ```bash
   ~/.hindsight/backup.sh
   ```

### Scheduled backups not running (macOS)

**Solutions:**

1. **Check launchd status**:
   ```bash
   ~/.hindsight/setup-backup-schedule.sh status
   launchctl list | grep hindsight
   ```

2. **View launchd errors**:
   ```bash
   cat ~/.hindsight/logs/backup-error.log
   ```

3. **Reinstall schedule**:
   ```bash
   ~/.hindsight/setup-backup-schedule.sh uninstall
   ~/.hindsight/setup-backup-schedule.sh install
   ```

## Performance Issues

### Slow queries

**Solutions:**

1. **Check query complexity** - Limit results:
   ```
   Search for "swift" with limit 10
   ```

2. **Use specific filters**:
   ```
   Search for "memory" in technology "swift" category "lesson"
   ```

3. **Rebuild FTS indexes** (see above)

4. **Analyze database**:
   ```bash
   sqlite3 ~/.hindsight/knowledge.db "ANALYZE;"
   ```

### High memory usage

**Solutions:**

1. **Limit result sizes** in queries

2. **Check database size** and archive old entries

3. **Restart Claude Desktop** to clear any caches

## Getting Help

If these solutions don't resolve your issue:

1. **Check logs** at `~/.hindsight/logs/hindsight.log`
2. **Search existing issues** on GitHub
3. **Open a new issue** with:
   - Error message
   - Steps to reproduce
   - Log output
   - Environment (OS, Python version)
