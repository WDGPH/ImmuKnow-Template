# v2 plan: adopt CSV reporting and revised shared QR resources

**Status: planned; implementation pending.** This repository checklist implements Phase 2 and records the Template migration notes arising during Phase 1 in the [shared Core plan](../ImmuKnow/plan.md). That plan owns schemas, report semantics, performance acceptance and cross-repository order; do not duplicate those contracts here. This planning change does not alter runtime files, pins or published resources.

Start at `91c5b1cf5e573d8c8f234d71252ea65bfbe6d9fb`, currently pinning Core `16792decc1e4fb405f63d2780ed87d5f46dba37c`. Template owns authored notices, Settings, translations, reference files, fictional clients, project setup/instructions and the resource package. Core owns the native reporting and shared QR implementation; Studio consumes this package.

Sol coordinates this repository phase, with most implementation delegated to Terra subagents and occasional Astra review of consequential integration decisions. Parallelize independent work where useful; do not split a small migration into artificial release gates. Keep this checklist current while Core iterates, then perform the consumer changes together.

## 1. Prepare the consumer handoff

- [ ] Review the shared CSV v1 / saved-run v2 / render-report v4 fixtures as Core evolves; carry forward final changes in the shared migration ledger. Identify native readers in `tests/conftest.py`, `tests/test_templates.py`, other presentation tests and helper-output assertions. They must consume the new saved evidence/effective-result shape rather than reconstruct the old `render_report` or HTML output.
- [ ] Keep the current authored notice requirements, English/French wording and QR Settings contract. The internal Core grid becomes integer-valued; no boolean compatibility wrapper belongs in this project. Search maintained notices/helpers for direct internal imports and update any that exist. Public `immuknow.qr-code` styling remains available.
- [ ] Prepare representative QR acceptance cases using existing fictional clients: distinct corner/alignment colors to exercise the styled-grid path, each module/corner style, representative Unicode destinations and logo/mask constraints. Also retain default RGB SVG and non-RGB run-path cases. The ordinary default sample may bypass the optimized grid; do not use it to claim the measured speedup.

## 2. Adopt the verified Core commit

After all Core work is coherent and verified:

- [ ] Set `core-revision.txt` to the exact reviewed Core commit and obtain that executable. Refresh the complete generated library with `immuknow project sync --replace`; never edit generated `templates/lib/immuknow/` or ship a partial resource patch.
- [ ] Run `immuknow project check --sample` and retain one `immuknow run --sample` for presentation/native handoff checks. Use the new canonical record and its selected export paths. Check both CSV headers and one row per source record, then follow a record through its original/protected copy when requested and bundle page range.
- [ ] Adapt the existing shared native journey to perform a hold/release and rebundle, resolve the new active export generation, and show earlier bundle/export snapshots still exist. Keep one representative readable requirement failure and one no-PDF case in appropriate test fixtures; Core owns the full failure/recovery matrix.
- [ ] Verify both languages, notice-local coverage/eligibility/display outcomes, long names/addresses/histories, page counts and QR destination/appearance. Keep source facts and expected semantic findings unchanged across the report representation change. Native test readers should retain coverage/source-display evidence assertions while removing assertions for obsolete duplicate measurement storage.

## 3. Update the operator journey and packaged resources

- [ ] Rewrite README sample/review instructions around terminal severity percentages, `records.csv`, `findings.csv`, original/bundle paths and page ranges. Explain the difference between highest severity and delivery route, text import for IDs, and locating the selected generation from the printed paths/`run.json`.
- [ ] Replace references to opening `report.html`, matching per-bundle CSVs, appended CSV filename stems and full technical detail dumps. Explain `warnings`, acknowledgment/revoke and `warnings RUN --refresh` by linking to Core's owning review guide. Acknowledgment never approves delivery or changes severity.
- [ ] Update `CONTRIBUTING.md`, helper messages, package/readiness tests and distribution expectations as needed. Keep native-only setup in the exported starter; add no spreadsheet generator dependency, HTML viewer or Python runtime requirement.
- [ ] Inspect wheel and source distribution: revised README and Core pin, authored Settings/notices/references and fictional examples are present; generated shared library, reports, private data and maintainer tools remain excluded as intended. Do not add report-format settings or compatibility files for the old outputs.

## 4. Verify and hand off to Studio

- [ ] Follow `CONTRIBUTING.md`: Ruff check/format, `uv run --locked --group test pytest`, `uv build --out-dir dist`, package inspection and the representative native journey with `IMMUKNOW_BIN` pointing to the exact candidate executable. Use Core's tests for generic CSV/schema/recovery behavior instead of duplicating them here.
- [ ] Keep tracked authored files unchanged by setup/tests. Record exact Core revision, actual checks and presentation limits, then create the Template adoption commit.
- [ ] Supply Studio that exact Template commit and matching Core commit together. If a later integration change affects Core, refresh the matching pin and affected checks before final adoption; internal Core iterations need no consumer repin. Publishing is a separate task; this plan authorizes no push or release.

## Preserve completed work

Filename defaults remain individual `{client_id}_{notice_variant}_{language_code}`, normal bundle `{route}_{bundle_number}` and review bundle `review_{bundle_number}`; only obsolete CSV naming claims change. Preserve Meningococcal normalization, TIg recognition plus both display exclusions, notice-local requirements without YAML fallback, independent source-row failures, safe school grouping and optional `last_name_dob` sorting. Keep authored project bytes and reference ownership intact.

The supplied native/report profiling is now completed evidence in the shared plan, not deferred work. Disease catalog/language migration and upstream school export review remain outside this change. No additional product decision is required here.
