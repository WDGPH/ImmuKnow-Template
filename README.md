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
The run keeps the results. Open the new folder inside `runs`, then open
`report.html` in a browser. Review
the checks and original notices. When grouping is enabled, `bundles-0001/`
contains PDFs combining notices for sending, separate `review-*.pdf` files for
readable notices that failed checks, and matching CSV page lists. Warnings can
be included for sending by default, so review them too. A notice that could not
be created appears in the report without a PDF.

The ten fictional clients cover English and French letters, supplied overdue
and up-to-date records, optional Ontario Immunization IDs and a guardian-directed
notice. All ten have recorded histories. Example run dates are in November 2026,
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
immuknow run input/clients.csv --project . --template overdue_diseases_v1.en.typ
```

See Core's [CSV guide](https://github.com/WDGPH/ImmuKnow/blob/b5a1ae4c3a0411f570aae2f6f1d829eda746d787/docs/user_guide/input_schema.md)
and [configuration guide](https://github.com/WDGPH/ImmuKnow/blob/b5a1ae4c3a0411f570aae2f6f1d829eda746d787/docs/user_guide/configuration.md)
for columns, history formatting and the JSON selection file. Keep the output
folder separate from templates, settings and input files.

To hold a notice or create a new set of combined PDFs from a saved run:

```sh
immuknow rebundle runs/<run-id> --withhold row-000001 --reason "Pending review"
immuknow rebundle runs/<run-id> --release row-000001
```

A hold excludes the notice from both normal and review PDFs. Each attempt keeps
the previous files. Releasing a hold leaves the notice's checks in force.

## Change your notices

| To change | Edit |
| --- | --- |
| Dates, grouping, password-protected copies | `config/parameters.yaml` |
| Wording, contacts, privacy text and suspension dates | The `<version_id>.<language>.typ` notices |
| Fonts, colours, title alignment, page size, envelope window and QR appearance | `templates/settings.typ` |
| Logo and signature | `templates/assets/` and the image calls in the notices |
| Disease names shown on notices | `templates/translations/` |
| Which notices exist and when each applies | `config/notice_versions.yaml` |
| Vaccine-to-disease mapping and source disease names | `config/vaccine_reference.json`, `config/disease_normalization.json` |

Keep each notice's opening import, Settings marker and `#show: immuknow.letter`
line. `setup.typ` and `settings.typ` connect client information to the shared
helpers. Put your own changes outside `templates/lib/immuknow/`; Core requires
that shared library to match the executable.

The default connected-square QR style uses Core's faster vector rendering.
Settings also allow dots, rounded or separated squares, independent corner and
alignment colours, and a centre image. Core's template guide below explains
the options and image constraints.

Replace placeholder contacts, branding and signatures before sending real
notices. After changing fonts or layout, inspect English and French examples,
long addresses and histories, envelope placement and QR links. Core's
[template guide](https://github.com/WDGPH/ImmuKnow/blob/b5a1ae4c3a0411f570aae2f6f1d829eda746d787/docs/developer_guide/templates.md)
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
version ID, such as `overdue_agents_v1`, rather than the general notice kind.
Keep filename version suffixes until intentionally migrating the matching
catalog and assignments; they identify notices in runs and bundles.
