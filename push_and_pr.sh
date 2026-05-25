#!/bin/bash
# ⚔️ opencode-roundtable-review — Push & Create Pull Request Utility
# This script pushes the quest/excalibur-node branch and creates a pull request.

set -e

BRANCH="quest/excalibur-node"
REPO="pratik-saptarshi/opencode-rountable-review"

echo "⚔️ Pushing feature branch to Camelot..."
git push origin "$BRANCH" --force-with-lease

echo "🛡️ Creating pull request on GitHub..."
gh pr create --repo "$REPO" \
    --head "$BRANCH" \
    --base "main" \
    --title "feat(excalibur-quest): migrate to universal cross-platform Node.js implementation" \
    --body "⚔️ **Excalibur Quest Remediation & Skill Integration Complete!**

This PR completes the migration of the \`excalibur-quest\` skill to a pure Node.js/JavaScript implementation, providing true cross-platform compatibility across Windows, macOS, and Linux without Python.

### 🛡️ Key Accomplishments
1. **Arthurian Core Skill:** Created \`SKILL.md\` under [SKILL.md](./skills/excalibur-quest/SKILL.md).
2. **Quest Helper Node CLI:** Built [quest_helper.js](./skills/excalibur-quest/scripts/quest_helper.js) utilizing zero-dependency standard Node modules.
3. **Roundtable Concurrency Seats:** Enforced a maximum of 3 concurrent instances globally via a file-locked execution queue.
4. **Resilient Local DB Engine:** Integrated transparent Dolt SQL primary engine with local JSON fallbacks for sandbox environments.
5. **Cleaned up Absolute Paths & Local Identifiers:** Sanitized all absolute paths, emails, and hostnames before public view.

This branch is clean, verified, and ready for review."
