# Changelog

## 1.2.0 - 2026-08-22

- Promoted the reviewed canonical 1.2.0 behavior from `deldos/skills` PR #51.
- Restored the complete canonical `SKILL.md` semantics and reference set after recovery review found that the earlier public projection had generalized or omitted governed routing behavior.
- Preserve `app-delivery-workshop` preflight compatibility and the required `governed-prd-adr-delivery` private handoff when that specialist is available; portable equivalent routing applies only when the private specialist is genuinely unavailable.
- Keep the public repository as a lineage-preserving distribution of the canonical semantic skill rather than a separately maintained sanitized semantic fork. MIT licensing and public release metadata remain distribution-layer concerns.
- Retired the stale 1.1.1 package from the current skill directory; a 1.2.0 package must be rebuilt only from the merged and verified public release before distribution.

## 1.1.1 - 2026-08-04

- Prepared the earlier connector-independent public projection from canonical `governed-prd-creation` 1.1.1.
- Preserved proposal-first mode selection, explicit product approval, measurable PRD quality, ADR-candidate routing, and requirement traceability.
- Preserved the complete four-state persistence contract: persisted, not persisted, blocked, and write failed.
- Historical note: that projection removed private specialist routing; this approach is superseded by the 1.2.0 one-skill semantic-preservation policy.
