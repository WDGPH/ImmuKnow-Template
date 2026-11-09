# Plan: reference fixes, notice intent and project defaults

Template work from the [tracked shared execution plan](../ImmuKnow/plan.md). Filename templates and reference fixes are implemented here and adopted in Studio. Notice-local requirements are verified here and adopted in Studio; the R3 Core pin is ready for the next Studio handoff. Native preparation, checks, policy and bundle implementation belong in Core; this repo owns project data, notice settings, labels, wording and packaged resources.

## F0: filename defaults complete

The active starter patterns in [parameters.yaml](config/parameters.yaml) are individual `{client_id}_{notice_variant}_{language_code}`, normal bundle `{route}_{bundle_number}`, and review bundle `review_{bundle_number}`. They work with size-only grouping and have passed package/native handoff tests. Last-name and school/variant patterns in the README are customization examples, not shipped defaults. Retain this delivered behavior.

## R1: reference fixes complete

The starter now includes the user's successful project edits:

- [x] Add `"Meningococcal disease": "Meningococcal"` to [disease_normalization.json](config/disease_normalization.json). All 14 meningococcal agent entries in [vaccine_reference.json](config/vaccine_reference.json) already map to `Meningococcal` and remain unchanged.
- [x] Add `"TIg": ["Tetanus"]` to the vaccine reference.
- [x] Add `TIg` to both history `ignore-agents` and `overdue-agent-exclusions` in [settings.typ](templates/settings.typ). Recognition, history display and notice display remain distinct.
- [x] Remove redundant `"Varicella": "Varicella"` normalization.
- [x] Verify the authored files appear in the resource distribution. No Core schema change is needed for these data edits.
- [x] Studio adopted the Template resource revision through its package pin/lock in `e851bb0ef752c1d6f052fff73daebe18f7aaf7da`, with fresh build, unit and browser/native handoff checks.

Checks: Core preparation with fictional Meningococcal disease and TIg recognizes the mapping; representative history and agent notices omit TIg while retaining the original facts; all existing meningococcal mappings remain correct. Keep malformed/conflicting validation fixtures in Core. Template should test project values and rendered behavior, not duplicate its entire validation suite.

## R2a/R2b: notice-local requirements and presentation

The prerelease v2.0 notice-local requirements contract replaces the former YAML catalog. Each notice places a shared helper declaration that emits eligibility/coverage metadata and structured findings. There is no legacy YAML fallback or deprecation period.

- [x] Participate in R2a before implementation: write the maintained-notice table of existing eligibility predicates, agent/disease/neutral coverage basis and intentional no-records/alternative branches for both languages. The shared helper owns evaluation in native/browser; use the same Core fixture contract rather than inventing separate semantics here. Adopt R2b only after that contract/library exists.
- [x] Put requirements beside the wording they protect. Share declarations where English/French entry points share intent, while supporting genuinely conditional notices.
- [x] Convert affirmative and suspension eligibility assertions to structured failures so readable ineligible notices go to review. Preserve their existing predicates/ISPA selection; keep fundamental input/schema/layout assertions when a trustworthy PDF cannot be rendered. Explicitly cover intentional no-records and alternate-text branches in the R2a table.
- [x] Update maintained notice requirements and remove the YAML catalog from project resources, package expectations, setup/readiness checks, tests and instructions. Use the v2.0 notice-local contract only; add no legacy catalog loader, precedence rules or compatibility resources.
- [x] Verify an agent coverage mismatch becomes a row failure/review PDF and the corresponding disease notice warns, without changing source facts or assignments. Verify starters/packages contain no notice YAML catalog, valid notices run without it, and missing local requirements cannot fall back to an obsolete file.
- [x] Review the shared empty-agent-display finding against starter wording, including flu/COVID/TIg exclusions and intentional no-records replacements. Preserve clients/facts and require review for accidental empty recommendations.
- [x] Explain exact-name exclusions and their display-only effect in the README. Eligibility changes and alternate assignments stay explicit.

Verification: the shared sample and [test_templates.py](tests/test_templates.py) exercise English/French presentation, agent/disease coverage, review routing, intentional no-records replacement and exclusions while retaining source facts. Affirmative and suspension eligibility failures retain readable notices for review; fundamental rendering failures remain report-only. The package no longer includes the notice YAML catalog.

## G1/W1/W2/S1: adopted Core behavior

The pinned Core includes grouping safety, optional last-name/DOB ordering, structured link aggregation and run-scoped acknowledgment. The starter retains size-only grouping and source ordering; school grouping and sorting are local configuration choices.

- [x] The starter leaves URL checks enabled. Core aggregates exact destinations and supports run-scoped acknowledgment; personalized QR values remain distinct.
- [ ] Review the real school reference/export with its upstream data owner when identified. School validation remains a local configuration choice.
- [x] Document optional last-name/DOB ordering separately from completed F0 filename support; source order remains the default.
- [x] Keep policy and bundle implementation in Core; no local Core patch is needed.

## D1: disease catalog exploration

The shared plan records the completed initial inventory and deferred migration work. The existing normalization and language/context label files remain the active format; catalog migration and new-language support need a separate agreed contract.

## Verification and adoption

Use [CONTRIBUTING.md](CONTRIBUTING.md): run Ruff checks/format check and the relevant `pytest` project/presentation/package checks with the intended native binary. Use one shared fictional sample journey and representative English/French notices; inspect wording and page counts, including empty-list/no-records and exclusion cases. Keep private client data out of examples.

R1 and R2 are implemented and verified, including Studio adoption at `02fb2dc`. R3 is adopted here through the new Core pin; Studio must update its matching pins. The complete generated library was refreshed through native project sync. Build/inspect wheel and source distributions with `uv build --out-dir dist` when package contents change. Studio then updates its Template dependency/lock and matching Core revision, regenerates assets and verifies preview plus downloaded native `project sync`, `project check --sample`, `run` and `rebundle`. Preserve imported/authored project bytes; do not change installed package resources in place.
