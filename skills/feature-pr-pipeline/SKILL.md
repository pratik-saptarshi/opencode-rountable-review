---
name: feature-pr-pipeline
version: 1.0.0
author: pratik-saptarshi
description: >
  Standardized feature-to-PR workflow — plan, implement with subagent-driven
  TDD, independent whole-branch review, hygiene pass, then PR with CI and
  review-comment gating. Use when the user asks for the standard workflow,
  says "make this the standard process", or requests a multi-step feature,
  fix, or docs change that will end as a pull request.
---

# Feature-to-PR Pipeline

**Announce at start:** "I'm using the feature-pr-pipeline skill for this feature-to-PR run."

## When to Use

Use for any multi-step feature, fix, or docs change that will end as a pull request: plan → implement → review → hygiene → PR → CI gate.

Do NOT use for: one-line fixes (do them directly), exploratory spikes (no PR planned), or work the user asked to keep local-only.

**Authorization (read once):** pushing a branch, opening a PR, and merging each require the user's explicit per-action authorization naming the exact branch/PR. Never bundle merge permission into a general "proceed". Branch deletion, force-push, and history rewrite need separate explicit per-action approval naming exact targets.

## Prerequisites

This skill orchestrates five companion workflow skills. At Stage 0, confirm each is installed (or that you know its procedure):
- `writing-plans` — implementation plans with task-level tests
- `subagent-driven-development` — fresh implementer subagent + reviewer per task
- `test-driven-development` — RED → GREEN → refactor
- `scrubbing-public-tree` — pre-push hygiene pass
- `finishing-a-development-branch` — push/PR integration decision

If a companion is missing, install it or substitute its documented procedure before proceeding — the stages below reference these skills as written.

## The Pipeline

```
Stage 0: Setup      → worktree + branch from the repo's default branch, verify base
Stage 1: Plan       → writing-plans (TDD checks per task)
Stage 2: Implement  → subagent-driven-development + test-driven-development
Stage 3: Review     → fresh independent whole-branch reviewer
Stage 4: Hygiene    → scrubbing-public-tree on the branch
Stage 5: Integrate  → finishing-a-development-branch (push + open PR)
Stage 6: Gate       → CI green + every review comment resolved
Stage 7: Merge      → only with explicit per-PR authorization; otherwise stop and report
```

### Stage 0 — Setup

- Fetch origin; create an isolated worktree + feature branch **from the repository's default branch** (resolve it — e.g. `git symbolic-ref refs/remotes/origin/HEAD` — never assume `origin/main`, and never branch from a diverged local branch).
- Verify the base: the commit(s) being built on must be ancestors of the new branch.
- Save the plan under the goal's `files/plans/` (or the repo's `docs/superpowers/plans/` when the tree is clean) — never in a dirty working tree.
- **Gate:** isolated worktree + branch exist on the verified base; plan location chosen; companion skills confirmed available (see Prerequisites).

### Stage 1 — Plan

- Follow `writing-plans`. Additionally, give every task a **TDD check script** (shell assertions in `/tmp`, never committed): it must FAIL on the unmodified tree (RED) and PASS after the edit (GREEN).
- Capture repo-specific rules in the plan's Global Constraints (e.g. no `bd` in worktrees, provenance hash updates, Markdown-only).
- **Gate:** plan covers every task with a RED-verified check script; Global Constraints recorded.

### Stage 2 — Implement

- Follow `subagent-driven-development` and `test-driven-development` as written: fresh implementer subagent per task, task reviewer after each, each task check (RED) → edit → check (GREEN) → Conventional Commit.
- Run continuously — no check-ins between tasks. Rule on ambiguity, record rulings in the ledger, keep going.
- **Gate:** every task committed GREEN; all task reviews clean.

### Stage 3 — Independent review

- Assign a FRESH agent (never a task implementer/reviewer) to review the whole branch diff vs base: spec compliance, non-regression of prior safeguards, code/prose quality. Run SDD fix rounds on findings.
- **Gate:** independent review reports no unresolved findings.

### Stage 4 — Hygiene

- Run `scrubbing-public-tree` against the branch's changed files before any push. Fix real findings; classify false positives — never weaken a guard to silence a match. If the skill file itself changed, recompute any pinned hashes afterward.
- **Gate:** hygiene reports no unresolved real findings.

### Stage 5 — Integrate

- Follow `finishing-a-development-branch` for the push/PR decision only — use its push and open-PR options, never its merge option. Selecting merge requires a separate explicit authorization naming the PR, per the Authorization rule above (ask once, name the branch).
- **Gate:** branch pushed and PR opened with user authorization. If the user declines, the pipeline ends here: report the local branch state and stop — do not proceed to Stage 6.

### Stage 6 — Gate

- Monitor CI to completion. Read every review comment and inline thread. Fix real findings; adjudicate non-findings explicitly. Route every fix back through the applicable gates (independent review for logic/prose changes, hygiene for any new content) before pushing the update. Repeat until CI is green and all threads resolved.
- **Gate:** CI green; every review comment and thread resolved.

### Stage 7 — Merge

- Default: STOP and report (PR URL, CI status, comment dispositions) for a merge decision. Merge only under the Authorization rule above.
- **Gate:** merge done with explicit authorization, or report delivered and handed to the user.

## Stop Conditions

Stop and ask the user: any irreversible or destructive operation; any action the Authorization rule covers; a plan so broken every path forward is a guess. Everything else: rule on it, record the ruling, keep going.
