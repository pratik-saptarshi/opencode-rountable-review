# Arthurian Bead Quest Reference

In the `excalibur-quest` system, every bug remediation is handled as a quest of the Roundtable.

## 1. Quest Structure
- **Quest**: The overall issue or task to remediate (e.g. Issue #123).
- **Bead**: An atomic step/remediation phase (e.g. `bead-1`, `bead-2`). Each bead has:
  - **ID**: `bead-N`
  - **Title**: Action description
  - **Severity**: CRITICAL, HIGH, MEDIUM, LOW
  - **Status**: PENDING, ACTIVE, COMPLETED

## 2. Concurrency Slots
Maximum 3 concurrent instances are allowed at any time. When a Knight initiates a quest, they take a seat at the Roundtable. If all 3 seats are full, they queue sequentially.

## 3. Databases and Local Fallbacks
- Primary: Dolt SQL database (`quests` table).
- Fallback: Local git directory JSON database (`.excalibur_quest/quest_db.json`).
- If GitHub API is sandboxed or unavailable, local status is synced to Git branch details.
