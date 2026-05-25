# excalibur-quest Design Plan

Designing the `excalibur-quest` skill to orchestrate multi-agent review remediation, bead tracking, atomic editing, and GitHub/Dolt issue syncing under Arthurian theme.

## 1. Skill Details
- **Name:** `excalibur-quest`
- **Description:** Remediates complex repository bugs/issues using multi-phase Roundtable bead plans, atomic edits, and Camelot/GitHub issue synchronizations.

## 2. Directory Structure
```
skills/excalibur-quest/
├── SKILL.md
├── scripts/
│   └── quest_helper.py
└── references/
    └── arthurian_bead_notes.md
```

## 3. Existing Skills Referenced
- `plan-review-integrator`: For merging multi-agent findings into structured plans.
- `overseer`: For running adversarial review panels on proposed designs.

## 4. Helper Script (`quest_helper.py`)
- **Subcommands:**
  1. `init`: Initialize Arthurian bead quest database (local Dolt db or fallback git tracker).
     - Arguments: `--issue-id`, `--reviews-path`, `--output`
  2. `sync`: Push findings/remediations/bead updates to GitHub issues.
     - Arguments: `--issue-id`, `--repo-owner`, `--repo-name`, `--output`
  3. `close`: Complete beads and finalize the quest.
     - Arguments: `--issue-id`, `--output`

## 5. Rate Limiting Strategy
- File-lock–based lock to restrict execution to maximum 3 concurrent runs.
- Sequential execution queue for remaining runs.

## 6. Error Handling Strategy
- Primary API fails (GitHub/Dolt) → Auto-fallback (local DB/git branch tracker).
- Fallback fails → Ask user for guidance.
- Complete breakdown → Fail loudly.
- Surface all edge cases, code gaps, and security risks.
