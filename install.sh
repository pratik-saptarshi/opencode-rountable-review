#!/usr/bin/env bash

set -e

TARGET=""
MODE="copy"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --target) TARGET="$2"; shift ;;
        --mode) MODE="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ -z "$TARGET" ]; then
    echo "Usage: $0 --target <directory> [--mode copy|symlink]"
    echo "Example: $0 --target ~/.config/opencode"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Evaluate target directory correctly
eval TARGET_DIR="$TARGET"
TARGET_DIR=$(realpath "$TARGET_DIR" 2>/dev/null || echo "$TARGET_DIR")

mkdir -p "$TARGET_DIR/skills/agent-review-panel"
mkdir -p "$TARGET_DIR/skills/plan-review-integrator"
mkdir -p "$TARGET_DIR/commands"

echo "Installing Agent Review Panel to $TARGET_DIR (Mode: $MODE)..."

if [ "$MODE" = "symlink" ]; then
    ln -sfn "$REPO_ROOT/skills/agent-review-panel/SKILL.md" "$TARGET_DIR/skills/agent-review-panel/SKILL.md"
    ln -sfn "$REPO_ROOT/skills/plan-review-integrator/SKILL.md" "$TARGET_DIR/skills/plan-review-integrator/SKILL.md"
    ln -sfn "$REPO_ROOT/commands/roundtable.md" "$TARGET_DIR/commands/roundtable.md"
    echo "✅ Symlinked Agent Review Panel to $TARGET_DIR"
else
    cp "$REPO_ROOT/skills/agent-review-panel/SKILL.md" "$TARGET_DIR/skills/agent-review-panel/"
    cp "$REPO_ROOT/skills/plan-review-integrator/SKILL.md" "$TARGET_DIR/skills/plan-review-integrator/"
    cp "$REPO_ROOT/commands/roundtable.md" "$TARGET_DIR/commands/"
    echo "✅ Copied Agent Review Panel to $TARGET_DIR"
fi

echo ""
echo "Next steps:"
echo "  Restart your OpenCode or agent tool session to load the /roundtable:agent-review-panel command."
