# ImmuKnow Project Template

A starting project for creating personalized immunization notices with
[ImmuKnow](https://github.com/WDGPH/ImmuKnow). It contains example notices,
settings, translations, images and fictional clients. Adapt and review the
content for your organization before sending notices.

The system supplying your client information assesses immunization status.
You choose the notices; ImmuKnow creates PDFs and reports their checks.

## What belongs here

| Folder | Contents |
| --- | --- |
| `config/` | Run dates, grouping, password settings, notice choices and vaccine/disease reference lists. |
| `templates/` | Notice wording, fonts, colours, QR links, translations and example images. |
| `references/` | Optional reference lists, including the former Core Ontario school list. |
| `input/sample/` | Fictional clients and their notice choices. Keep real input files elsewhere in `input/`. |
| `runs/` | Generated notices and reports; never committed. |

Core supplies the processing application and shared Typst components. The shared
library is copied into `templates/lib/immuknow/` during setup and is not committed.

## Set up the project

1. Obtain an `immuknow` executable matching the Core revision recorded in
   `core-revision.txt`. Ask your project maintainer for it. Developers can
   [build the pinned revision](https://github.com/WDGPH/ImmuKnow-Template/blob/feat/rust-core-project/CONTRIBUTING.md#build-the-reviewed-core).
2. Install the fonts named in `templates/settings.typ`. The examples use
   FreeSans and FreeSerif from GNU FreeFont.
3. Install the shared library supplied by the executable:

   ```sh
   immuknow project sync
   immuknow project check
   ```

The executable includes Typst. Setup, sample checks and notice generation need
neither Python, uv nor a separate Typst installation. Run commands from the
project folder, or supply `--project /path/to/project`.

Keep personal information out of Git. The ignore rules exclude run outputs and
common client-data files; maintainers can also install the
[commit checks](https://github.com/WDGPH/ImmuKnow-Template/blob/feat/rust-core-project/CONTRIBUTING.md#checks-before-committing).

## Try the fictional clients

From the project folder, run:

```sh
immuknow project check --sample
immuknow run --sample
```

The check renders the sample in a temporary folder and removes its output.
The run keeps the results and prints counts and percentages for error, warning,
clear and pending records, followed by the selected `records.csv` and
`findings.csv` paths. `records.csv` has one row per source record; use `row_key`
to join its findings, and open IDs as text in your spreadsheet. Paths are relative
to the run folder. Original and protected PDF paths and inclusive bundle page
ranges identify available notices. The selected paths are also in `run.json`.

Severity summarizes effective findings and required work; route describes delivery. A warning can
still be eligible for sending, while a readable notice with failed checks goes
to review. A notice that could not be created has no PDF path. Review the findings
and PDFs before delivery.

The ten fictional clients cover English and French letters, supplied overdue
and up-to-date records, optional Ontario Immunization IDs and a guardian-directed
notice. Eight have recorded histories; two have no recorded immunizations. Example run dates are in November 2026,
after the supplied vaccination dates. These records are not clinical assessments
or advice for an individual.

## Use your own client list

Save your CSV and notice choices in `input/`, then run:

```sh
immuknow run input/clients.csv --notice-assignments input/assignments.json \
  --templates templates --config config --output runs
```

To use one notice for everyone:

```sh
immuknow run input/clients.csv --project . --template overdue_diseases.en.typ
```

See Core's [CSV guide](https://github.com/WDGPH/ImmuKnow/blob/e9189d1633a0c590a50adf0fb010b33760d919ba/docs/user_guide/input_schema.md)
and [configuration guide](https://github.com/WDGPH/ImmuKnow/blob/e9189d1633a0c590a50adf0fb010b33760d919ba/docs/user_guide/configuration.md)
for columns, history formatting and the JSON selection file. Keep the output
folder separate from templates, settings and input files.

The required history column is `immunizations_given`. Each semicolon-separated
entry contains a date, agent and optional validity result. Rename an older
`imms_given` header before running; it is no longer accepted.

Duplicate nonblank client IDs normally reject the input. To accept repeats for
specific clients, set `allowed_duplicate_client_ids: ["0123456789"]` in
`config/parameters.yaml`. Keep the IDs quoted. Every repeated source row is
rendered separately with a warning, using the same assignment for that client ID.
Unlisted duplicate IDs still reject the input. Use the report's distinct row keys
for holds or row-specific policy decisions.

To hold a notice or create a new set of combined PDFs from a saved run:

```sh
immuknow rebundle runs/<run-id> --withhold row-000001 --reason "Pending review"
immuknow rebundle runs/<run-id> --release row-000001
```

A hold excludes the notice from both normal and review PDFs. Each attempt keeps
the previous files. Releasing a hold leaves the notice's checks in force. The
selected CSV pair changes with each successful rebundle; earlier exports remain
available. Use `immuknow warnings runs/<run-id>` to review warnings and
`immuknow warnings runs/<run-id> --refresh` to regenerate exports. The
[review guide](https://github.com/WDGPH/ImmuKnow/blob/e9189d1633a0c590a50adf0fb010b33760d919ba/docs/user_guide/pdf_validation.md)
explains acknowledgment and revocation. Acknowledging a warning does not approve
delivery or change severity.

## Change your notices

| To change | Edit |
| --- | --- |
| Dates, grouping, password-protected copies | `config/parameters.yaml` |
| Wording, contacts, privacy text and suspension dates | The `<version_id>.<language>.typ` notices |
| Fonts, colours, title alignment, page size, envelope window and QR appearance | `templates/settings.typ` |
| Logo and signature | `templates/assets/` and the image calls in the notices |
| Disease names shown on notices | `templates/translations/` |
| Which notices exist and when each applies | The notice files and their `immuknow.requirements` calls |
| Vaccine-to-disease mapping and source disease names | `config/vaccine_reference.json`, `config/disease_normalization.json` |

Keep each notice's opening import, Settings marker and `#show: immuknow.letter`
line. `settings.typ` connects client information to the shared
helpers. Put your own changes outside `templates/lib/immuknow/`; Core requires
that shared library to match the executable.

Set `overdue-agent-exclusions` in Settings to omit exact source agent names from
the overdue-agent list. This is separate from the history table's `ignore-agents`
and leaves source facts, history and overdue-disease lists unchanged. The starter
uses `("COVID-19 mRNA", "Inf (TIV)", "TIg")`, omitting those labels only; use the actual
labels in your input when they differ. A single call can override the shared
choice with `#immuknow.overdue-agents(ignore-agents: ())`. If every source
agent is excluded, the notice is sent to review unless a no-records or authored
alternative is displayed. Exclusions do not change eligibility or assignments.

Each notice places one `#immuknow.requirements(eligibility: "...", coverage: "...")`
call beside its wording. These requirements check whether the selected notice
applies and whether its recommendations cover the supplied diseases. A readable
notice that fails a requirement is retained for review. To write alternative
agent wording, use `#immuknow.agent-alternative[Your wording]` in place of the
agent list; it records the intentional replacement. The default no-records
wording is also an intentional replacement, but does not change eligibility.

The default connected-square QR style uses Core's faster vector rendering.
Settings also allow dots, rounded or separated squares, independent corner and
alignment colours, and a centre image. Core's template guide below explains
the options and image constraints.

Replace placeholder contacts, branding and signatures before sending real
notices. After changing fonts or layout, inspect English and French examples,
long addresses and histories, envelope placement and QR links. Core's
[template guide](https://github.com/WDGPH/ImmuKnow/blob/e9189d1633a0c590a50adf0fb010b33760d919ba/docs/developer_guide/templates.md)
explains the available components and options.

## Check school names

School checking is off by default. `config/school_reference.json` contains only
fictional sample schools. To use your own list, put it in `config/`, set
`school_validation.enabled: true`, and select its exact health unit name.
With `reference_file: null`, Core uses `school_reference.json` in that folder.
It does not supply a regional fallback.

`references/ontario_schools.json` preserves the former Core list unchanged. Its
metadata identifies the Ontario Ministry of Health workbook
`PHIX Reference Lists v5.2 - 2025Jun30.xlsm`. Treat it as a saved reference and
review it for changes before use. To select that file, for example:

```yaml
school_validation:
  enabled: true
  reference_file: ../references/ontario_schools.json
  target_phu: Wellington-Dufferin-Guelph Public Health
```

Updating Core does not update your school list. This project's reference files
are maintained separately from the application.

## Project checks and samples

`immuknow project check` compares the entire shared library with the executable
and prepares the sample to check its configuration and inputs. Add `--sample`
to create the sample notices in a temporary folder. Checks leave authored files
unchanged. Use `immuknow run --sample` to keep the notices and their full report.
Warnings remain eligible for sending; failures return a nonzero exit status.

`sample.json`, when present, selects a sample CSV and notice choices relative
to the project folder. Studio uses this for a selected or imported example:

```json
{"csv": "examples/clients/short.csv", "assignments": "examples/assignments/short.json"}
```

[Studio](https://immuknow.phiz.ca/) is a separate browser editor. A downloaded
project must include compatible shared files and project settings. Check its
version instructions; updating this repository does not update Studio's pin.

## Update Core

Get the reviewed executable recorded in `core-revision.txt`, then refresh its
complete shared library:

```sh
immuknow project sync --replace
immuknow project check --sample
```

Keep your notices, settings, images and translations. `--replace` only replaces
`templates/lib/immuknow/`; it refuses linked library paths. Without `--replace`,
sync accepts an identical library and refuses to overwrite a different one.
Inspect a retained sample run and its report after an update.

Developers and resource-package maintainers: see
[contributing](https://github.com/WDGPH/ImmuKnow-Template/blob/feat/rust-core-project/CONTRIBUTING.md).
Python helpers remain in the source repository for compatibility and maintainer
checks; Studio's starter resource package omits them and Python setup files.

## Dates, headings and grouping

The letters print `date_of_delivery` as the letter date. `date_as_of` is the
assessment date used in the wording. Optional `date_due` and
`date_of_suspension` select the update deadline and suspension start. Omit them
or use `null` when they do not apply. Supplied dates must follow
`date_as_of <= date_of_delivery < date_due < date_of_suspension`; omitted dates
are skipped when comparing. Set suspension timing from your reviewed project
requirements and school calendar; Core does not calculate the end date.

Set `title-align` in `templates/settings.typ` to `left`, `center` or `right`.
Individual `immuknow.notice-page` calls can override that option for one page.
Studio also exposes title alignment in Theme.

To keep different notice versions in separate bundles, use
`bundling.group_by: notice_variant`. Add language when it also needs separating:
`bundling.group_by: [notice_variant, language]`. The variant is the selected
version ID, such as `overdue_agents`, rather than the general notice kind.
Starter filenames use descriptive notice IDs without a default `_v1` suffix.
Assignments use the same IDs as the notice filenames; saved runs retain their
original identities.

When grouping by school or board, Core warns if an ID is missing and uses the available name; missing identities and conflicting names for one ID go to review. Verify source identifiers with the data owner.

Bundles keep source order by default (`bundling.sort_by: source`). To order
notices by last name and date of birth, set `bundling.sort_by: last_name_dob`.

## Output filenames

Edit `filenames` in `config/parameters.yaml` using `{field}` placeholders, as
with the encryption password template. The starter individual pattern is
`{client_id}_{notice_variant}_{language_code}` for originals and protected copies
in separate directories. The bundle pattern `{route}_{bundle_number}` works
with size-only grouping. Core appends PDF/CSV extensions and matching CSV stems.

For school-based batch names, set `bundling.group_by` to
`[school, notice_variant, language]` and the bundle pattern to
`{school}_{notice_variant}_{bundle_number}`. This produces names such as
`example_school_overdue_agents_01.pdf`. The starter review pattern is `review_{bundle_number}`. Omit
`review_bundle` for an automatic `review_` prefix, or provide its own pattern. A referenced bundle value must be
identical across members. Missing/mixed values use a fallback with a warning;
collisions receive deterministic suffixes. Removing filename settings restores
Core's legacy naming for new runs.

See Core's [supported fields and normalization](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/configuration.md#filename-templates)
and [rebundling with new names](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/pdf_validation.md#rebuild-bundles).
