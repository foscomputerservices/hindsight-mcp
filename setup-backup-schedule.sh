#!/bin/bash
#
# Hindsight Backup Schedule Setup
# Installs or removes the daily backup schedule using launchd
#
# Usage: ./setup-backup-schedule.sh [install|uninstall|status]
#

set -e

HINDSIGHT_DIR="${HOME}/.hindsight"
PLIST_NAME="com.hindsight.backup"
PLIST_SRC="${HINDSIGHT_DIR}/${PLIST_NAME}.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"
LOGS_DIR="${HINDSIGHT_DIR}/logs"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

install_schedule() {
    log_info "Installing daily backup schedule..."

    # Create logs directory
    mkdir -p "$LOGS_DIR"

    # Copy plist to LaunchAgents
    if [[ ! -f "$PLIST_SRC" ]]; then
        log_error "Source plist not found: $PLIST_SRC"
        exit 1
    fi

    # Update plist with correct home directory
    sed "s|/Users/david|${HOME}|g" "$PLIST_SRC" > "$PLIST_DST"

    # Load the agent
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    launchctl load "$PLIST_DST"

    log_info "Backup schedule installed successfully"
    log_info "Backups will run daily at 3:00 AM"
    log_info "Logs: ${LOGS_DIR}/backup.log"
}

uninstall_schedule() {
    log_info "Removing backup schedule..."

    if [[ -f "$PLIST_DST" ]]; then
        launchctl unload "$PLIST_DST" 2>/dev/null || true
        rm -f "$PLIST_DST"
        log_info "Backup schedule removed"
    else
        log_warn "No backup schedule found"
    fi
}

show_status() {
    echo "Hindsight Backup Schedule Status"
    echo "================================="

    if [[ -f "$PLIST_DST" ]]; then
        log_info "Schedule installed: YES"
        launchctl list | grep "$PLIST_NAME" && log_info "Status: Running" || log_warn "Status: Not loaded"
    else
        log_warn "Schedule installed: NO"
    fi

    echo ""
    echo "Backup directory: ${HINDSIGHT_DIR}/backups"
    BACKUP_COUNT=$(ls -1 "${HINDSIGHT_DIR}/backups"/knowledge_*.db 2>/dev/null | wc -l | tr -d ' ')
    echo "Existing backups: ${BACKUP_COUNT}"

    if [[ $BACKUP_COUNT -gt 0 ]]; then
        echo ""
        echo "Most recent backups:"
        ls -lt "${HINDSIGHT_DIR}/backups"/knowledge_*.db 2>/dev/null | head -5 | while read -r line; do
            echo "  $line"
        done
    fi
}

# Main
case "${1:-status}" in
    install)
        install_schedule
        ;;
    uninstall)
        uninstall_schedule
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 [install|uninstall|status]"
        exit 1
        ;;
esac
