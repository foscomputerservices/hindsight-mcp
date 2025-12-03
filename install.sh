#!/bin/bash
# Hindsight MCP Server Installation Script
# Installs/updates runtime files to ~/.hindsight

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.hindsight"

echo "Installing Hindsight MCP Server..."
echo "  Source: $SCRIPT_DIR"
echo "  Target: $INSTALL_DIR"

# Create install directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/backups"

# Core server files (copy, not symlink, for stability)
echo "Copying server files..."
cp "$SCRIPT_DIR/server.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/schema.sql" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/backup.sh" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/setup-backup-schedule.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/backup.sh"
chmod +x "$INSTALL_DIR/setup-backup-schedule.sh"

# Config - only copy if doesn't exist (preserve local customizations)
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo "Creating default config..."
    cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/"
else
    echo "Keeping existing config.json (not overwritten)"
fi

# Set up Python virtual environment if needed
if [ ! -d "$INSTALL_DIR/.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$INSTALL_DIR/.venv"
fi

# Install/upgrade dependencies
echo "Installing Python dependencies..."
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet mcp pydantic

# Initialize database if needed
if [ ! -f "$INSTALL_DIR/knowledge.db" ]; then
    echo "Initializing database..."
    sqlite3 "$INSTALL_DIR/knowledge.db" < "$INSTALL_DIR/schema.sql"
    echo "Database created. You can load seed data with:"
    echo "  sqlite3 ~/.hindsight/knowledge.db < $SCRIPT_DIR/test-data.sql"
else
    echo "Database exists (not modified)"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Configure your MCP client (see README.md)"
echo "  2. Restart Claude Desktop or Claude Code"
echo ""
echo "Server location: $INSTALL_DIR/server.py"
echo "Python: $INSTALL_DIR/.venv/bin/python"
