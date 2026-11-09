# Plan: reference fixes, notice intent and project defaults

Template work from the [shared investigation plan](../plan.md). Filename templates are implemented; other tasks remain planned. Native preparation, checks, policy and bundle implementation belong in Core; this repo owns project data, notice settings, labels, wording and packaged resources.

## P0: editable individual and batch filename templates — highest usability priority

- [x] After Core supports filename settings, add documented patterns to [parameters.yaml](config/parameters.yaml), following the existing `encryption.password.template` authoring approach. Configuration: `filenames.individual.template`, `filenames.bundle.template`, optional `filenames.review_bundle.template`; stem-only values, with extensions supplied by Core.
- [x] Show an individual example `{last_name}_{first_name}_{client_id}_{notice_variant}` and batch example `{school}_{notice_variant}_{bundle_number}`, producing `normalized_schoolname_noticevariant_01.pdf`. The individual pattern also names protected copies in their separate directory; review batches have a clear prefix and PDF/CSV stems match.
- [x] Document Core's explicit supported-field lists for individual versus batch scope. Reuse encryption names such as `school` and `language_code`; batch fields need one value across all actual members. Explain chunk numbering, filename normalization, missing/mixed-field fallback and deterministic collision suffixes. Keep filename fields independent from password derivation.
- [x] Verify authored patterns survive package export and an actual native original/protected/bundle/review journey. Existing projects without patterns retain old names. Adopt the compatible Core pin before adding settings to avoid rejection by old strict readers.
- [x] Ship this usability work independently of warning acknowledgment, catalog redesign and optional last-name/DOB sorting; retain grouping behavior; mixed batch fields use an explicit filename fallback. Studio then updates matching pins and preserves editable patterns in downloads.

## P0: carry run-local reference fixes upstream

The inspected checkout does not contain the user's successful project edits:

- [ ] Add `"Meningococcal disease": "Meningococcal"` to [disease_normalization.json](config/disease_normalization.json). All 14 meningococcal agent entries in [vaccine_reference.json](config/vaccine_reference.json) already map to `Meningococcal`; keep them as they are.
- [ ] Add `"TIg": ["Tetanus"]` to the vaccine reference.
- [ ] Add `TIg` to both history `ignore-agents` and `overdue-agent-exclusions` in [settings.typ](templates/settings.typ). Preserve these separate settings: recognition, history display and notice display have distinct purposes.
- [ ] Remove redundant `"Varicella": "Varicella"` if cleaning normalization. Do not create identity mappings for every disease.
- [ ] Verify these authored files appear in the resource distribution, then update Studio's Template package pin/lock. No Core schema change is needed for these data edits.

Checks: Core preparation with fictional Meningococcal disease and TIg recognizes the mapping; representative history and agent notices omit TIg while retaining the original facts; all existing meningococcal mappings remain correct. Keep malformed/conflicting validation fixtures in Core. Template should test project values and rendered behavior, not duplicate its entire validation suite.

## P1: move requirements beside notice wording

[notice_versions.yaml](config/notice_versions.yaml) currently supplies coarse `kind`/`requires` checks. The agreed design replaces that separate authoring requirement with a shared helper in each notice that emits validated eligibility/coverage metadata and structured findings.

- [ ] Adopt Core's shared helper/report contract only after the compatible library and schema support exist. Declare agent/disease coverage intent separately from eligibility, without inferring intent from filenames.
- [ ] Put requirements beside the wording they protect. Share declarations where English/French entry points share intent, while supporting genuinely conditional notices.
- [ ] Review existing affirmative/suspension assertions. Use structured failures where retaining a readable review PDF is intended; keep assertions where producing any PDF is inappropriate. Do not merely replace the YAML with more fatal assertions.
- [ ] Migrate maintained notice requirements, then remove the starter YAML catalog from new project resources and setup instructions. Core retains optional YAML fallback for older imported projects; users should not maintain duplicate declarations. Document migration and local-declaration precedence.
- [ ] Verify an agent coverage mismatch becomes a row failure/review PDF and the corresponding disease notice warns, without changing source facts or assignments. Verify new projects run without the catalog and legacy projects still work.
- [ ] Review the shared empty-agent-display finding against starter wording, including flu/COVID/TIg exclusions and intentional no-records replacements. Preserve clients/facts and require review for accidental empty recommendations.
- [ ] Explain exact-name exclusions and their display-only effect in the README. Eligibility changes and alternate assignments stay explicit.

Existing evidence: [settings.typ](templates/settings.typ) defines separate history and overdue-agent exclusions; [test_templates.py](tests/test_templates.py) confirms excluded agents remain in facts. The [affirmative notice](templates/affirmative_schedule.en.typ) and [suspension notice](templates/suspension_order.en.typ) already contain local assertions; their PDF-retention behavior needs an explicit migration decision.

## P1/P2: project review, grouping and bundle preferences

- [ ] Review repeated authored website/email/phone destinations with Core's forthcoming aggregate findings. Existing rule-wide overrides are broader than acknowledging one link; do not add blanket URL disabling to project defaults.
- [ ] Keep personalized QR destinations in [settings.typ](templates/settings.typ) distinct: they include client ID and DOB. Do not use a stripped URL as an acceptance key. Authored stable link IDs, if later supported, need an explicit shared contract.
- [ ] Review school reference/export assumptions with the upstream data owner. School validation is currently disabled in [parameters.yaml](config/parameters.yaml); enabling it is a local project choice, not a substitute for Core's missing-ID grouping fix.
- [ ] Keep optional last-name/DOB ordering separate from P0 filename patterns. Once Core supports sorting, document it and opt in through project configuration; source order remains backward compatible.
- [ ] Keep all native policy and bundle changes upstream in Core. Do not restore a local Core patch in this project.

## Explore: disease catalog and languages

Current normalization standardizes input aliases. Four files under [translations](templates/translations) supply en/fr labels separately for charts and overdue wording; English labels are also presentation data. French files currently contain both `Meningococcal` and `Meningococcal disease` keys, so migration needs alias conflict detection.

- [ ] With Core, prototype a catalog with stable IDs, aliases, and language/context labels. Keep project-specific data and wording editable here.
- [ ] Inventory current agent mapping values, aliases and both label contexts before converting. Preserve chart abbreviations and notice wording separately; do not collapse them into one translated name.
- [ ] Keep old files and imported projects supported until an explicit migration path is tested. A rename to `languages/` is optional presentation organization, not the implementation of normalization or new language support.
- [ ] Verify package inclusion, relative Typst paths, missing-label fallback, unknown names, conflicting aliases and authored label overrides. New languages beyond en/fr need Core and Studio support too.

This exploration must not delay the small Meningococcal/TIg fixes.

## Verification and adoption

Use [CONTRIBUTING.md](CONTRIBUTING.md): run Ruff checks/format check and the relevant `pytest` project/presentation/package checks with the intended native binary. Use one shared fictional sample journey and representative English/French notices; inspect wording and page counts, including empty-list/no-records and exclusion cases. Keep private client data out of examples.

For shared contract changes, update `core-revision.txt`, refresh the complete generated library through native project sync, and test before publishing the Template resource revision. Build/inspect wheel and source distributions with `uv build --out-dir dist` when package contents change. Studio then updates its Template dependency/lock and matching Core revision, regenerates assets and verifies preview plus downloaded native `project sync`, `project check --sample`, `run` and `rebundle`. Preserve imported/authored project bytes; do not change installed package resources in place.
