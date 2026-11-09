# Plan: reference fixes, notice intent and project defaults

Template work from the [tracked shared execution plan](../ImmuKnow/plan.md). Filename templates are implemented; other tasks remain planned. Native preparation, checks, policy and bundle implementation belong in Core; this repo owns project data, notice settings, labels, wording and packaged resources.

## F0: filename defaults complete

The active starter patterns in [parameters.yaml](config/parameters.yaml) are individual `{client_id}_{notice_variant}_{language_code}`, normal bundle `{route}_{bundle_number}`, and review bundle `review_{bundle_number}`. They work with size-only grouping and have passed package/native handoff tests. Last-name and school/variant patterns in the README are customization examples, not shipped defaults. Retain this delivered behavior.

## R1: reference fixes — ready next

The inspected checkout does not contain the user's successful project edits:

- [ ] Add `"Meningococcal disease": "Meningococcal"` to [disease_normalization.json](config/disease_normalization.json). All 14 meningococcal agent entries in [vaccine_reference.json](config/vaccine_reference.json) already map to `Meningococcal`; keep them as they are.
- [ ] Add `"TIg": ["Tetanus"]` to the vaccine reference.
- [ ] Add `TIg` to both history `ignore-agents` and `overdue-agent-exclusions` in [settings.typ](templates/settings.typ). Preserve these separate settings: recognition, history display and notice display have distinct purposes.
- [ ] Remove redundant `"Varicella": "Varicella"` if cleaning normalization. Do not create identity mappings for every disease.
- [ ] Verify these authored files appear in the resource distribution, then update Studio's Template package pin/lock. No Core schema change is needed for these data edits.

Checks: Core preparation with fictional Meningococcal disease and TIg recognizes the mapping; representative history and agent notices omit TIg while retaining the original facts; all existing meningococcal mappings remain correct. Keep malformed/conflicting validation fixtures in Core. Template should test project values and rendered behavior, not duplicate its entire validation suite.

## R2a/R2b: notice-local requirements and presentation

[notice_versions.yaml](config/notice_versions.yaml) currently supplies coarse `kind`/`requires` checks. The agreed prerelease v2.0 breaking change removes that file outright and replaces it with a shared helper in each notice that emits validated eligibility/coverage metadata and structured findings. There is no legacy YAML fallback or deprecation period.

- [ ] Participate in R2a before implementation: write the maintained-notice table of existing eligibility predicates, agent/disease/neutral coverage basis and intentional no-records/alternative branches for both languages. The shared helper owns evaluation in native/browser; use the same Core fixture contract rather than inventing separate semantics here. Adopt R2b only after that contract/library exists.
- [ ] Put requirements beside the wording they protect. Share declarations where English/French entry points share intent, while supporting genuinely conditional notices.
- [ ] Convert affirmative and suspension eligibility assertions to structured failures so readable ineligible notices go to review. Preserve their existing predicates/ISPA selection; keep fundamental input/schema/layout assertions when a trustworthy PDF cannot be rendered. Explicitly cover intentional no-records and alternate-text branches in the R2a table.
- [ ] Update maintained notice requirements and remove the YAML catalog from project resources, package expectations, setup/readiness checks, tests and instructions. Use the v2.0 notice-local contract only; add no legacy catalog loader, precedence rules or compatibility resources.
- [ ] Verify an agent coverage mismatch becomes a row failure/review PDF and the corresponding disease notice warns, without changing source facts or assignments. Verify starters/packages contain no notice YAML catalog, valid notices run without it, and missing local requirements cannot fall back to an obsolete file.
- [ ] Review the shared empty-agent-display finding against starter wording, including flu/COVID/TIg exclusions and intentional no-records replacements. Preserve clients/facts and require review for accidental empty recommendations.
- [ ] Explain exact-name exclusions and their display-only effect in the README. Eligibility changes and alternate assignments stay explicit.

Existing evidence: [settings.typ](templates/settings.typ) defines separate history and overdue-agent exclusions; [test_templates.py](tests/test_templates.py) confirms excluded agents remain in facts. The [affirmative notice](templates/affirmative_schedule.en.typ) and [suspension notice](templates/suspension_order.en.typ) already contain local assertions; their eligibility mismatch behavior will become structured failure/review; prerequisite rendering failures remain report-only.

## G1/W1/W2/S1: consume the owning Core changes

- [ ] Review repeated authored website/email/phone destinations with Core's forthcoming aggregate findings. Existing rule-wide overrides are broader than acknowledging one link; do not add blanket URL disabling to project defaults.
- [ ] Keep personalized QR destinations in [settings.typ](templates/settings.typ) distinct: they include client ID and DOB. Do not use a stripped URL as an acceptance key. Authored stable link IDs, if later supported, need an explicit shared contract.
- [ ] Review school reference/export assumptions with the upstream data owner. School validation is currently disabled in [parameters.yaml](config/parameters.yaml); enabling it is a local project choice, not a substitute for Core's missing-ID grouping fix.
- [ ] Keep optional last-name/DOB ordering separate from completed F0 filename support. Once Core supports sorting, document it and opt in through project configuration; source order remains backward compatible.
- [ ] Keep all native policy and bundle changes upstream in Core. Do not restore a local Core patch in this project.

## D1: disease catalog/languages — exploration only

Current normalization standardizes input aliases. Four files under [translations](templates/translations) supply en/fr labels separately for charts and overdue wording; English labels are also presentation data. French files currently contain both `Meningococcal` and `Meningococcal disease` keys, so migration needs alias conflict detection.

- [ ] With Core, prototype a catalog with stable IDs, aliases, and language/context labels. Keep project-specific data and wording editable here.
- [ ] Inventory current agent mapping values, aliases and both label contexts before converting. Preserve chart abbreviations and notice wording separately; do not collapse them into one translated name.
- [ ] Keep old files and imported projects supported until an explicit migration path is tested. A rename to `languages/` is optional presentation organization, not the implementation of normalization or new language support.
- [ ] Verify package inclusion, relative Typst paths, missing-label fallback, unknown names, conflicting aliases and authored label overrides. New languages beyond en/fr need Core and Studio support too.

This exploration must not delay the small Meningococcal/TIg fixes.

## Verification and adoption

Use [CONTRIBUTING.md](CONTRIBUTING.md): run Ruff checks/format check and the relevant `pytest` project/presentation/package checks with the intended native binary. Use one shared fictional sample journey and representative English/French notices; inspect wording and page counts, including empty-list/no-records and exclusion cases. Keep private client data out of examples.

R1 can ship independently. R2a precedes R2b; adopt the schema versions and deferred/prepared evidence specified there. For shared contract changes, update `core-revision.txt`, refresh the complete generated library through native project sync, and test before publishing the Template resource revision. Build/inspect wheel and source distributions with `uv build --out-dir dist` when package contents change. Studio then updates its Template dependency/lock and matching Core revision, regenerates assets and verifies preview plus downloaded native `project sync`, `project check --sample`, `run` and `rebundle`. Preserve imported/authored project bytes; do not change installed package resources in place.
