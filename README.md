# ImmuKnow Project Template

A starting project for creating personalized immunization notices with
[ImmuKnow Core](https://docs.phiz.ca/immuknow/latest/). Adapt the notices,
settings, translations and example branding for your organization before
sending notices. The source system assesses immunization status; you choose
the notices, and Core creates PDFs and reports their checks.

## What belongs here

| Folder | Contents |
| --- | --- |
| `config/` | Run dates, grouping, password settings and vaccine/disease reference lists. |
| `templates/` | Authored notices, Settings, display translations and example images. |
| `references/` | Optional reference lists, including the saved Ontario school list. |
| `input/sample/` | Shared fictional clients and their notice choices. Keep real input files elsewhere in `input/`. |
| `runs/` | Generated notices and reports; never committed. |

Core owns the native engine, schemas and shared Typst APIs. Its complete shared
library is installed in `templates/lib/immuknow/` during setup and stays intact.
[Studio](https://docs.phiz.ca/immuknow-studio/latest/) owns browser editing,
previews and project downloads. It consumes this project's resource package
and fictional clients. See [contributing](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md)
for maintaining Template and its package.

## Set up the project

Run these commands from the project folder, which contains `config/` and
`templates/`.

1. Obtain an `immuknow` executable matching `core-revision.txt` and put it on
   your terminal's PATH. Use a matching [Core release archive](https://github.com/WDGPH/ImmuKnow/releases)
   when available, or ask your maintainer for a prepared executable.
   Core's [release guide](https://docs.phiz.ca/immuknow/latest/developer_guide/releases/)
   explains platform choices and checksums; Template contributors can
   [build the recorded revision](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md#build-the-reviewed-core).
2. Install the fonts named in `templates/settings.typ`. The starters use
   FreeSans and FreeSerif from [GNU FreeFont](https://www.gnu.org/software/freefont/).
3. Install and check the executable's shared library:

   ```sh
   immuknow project sync
   immuknow project check
   ```

The executable includes Typst. Operator setup, sample checks and notice
generation require neither Python, uv nor a separate Typst installation.
Core's [project commands](https://docs.phiz.ca/immuknow/latest/developer_guide/cli/#native-project-setup-and-samples)
describe checks, replacement and recovery. Keep your changes outside
`templates/lib/immuknow/`.

Keep personal information out of Git. The ignore rules exclude run outputs
and common client-data files; maintainers can install the
[commit checks](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md#checks-before-committing).

## Try the fictional clients

```sh
immuknow project check --sample
immuknow run --sample
```

The check renders the sample temporarily; the run retains its output under
`runs/`. Open the printed `records.csv` and `findings.csv` files and review the
PDFs before delivery. Core's [review guide](https://docs.phiz.ca/immuknow/latest/user_guide/pdf_validation/)
explains findings, delivery routes, holds and rebundling.

The ten shared fictional clients cover English and French notices, supplied
overdue and up-to-date records, optional Ontario Immunization IDs and an
explicit guardian choice. Eight have recorded histories; two have no recorded
immunizations. Example run dates are in November 2026, after the supplied
vaccination dates. These records are for notice development, not clinical
assessment or advice.

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

See Core's [CSV guide](https://docs.phiz.ca/immuknow/latest/user_guide/input_schema/)
for columns and history formatting, and its
[notice selection guide](https://docs.phiz.ca/immuknow/latest/user_guide/configuration/)
for the assignments file. Keep output separate from authored files and input.

The conventional fictional sample is in `input/sample/`. A project's
`sample.json` can select another project-relative CSV and assignments file;
Studio downloads supply the selected example this way. Core's
[project commands](https://docs.phiz.ca/immuknow/latest/developer_guide/cli/#native-project-setup-and-samples)
own the sample-selection contract.

## Change your notices

| To change | Edit |
| --- | --- |
| Dates, grouping, filenames and password-protected copies | `config/parameters.yaml` |
| Wording, contacts, privacy text and suspension wording | The `<version_id>.<language>.typ` notices |
| Fonts, colours, title alignment, page size, envelope window and QR appearance | `templates/settings.typ` |
| Logo and signature | `templates/assets/` and the image calls in the notices |
| Disease names shown on notices | `templates/translations/` |
| When a notice applies and what it must cover | Its `immuknow.requirements` call |
| Vaccine-to-disease mapping and source disease names | `config/vaccine_reference.json`, `config/disease_normalization.json` |

Keep each notice's opening Settings marker, `#import "settings.typ" as immuknow`
and `#show: immuknow.letter`. Settings connects the current client's facts to
Core's helpers and supplies project defaults. Starter names and assignment
values use the same notice filenames, such as `overdue_agents.en.typ`.

The notices print `date_of_delivery` as the letter date and `date_as_of` as the
assessment date. Optional `date_due` and `date_of_suspension` supply the update
deadline and suspension start. Edit these in `config/parameters.yaml` for your
reviewed requirements and school calendar; Core's
[configuration guide](https://docs.phiz.ca/immuknow/latest/user_guide/configuration/)
explains date rules and other run settings.

Set `title-align` to `left`, `center` or `right` in Settings. Named options on
one `immuknow.notice-page` or `immuknow.immunization-history` call override its
shared defaults, for example:

```typst
#immuknow.immunization-history(show-age: true, font-size: 12pt)
```

`overdue-agent-exclusions` omits exact source labels from the overdue-agent
list. The starter uses `("COVID-19 mRNA", "Inf (TIV)", "TIg")`; use the actual
labels in your source when they differ. This choice is independent of the
history table's `ignore-agents` and leaves supplied facts unchanged. Use
`#immuknow.overdue-agents(ignore-agents: ())` to show every source agent in one
call. Put intentional replacement wording in
`#immuknow.agent-alternative[Your wording]` and keep each notice's requirements
beside its wording. Core's
[authoring guide](https://docs.phiz.ca/immuknow/latest/developer_guide/templates/)
owns the helper APIs, requirements, display checks and QR options.

Replace placeholder contacts, branding and signatures before using real data.
After changing fonts or layout, inspect English and French examples, long
addresses and histories, envelope placement and QR destinations. Reference
lists support input interpretation; they do not turn the fictional examples
into an immunization assessment.

## Check school names

School checking is off by default. `config/school_reference.json` contains
fictional sample schools. To use your own list, put it in `config/`, enable
`school_validation` in `config/parameters.yaml` and select its exact health unit
name. Review the list independently when updating Core.

`references/ontario_schools.json` retains a saved Ontario list. Its metadata
identifies the Ministry of Health workbook
`PHIX Reference Lists v5.2 - 2025Jun30.xlsm`. Review it before use. To select it:

```yaml
school_validation:
  enabled: true
  reference_file: ../references/ontario_schools.json
  target_phu: Wellington-Dufferin-Guelph Public Health
```

## Grouping and filenames

The starter uses source order and size-only grouping. To separate notices by
school, version and language, for example:

```yaml
bundling:
  group_by: [school, notice_variant, language]
  sort_by: last_name_dob
filenames:
  bundle:
    template: '{school}_{notice_variant}_{bundle_number}'
```

The individual default is `{client_id}_{notice_variant}_{language_code}`;
the bundle default is `{route}_{bundle_number}` and the review default is
`review_{bundle_number}`. These name PDFs. The selected run-wide
`records.csv` and `findings.csv` exports are separate. Core's
[configuration guide](https://docs.phiz.ca/immuknow/latest/user_guide/configuration/#filename-templates)
owns supported fields, grouping, fallback behavior and naming rules.

## Update Core

Obtain the reviewed executable recorded in `core-revision.txt`, then run:

```sh
immuknow project sync --replace
immuknow project check --sample
```

Review a retained sample run after the update. Your notices, Settings,
translations and reference files remain project-owned. See the
[contributor guide](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md)
for updating the recorded pin and resource package. Studio records its own
reviewed Template dependency; updating this checkout does not change it.
