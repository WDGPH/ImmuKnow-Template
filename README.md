# ImmuKnow Template

A starting project for creating personalized immunization notices with
[ImmuKnow](https://docs.phiz.ca/immuknow/latest/). Adapt the notices,
settings, translations and example branding for your organization before
sending notices. The source system assesses immunization status; you choose
the notices, and ImmuKnow creates PDFs and reports their checks.

## What belongs here

| Folder | Contents |
| --- | --- |
| `config/` | Run dates, grouping, password settings and vaccine/disease reference lists. |
| `templates/` | Authored notices, Settings, display translations and example images. |
| `references/` | Optional reference lists, including the saved Ontario school list. |
| `input/sample/` | Shared fictional clients. Keep real input files elsewhere in `input/`. |
| `runs/` | Generated notices and reports; never committed. |

ImmuKnow owns the native engine, schemas and shared Typst APIs. Its complete shared
library is installed in `templates/lib/immuknow/` during setup and stays intact.
[ImmuKnow Studio](https://docs.phiz.ca/immuknow-studio/latest/) owns browser editing,
previews and project downloads. It consumes this project's resource package
and fictional clients. See [contributing](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md)
for maintaining Template and its package.

## Set up the project

Run these commands from the project folder, which contains `config/` and
`templates/`.

1. Download [ImmuKnow v2.0.0](https://github.com/WDGPH/ImmuKnow/releases/tag/v2.0.0),
   which matches `immuknow-revision.txt`, and put the extracted `immuknow`
   executable on your terminal's PATH.
   ImmuKnow's [release guide](https://docs.phiz.ca/immuknow/latest/developer_guide/releases/)
   explains platform choices and checksums; Template contributors can
   [build the recorded revision](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md#build-the-reviewed-immuknow).
2. Install the fonts named in `templates/settings.typ`. The starters use
   FreeSans and FreeSerif from [GNU FreeFont](https://www.gnu.org/software/freefont/).
3. Install and check the executable's shared library:

   ```sh
   immuknow project sync
   immuknow project check
   ```

The executable includes Typst. Operator setup, sample checks and notice
generation require neither Python, uv nor a separate Typst installation.
ImmuKnow's [project commands](https://docs.phiz.ca/immuknow/latest/developer_guide/cli/#native-project-setup-and-samples)
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
PDFs before delivery. ImmuKnow's [review guide](https://docs.phiz.ca/immuknow/latest/user_guide/pdf_validation/)
explains findings, delivery routes, holds and rebundling.

The ten shared fictional clients include overdue and up-to-date records, optional Ontario Immunization IDs and an
explicit guardian choice. Eight have recorded histories; two have no recorded
immunizations. Example run dates are in November 2026, after the supplied
vaccination dates. These records are for notice development, not clinical
assessment or advice. The default notice targets overdue clients, so the full
collection also produces eligibility failures and review routing for clients who
are up to date. Choose a suitable notice for each real client.

## Use your own client list

Save your CSV in `input/` and choose one notice for everyone:

```sh
immuknow run input/clients.csv --project . --template overdue_diseases.en.typ
```

See ImmuKnow's [CSV guide](https://docs.phiz.ca/immuknow/latest/user_guide/input_schema/)
for columns and history formatting, and its
[notice selection guide](https://docs.phiz.ca/immuknow/latest/user_guide/configuration/)
for advanced per-client assignments and A/B selection. Keep output separate
from authored files and input.

The conventional fictional sample is in `input/sample/`. A project's
`sample.json` selects a project-relative CSV and template path;
use `--sample --template <filename>` to choose a different template.
Studio downloads supply the selected example this way. ImmuKnow's
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
ImmuKnow's helpers and supplies project defaults. Starter names and assignment
values use the same notice filenames, such as `overdue_agents.en.typ`.

The notices print `date_of_delivery` as the letter date and `date_as_of` as the
assessment date. Optional `date_due` and `date_of_suspension` supply the update
deadline and suspension start. Edit these in `config/parameters.yaml` for your
reviewed requirements and school calendar; ImmuKnow's
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
beside its wording. ImmuKnow's
[authoring guide](https://docs.phiz.ca/immuknow/latest/developer_guide/templates/)
owns the helper APIs, requirements, display checks and QR options.

Replace placeholder contacts, branding and signatures before using real data.
After changing fonts or layout, inspect English and French examples, long
addresses and histories, envelope placement and QR destinations. Reference
lists support input interpretation; they do not turn the fictional examples
into an immunization assessment.

## Check school names

School checking is enabled by default. `config/school_reference.json` contains
the fictional sample schools. To use your own list, put it in `config/`, set
`school_validation.reference_file` in `config/parameters.yaml` and select its
exact health unit name with `target_phu`. Review the list independently when
updating ImmuKnow.

`references/ontario_schools.json` retains a saved Ontario list. Review it before
use. To select it:

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
`records.csv` and `findings.csv` exports are separate. ImmuKnow's
[configuration guide](https://docs.phiz.ca/immuknow/latest/user_guide/configuration/#filename-templates)
owns supported fields, grouping, fallback behavior and naming rules.

## Update ImmuKnow

Obtain the reviewed executable recorded in `immuknow-revision.txt`, then run:

```sh
immuknow project sync --replace
immuknow project check --sample
```

Review a retained sample run after the update. Your notices, Settings,
translations and reference files remain project-owned. See the
[contributor guide](https://github.com/WDGPH/ImmuKnow-Template/blob/main/CONTRIBUTING.md)
for updating the recorded pin and resource package. Studio records its own
reviewed Template dependency; updating this checkout does not change it.
