# Overseer for OpenCode

This repository packages the `overseer` and `plan-review-integrator` skills for easy installation in OpenCode and other compatible agentic environments.

Licensed under MIT.

## Included Skills

1. **overseer**: Orchestrates a multi-agent adversarial review panel (4–6 reviewers + judge) to evaluate code, plans, or documentation.
2. **plan-review-integrator**: A companion skill to apply review findings back into implementation plans with full traceability.
3. **overnight-parallel-lanes**: Sets up an unattended multi-lane coding run — one isolated worktree per lane, parallel workers, independent review per lane, cost-tiered routing, and explicit stop conditions before the merge batch.
4. **feature-pr-pipeline**: Standardized feature-to-PR workflow — plan, implement with subagent-driven TDD, independent review, hygiene pass, then PR with CI and review-comment gating.

## Quick Start Installation

Run the included installation script to copy the skills, support files, and slash commands to your OpenCode configuration directory:

```bash
# Mac / Linux
chmod +x install.sh
./install.sh --target ~/.config/opencode

# For live development (symlinks instead of copying)
./install.sh --target ~/.config/opencode --mode symlink
```

## Usage

Once installed, restart your OpenCode session. You can now trigger the review panel using the registered slash command:

```
> /roundtable ./src
```

Or trigger it naturally:
```
> Run an adversarial review panel on my current implementation plan.
```

The panel will produce three artifacts in your current directory:
- `review_panel_report.md` (Executive Summary & Action Items)
- `review_panel_process.md` (Verbatim Process Log)
- `review_panel_report.html` (Interactive Dashboard)
