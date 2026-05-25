---
name: excalibur-quest
description: >-
  Remediates repository bugs/issues using multi-phase Roundtable bead plans,
  atomic edits, and Camelot/GitHub issue synchronizations.
---

# Excalibur Quest

## Overview
The `excalibur-quest` skill orchestrates structural repository bug remediations.
It is modeled after King Arthur and the Knights of the Roundtable, utilizing a
bead-based quest planning methodology and robust local-first fallbacks.

## Dependencies
- `plan-review-integrator`: Merges review findings into Camelot plans.
- `overseer`: Conducts adversarial review panels before beginning quests.

## Quick Start
To remediate issue #123:
```bash
uv run python3 -m excalibur-quest.scripts.quest_helper init --issue-id 123 --reviews-path reviews.json
```

## Utility Scripts
The programmatic orchestration is driven by `quest_helper.py` which provides
the following subcommands:

### `init`
Initializes a remediation quest and creates a local bead database/git branch.
```bash
uv run python3 -m excalibur-quest.scripts.quest_helper init --issue-id 123 --reviews-path reviews.json --output quest_status.json
```

### `sync`
Synchronizes the status of the local beads and edits to origin GitHub issues.
```bash
uv run python3 -m excalibur-quest.scripts.quest_helper sync --issue-id 123 --repo-owner Cognilogical --repo-name NeuroStrata --output sync_status.json
```

### `close`
Closes the local beads and registers the successful completion of the quest.
```bash
uv run python3 -m excalibur-quest.scripts.quest_helper close --issue-id 123 --output final_status.json
```

## Rate Limiting
Enforces a maximum of 3 concurrent instances globally via a file-locked execution queue.

## Common Mistakes
1. **Skipping adversarial review panel**: Ensure `overseer` has reviewed the plan before calling `init`.
2. **Missing local database path**: Ensure appropriate workspace context when running.
