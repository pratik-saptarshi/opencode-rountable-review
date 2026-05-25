#!/bin/bash
# ⚔️ opencode-roundtable-review — Push & Create Pull Request Utility
# This script pushes the quest/excalibur-skill branch and creates a pull request.

set -e

BRANCH="quest/excalibur-skill"
REPO="pratik-saptarshi/opencode-rountable-review"

echo "⚔️ Pushing feature branch to Camelot..."
git push origin "$BRANCH" --force-with-lease

echo "🛡️ Creating pull request on GitHub..."
gh pr create --repo "$REPO" \
    --head "$BRANCH" \
    --base "master" \
    --title "feat(excalibur-quest): integrate arthurian quest-based remediation skill" \
    --body "⚔️ **Excalibur Quest Remediation & Skill Integration Complete!**

This PR integrates the \`excalibur-quest\` skill, modeled after King Arthur and the Knights of the Roundtable, providing a robust bead-based remediation quest planning and local-first fallback mechanism.

### 🛡️ Key Accomplishments
1. **Arthurian Core Skill:** Created \`SKILL.md\` under [SKILL.md](./skills/excalibur-quest/SKILL.md).
2. **Quest Helper CLI:** Built [quest_helper.py](./skills/excalibur-quest/scripts/quest_helper.py) utilizing standard Python libraries.
3. **Roundtable Concurrency Seats:** Enforced a maximum of 3 concurrent instances globally via a file-locked execution queue.
4. **Resilient Local DB Engine:** Integrated transparent Dolt SQL primary engine with local JSON fallbacks for sandbox environments.
5. **Cleaned up Absolute Paths & Local Identifiers:** Sanitized all absolute paths, emails, and hostnames before public view.

This branch is clean, verified, and ready for review."
