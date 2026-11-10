# v2 plan: adopt CSV reporting and revised shared QR resources

**Status: Template adoption verified against Core `073dde56ad71cc852141e69135a8b779d4332fe6`.** This repository implements Phase 2 of the [shared Core plan](../ImmuKnow/plan.md). Studio should consume this Template revision together with that exact Core revision. Publishing remains a separate task.

The generated shared library was refreshed with `immuknow project sync --replace`. The native executable used for verification had SHA-256 `fcbe29bfab628cfd65ba8640a68962a6ac21bc7b8cc86fe985de691d612175f6`. Authored notices, Settings, translations and reference data remain project-owned.

- The sample helper reads saved-run v2 keyed observations and effective results, including partial failed checkpoints. Normal runs use Core's terminal receipt; quiet failure diagnostics remain available.
- Operator guidance uses selected paired CSV exports, severity and delivery routes, warning review, and retained rebundle snapshots. The resource wheel contains the revised guide, exact Core pin, authored resources and fictional examples; generated shared library and maintainer helpers are excluded. The source distribution additionally contains the maintained helper scripts used by contributors.
- Verification: Ruff check and format, 64 pytest cases, wheel and source-distribution builds and contents inspection, native `project check --sample` (10/10 PDFs), and a retained `run --sample` (10 source rows). Tests validate CSV headers, hashes and row joins, original and bundle page ranges, hold/release and immutable earlier bundle/export files, a failed preparation without a PDF, and a requested protected copy.
- English and French notice variants retained 50 history rows, QR evidence and multi-page output in the long-content fixture. The deliberately extreme address can be cramped or clipped; this check does not establish unlimited address fit. Core's independent styled QR acceptance covered module and corner styles, colors, Unicode, logo/mask boundaries and decoded rendered PDFs.

## Preserve completed work

Filename defaults remain individual `{client_id}_{notice_variant}_{language_code}`, normal bundle `{route}_{bundle_number}` and review bundle `review_{bundle_number}`; only obsolete CSV naming claims change. Preserve Meningococcal normalization, TIg recognition plus both display exclusions, notice-local requirements without YAML fallback, independent source-row failures, safe school grouping and optional `last_name_dob` sorting. Keep authored project bytes and reference ownership intact.

The supplied native/report profiling is now completed evidence in the shared plan, not deferred work. Disease catalog/language migration and upstream school export review remain outside this change. No additional product decision is required here.
