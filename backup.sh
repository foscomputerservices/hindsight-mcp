#!/bin/bash
#
# Hindsight Knowledge Base Backup Script
# Creates timestamped backups with automatic rotation (keeps last 30)
#
# Usage: ./backup.sh [backup_dir]
# Default backup_dir: ~/.hindsight/backups
#

set -e

# Configuration
HINDSIGHT_DIR="${HOME}/.hindsight"
DB_PATH="${HINDSIGHT_DIR}/knowledge.db"
DEFAULT_BACKUP_DIR="${HINDSIGHT_DIR}/backups"
MAX_BACKUPS=30

# Use provided backup dir or default
BACKUP_DIR="${1:-$DEFAULT_BACKUP_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Check if database exists
if [[ ! -f "$DB_PATH" ]]; then
    log_error "Database not found at ${DB_PATH}"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/knowledge_${TIMESTAMP}.db"

# Check database integrity before backup
log_info "Checking database integrity..."
INTEGRITY_CHECK=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>&1)
if [[ "$INTEGRITY_CHECK" != "ok" ]]; then
    log_error "Database integrity check failed: ${INTEGRITY_CHECK}"
    exit 1
fi

# Create backup using SQLite's .backup command for consistency
log_info "Creating backup at ${BACKUP_FILE}..."
sqlite3 "$DB_PATH" ".backup '${BACKUP_FILE}'"

if [[ -f "$BACKUP_FILE" ]]; then
    # Get file sizes for comparison
    ORIGINAL_SIZE=$(stat -f%z "$DB_PATH" 2>/dev/null || stat -c%s "$DB_PATH")
    BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE")

    log_info "Backup created successfully"
    log_info "  Original: $(numfmt --to=iec-i --suffix=B $ORIGINAL_SIZE 2>/dev/null || echo "${ORIGINAL_SIZE} bytes")"
    log_info "  Backup:   $(numfmt --to=iec-i --suffix=B $BACKUP_SIZE 2>/dev/null || echo "${BACKUP_SIZE} bytes")"
else
    log_error "Backup file was not created"
    exit 1
fi

# Rotate old backups (keep only MAX_BACKUPS most recent)
log_info "Rotating old backups (keeping last ${MAX_BACKUPS})..."
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/knowledge_*.db 2>/dev/null | wc -l | tr -d ' ')

if [[ $BACKUP_COUNT -gt $MAX_BACKUPS ]]; then
    # Get list of oldest backups to remove
    REMOVE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))

    ls -1t "${BACKUP_DIR}"/knowledge_*.db | tail -n $REMOVE_COUNT | while read -r OLD_BACKUP; do
        log_info "  Removing old backup: $(basename "$OLD_BACKUP")"
        rm -f "$OLD_BACKUP"
    done

    log_info "Removed ${REMOVE_COUNT} old backup(s)"
else
    log_info "No rotation needed (${BACKUP_COUNT}/${MAX_BACKUPS} backups)"
fi

# Summary
CURRENT_BACKUPS=$(ls -1 "${BACKUP_DIR}"/knowledge_*.db 2>/dev/null | wc -l | tr -d ' ')
log_info "Backup complete. Total backups: ${CURRENT_BACKUPS}"
