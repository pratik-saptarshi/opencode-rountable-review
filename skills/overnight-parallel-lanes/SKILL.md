---
name: overnight-parallel-lanes
version: 1.0.0
author: pratik-saptarshi
description: >
  Set up an unattended multi-lane coding run — overnight or otherwise — where
  a milestone is split into independent workstreams built in parallel. Use when
  independent workstreams should build concurrently with review gating the merge,
  when you will be away while agents work, or when you want parallel throughput
  without babysitting. Does NOT trigger for single tasks, tightly coupled work
  sharing files or interfaces, or work with no deterministic test/lint gate.
---

# Overnight Parallel Lanes

## Overview

One invocation sets up an unattended run: a milestone split into independent lanes, one worker agent per lane in its own git worktree, a different agent reviewing each lane, deterministic gates before merge, and explicit stop conditions. The stop conditions are the skill — unattended scale magnifies errors, cost, and coordination debt, and the most repeated lesson from the field is to install the brakes before the engine.

**Core principle:** Isolated lanes + fresh reviewers + capped rounds + human merge = throughput that stays merge-grade while you are away.

**Provenance.** Distilled from the top-ranked pattern ("overnight feature lanes with independent review") in an Oct 2026 synthesis of Reddit's coding-agent orchestration threads. Honest caveats travel with it: tool-specific evidence was thin — most mature patterns come from the Claude Code and Codex communities and transfer because the mechanics (MCP, skills, hooks, worktrees) are shared. One field report of an uncapped loop (18 hours, 39 commits, no real artifacts, ~$100 of plan budget burned) is the reason the stop conditions below are mandatory, not advisory.

**Works well with:** `overseer` (adversarial review panel) as the per-lane reviewer, and `plan-review-integrator` for folding review findings back into the lane plan. This skill is self-contained — those are upgrades, not requirements.

## When to Use

- A milestone splits into 2+ independent workstreams and you will be away — or you want parallel throughput without babysitting
- Each lane has a deterministic completion gate (tests, lint, build)
- You can name the stop conditions before the first dispatch

**Do NOT use when:** lanes share files or interfaces (split differently or run sequentially); there is no test suite or deterministic gate (unverifiable autonomy becomes babysitting); a single task would finish in minutes (dispatch overhead exceeds the gain).

## The Run Setup

**1. Split into lanes.** Each lane: one bounded deliverable, its own files, its own acceptance test. Two lanes touching the same file are not two lanes — re-split. Record the lane list and the independence argument in the ledger before dispatching anything.

**2. One lane, one worktree, one branch.** Cut every lane worktree from the same base commit. Verify the worktree directory is ignored before creating anything inside it. Never let parallel workers share a working copy.

**3. Dispatch one worker per lane, in parallel.** Each dispatch is self-contained: the lane brief (exact values verbatim), the files it may touch, the deterministic gate commands, the report contract. Workers never dispatch subagents — no reviewer, no helpers. Review arrives from you.

**4. Route by cost.** Mechanical lanes (transcription from a complete spec, single-file changes) go to the cheapest capable tier. Judgment lanes (multi-file integration, debugging) go mid-tier. Reviewers go mid-tier minimum — a cheap reviewer is a rubber stamp. Always name the tier in the dispatch; an omitted tier silently inherits the most expensive model and multiplies across every lane. If your runtime cannot select models per dispatch, say so in the ledger and keep the tier labels as documentation of intent.

**5. Independent review per lane — fresh context, never the author.** The reviewer is a different agent from the lane's worker, handed the diff as a file plus the lane brief. "Nobody accepts their own work" includes you: the coordinator that dispatched a lane does not review it. Each review verdicts two things — spec compliance AND code quality — followed by capped fix rounds with scoped re-reviews (re-reviewer checks only the fix diff and the open findings).

**6. Deterministic gates before review.** Tests, lint, vet, build — run as commands, not as requests. A lane that cannot pass its gate does not reach review; it reports instead of committing broken code.

**7. Batched merge, one CI run, human merge authority.** Lanes merge to the integration branch as a batch; run the full suite once over the batch. You prepare the batch — the human merges and releases. Unattended agents draft and triage; they do not merge, push to shared branches, or publish.

## Stop Conditions

Write these into the ledger BEFORE the first dispatch. They are not advisory.

- **Per-lane time cap.** One hour per lane run by default. A lane that exceeds it is stopped, its partial state committed to its branch, and the lane is re-scoped or parked — never extended silently.
- **Review/fix round cap.** Three fix rounds per lane. At the cap, adjudicate: park with a ruling, or re-scope the lane. Rounds past the cap do not converge — the failure is structural.
- **Redesign threshold.** Two lanes parked, or one lane failing the same gate twice with different approaches → stop the run and redesign the lane split. Do not re-dispatch the same shape hoping for a different result.
- **Budget cap.** Name a total spend ceiling for the run. Cost-tiered routing (step 4) is how you stay under it; the cap is what stops you when routing was wrong.
- **Zero-artifact loop guard.** If commits accumulate with no gate ever passing — the field-reported failure was 18 hours, 39 commits, no real artifacts, ~$100 burned — halt the run. Commits are not progress; passing gates are.

## Ledger

Conversation memory does not survive the night. Every run owns a ledger file (one per run, next to the lane briefs): the lane list, the stop conditions, per-lane status lines (`Lane A: complete (commits a1..b2, review clean)` / `Lane B: parked — <ruling>`), and every ruling with what it costs if wrong. After any interruption, trust the ledger and `git log` over recollection. Never re-dispatch a lane the ledger marks complete.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "These lanes are simple — skip the worktrees" | Shared working copies are how parallel runs corrupt each other. Isolation is not overhead, it is the run. |
| "I'll review the lanes myself, it's faster" | The coordinator that dispatched a lane cannot review it — you have context the reviewer must not, and stakes in the outcome. Fresh agent or it didn't happen. |
| "One more round will converge" | Past the cap, rounds don't converge. Adjudicate and re-scope. |
| "The tests will take too long to run per lane" | A lane without a deterministic gate is unverifiable autonomy. Shrink the gate, don't skip it. |
| "Merging now saves a step in the morning" | Unattended merges are how broken batches land. Prepare the batch; the human merges. |
| "The budget cap is pessimistic" | The $100/18-hour loop started with the same confidence. The cap is the lesson. |

## Quick Reference

| Situation | Action |
|-----------|--------|
| Lanes share a file | Re-split; not independent |
| No deterministic gate | Do not run unattended |
| Lane exceeds 1h | Stop, commit partial, re-scope or park |
| 3 fix rounds exhausted | Adjudicate: park with ruling or re-scope |
| 2 lanes parked | Halt run, redesign the split |
| Commits but no green gate | Halt run (zero-artifact guard) |
| Worker asks to merge/push | Deny — human merge authority |
| Session interrupted | Resume from ledger + `git log`, never re-dispatch complete lanes |
