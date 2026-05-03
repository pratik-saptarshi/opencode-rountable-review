# Signals and Checklists

This is the public companion index for `skills/overseer/SKILL.md`.

## Signal groups
- **Security:** auth, secrets, permissions, injection, sanitization, XSS, CSRF
- **Reliability:** retries, idempotency, rollback, race conditions, timeouts
- **Data:** SQL, schemas, migrations, transformations, validation, null handling
- **Infra:** Docker, Kubernetes, CI/CD, cloud, networking, deployment
- **Frontend:** React, TypeScript, accessibility, layout, rendering, forms
- **Docs/Plans:** completeness, ambiguity, contradictory requirements, missing steps

## Reviewer checklist
- Trace the data flow end-to-end
- Verify invariants and guards
- Look for duplicated logic or boundary violations
- Check for missing tests on critical paths
- Distinguish existing defects from plan risks
- Confirm any external-domain claims with authoritative sources when needed

## Sanity checks
- Prefer concrete file/line evidence
- Avoid speculative severity inflation
- Do not treat pre-existing debt as a must-fix unless the plan worsens it
