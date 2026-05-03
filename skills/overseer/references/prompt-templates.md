# Prompt Templates

This file contains the prompt skeletons referenced by `skills/overseer/SKILL.md`.
It is intentionally compact and public-safe: the skill file remains the source of
truth for orchestration behavior.

## Phase 2: Data Flow Tracer
Trace the important data paths, schemas, invariants, and boundary transforms.

## Phase 3: Independent Review
Review the work independently, with no cross-talk, and return findings with citations.

## Phase 4: Private Reflection
Re-read the source, rate confidence, and identify your most/least defensible findings.

## Phase 5: Debate
Respond to unresolved points only; call out new evidence and changed opinions.

## Phase 7: Blind Final
Give a final score, top issues, and recommendation without seeing other final scores.

## Phase 8: Completeness Audit
Look for missed edge cases, constants, and overlooked code paths.

## Phase 10: Claim Verification
Verify citations against source; mark verified, inaccurate, misattributed, hallucinated, or unverifiable.

## Phase 11: Severity Verification
Read the actual codebase, verify P0/P1 claims, and check for existing safety mechanisms.

## Phase 12b: Tier Refinement Advisor
Refine the draft tier table with supporting reasoning and suggested verification persona.

## Phase 13: Targeted Verification Agent
Verify one dispute/action item at a time, using the tiered budget and persona match.

## Phase 14: Supreme Judge
Arbitrate disagreements, validate coverage, and produce the final ruling.

## Phase 14.5: Post-Judge Verification
Re-check any judge-introduced P0/P1 claims against ground truth before report generation.

## Phase 15.2: Process History
Assemble a chronological, verbatim log of the run, including persona profiles.

## Phase 15.3: HTML Report Generation Prompt
Read the markdown report and process history from disk, then render a self-contained HTML dashboard.

## Phase 16: Merge Agent Prompt
Deduplicate findings across runs, score stability, and produce the merged report.
