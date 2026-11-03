# ImmuKnow Project Template

A starting point for running [ImmuKnow](https://github.com/WDGPH/ImmuKnow)
immunization notices for one public health unit, without working inside the
ImmuKnow codebase.

This repository maintains the starter letters, Settings, display translations,
example branding and project configuration used by Studio and native projects.
ImmuKnow Core ships the processing engine and shared Typst library, with no
starter letters. Studio owns its fictional client scenarios.

ImmuKnow does all the processing. This repository holds what belongs to your
health unit:

| This repository | ImmuKnow |
|---|---|
| `config/`: run dates, notice catalog, vaccine and disease reference data | Processing, checks and the CSV input schema |
| `templates/`: your notice wording, layout, logo and translations | The shared Typst library (`templates/lib/immuknow/`, generated locally) |
| `input/`: your client CSVs (not committed); fictional sample files | |
| `runs/`: one folder per run (never committed) | |

Studio downloads include this project's Python setup and helper scripts, the
selected notice and its configuration. The **Include fictional client data**
checkbox controls whether the selected fictional inputs and sample setup are
included; custom imported sample data is preserved. Extract the ZIP to run it;
no separate Template checkout is needed. The notice catalog may list notices that are not
in the project.

## Repository structure

The full Template has the layout below. A Studio download may contain only the
selected notice and example files.

```
immuknow-template/
├── config/
│   ├── parameters.yaml           # Dates, bundling, encryption, compiler settings
│   ├── notice_versions.yaml      # Notice versions and who each applies to
│   ├── vaccine_reference.json    # Vaccine agent → diseases it covers
│   ├── disease_normalization.json
│   └── school_reference.json     # Optional: your own school list (default: ImmuKnow's)
├── templates/
│   ├── <version_id>.<language>.typ  # One file per notice and language
│   ├── setup.typ                 # Connect the letter to Settings and client helpers
│   ├── settings.typ              # Fonts, colours, QR code, shared display choices
│   ├── presentation.typ
│   ├── translations/             # Disease names shown on notices
│   ├── assets/                   # logo.png, signature.png
│   └── lib/immuknow/             # Generated from installed Core; ignored by Git
├── input/sample/                 # Synthetic sample cohort and assignments
├── scripts/
│   ├── run.py                    # Run ImmuKnow with this project's folders
│   ├── check.py                  # Check this machine and project are ready
│   ├── check_client_data.py      # Refuse client data files (pre-commit and CI)
│   └── sync_lib.py               # Refresh templates/lib/immuknow after an upgrade
└── tests/
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/). ImmuKnow requires Python 3.11 or later;
  uv installs the version named in `.python-version`.
- [Typst 0.15.1](https://typst.app/docs/changelog/0.15.1/), exactly. ImmuKnow
  rejects other versions. Put `typst` on `PATH`, set `TYPST_BIN`, or set
  `typst.bin` in `config/parameters.yaml`.
- The fonts named in `templates/settings.typ`. The default is FreeSans (GNU
  FreeFont). Typst uses fonts installed on your system.

## Installation

`uv sync` installs the ImmuKnow release named in `pyproject.toml` from GitHub.
`scripts/check.py` and `scripts/run.py` generate a missing shared library from
that installed package. An existing modified or incompatible library is retained
and rejected; use `scripts/sync_lib.py` explicitly when upgrading.
You don't need a copy of the ImmuKnow code.

```bash
git clone <this repository> immuknow-template
cd immuknow-template
uv sync --locked
uv run --locked prek install
uv run python scripts/check.py --sample
```

For a Studio ZIP, extract it and open a terminal in its folder, then run
`uv sync --locked`. With fictional data included, run
`uv run python scripts/check.py --sample`. Without a sample, provide your own
CSV and assignments before running notices. Install Git
as well: uv fetches the pinned Core release from GitHub. If you want to commit
changes, run `git init` before `uv run --locked prek install`.

`sample.json`, when present, names the sample CSV and assignments relative to
the project folder. When fictional client data is included, Studio sets it to
the selected fictional example. Without it, the scripts use `input/sample/sample_students.csv` and
`input/sample/sample_assignments.json`. An imported project's existing sample
selection is preserved. Without fictional data or a prepared example, provide
your own inputs and sample selection before using `--sample`. For example:

```json
{
  "csv": "input/sample/sample_students.csv",
  "assignments": "input/sample/sample_assignments.json"
}
```

`prek install` adds Git hooks that lint and format Python with Ruff and refuse
to commit files that may hold
client information: spreadsheets, PDFs, run records, and anything in `input/`
or `runs/` other than the sample. Git doesn't copy hooks when you clone, so
everyone who commits runs this once in their clone. CI runs the same check.

Run all hooks manually with `uv run --locked prek run --all-files`. The hooks run
the Ruff version locked by the project.

`check.py` reports the ImmuKnow version, whether `config/parameters.yaml` is
valid, the Typst version, whether `templates/lib/immuknow` matches ImmuKnow and
which catalog notices and languages are present in the project. `--sample`
also runs the sample cohort into a temporary folder and lists warnings and
failures by type. A missing font shows up there as
`compiler.font_substitution`. The temporary folder is deleted afterwards. For
the full report, run the sample with `scripts/run.py`
(see "Running notices").

Template maintainers can run `uv run --locked --group test pytest`. Add
`-m "not pipeline"` to skip the full sample run. These tests cover the
Template's helpers and project files, with one sample run to check integration
with ImmuKnow and Typst. ImmuKnow Core tests native input, notice checks and
delivery rules; see the [testing strategy across the projects](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/testing.md#testing-across-the-projects).
Studio downloads do not include the maintainer tests; use
`uv run --locked python scripts/check.py --sample` to check a downloaded project.

## Running notices

Each run takes one CSV and exactly one way of choosing notices:

```bash
# A notice for each client, chosen in an assignments file
uv run python scripts/run.py input/students.csv --notice-assignments input/assignments.json

# The same notice for every client
uv run python scripts/run.py input/students.csv --template overdue_diseases_v1.en.typ
```

A `--template` given as a bare file name is a file in `templates/`, as in an
assignments file. A path such as `../other/overdue_diseases_v1.en.typ` uses that
file and the folder it is in. `--templates` only applies with
`--notice-assignments`.

Try it with the sample:

```bash
uv run python scripts/run.py --sample
```

Paths you supply are relative to your current folder, except for a bare
`--template` filename as described above. By default, `run.py` uses this
project's `config/`, `templates/` and `runs/` folders. Any other option is passed
to ImmuKnow unchanged. For example, `--input-encoding cp1252` reads a CSV saved by
Excel on Windows. See `uv run immuknow --help` for every option.

The output folder must not be inside `config/`, `templates/` or a folder you
read input from. ImmuKnow refuses to run if it is. Running `uv run immuknow`
directly without `--output` writes to `runs/` in your current folder.

### Input CSV

The full rules are in ImmuKnow's
[getting started guide](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/getting_started.md).
The main points:

- Required columns: `school_name`, `client_id` (10 digits), `first_name`,
  `last_name`, `date_of_birth`, `city`, `imms_given`.
- Optional columns: address fields, `overdue_disease`, `overdue_agent`,
  `board_name`, `board_id`, `school_id`, `version_id`. Other columns are ignored.
- **Every history entry ends with a semicolon, including the last:**
  `2013-08-20 - DTaP-IPV-Hib; 2014-10-03 - Var;`. Use `-;` for no history.
  A missing final semicolon rejects the whole file.
- The overdue agents must cover every overdue disease, using
  `config/vaccine_reference.json`. A client whose agents don't cover their
  overdue diseases rejects the whole file.

When a file is rejected, no notices are made. The report lists every problem
row so you can fix them all at once.

### Assignments file

A JSON list with one entry per client. `template` is a file name in
`templates/`. It decides both the notice and the language:

```json
[
  {"client_id": "1009876545", "template": "overdue_agents_v1.fr.typ"},
  {"client_id": "1009876549", "template": "affirmative_schedule_v1.en.typ",
   "experiment_id": "EXP-2026-01", "experiment_arm": "control"}
]
```

### Results

Each run creates its own folder and keeps earlier runs:

```
runs/<run-id>/
├── report.html     # Open this first: every client, check and PDF
├── run.json        # The complete record of the run
├── originals/      # The notices as produced
├── bundles/        # delivery/ (ready to send) and review/ (needs a look)
├── encrypted/      # When encryption is enabled
└── ...
```

The last line of the run prints its status:

| Status | Meaning | Exit code |
|---|---|---|
| `completed` | Every notice was produced and passed its checks | 0 |
| `completed_with_warnings` | Every notice was produced; some need review before delivery | 0 |
| `completed_with_failures` | A notice, check or output step failed | 1 |
| `rejected_input` | The CSV has errors; no notices were made | 1 |
| `failed_setup` | A config, template or Typst problem stopped the run | 1 |

Notices with warnings are held in `bundles/review/`. Once you've checked one,
release it with the token shown in `report.html`:

```bash
uv run immuknow-rebundle runs/<run-id> --accept-warning <token> --reason "Checked layout"
```

The full Template sample finishes `completed_with_warnings` on purpose. A Studio
download may have a different sample, so its findings differ. The full Template
sample warnings show what review looks like:

- `content.multiple_links`: every notice links to more than one website.
- `data.forecast_coverage`: two clients are overdue for one disease, but the
  agent offered (MMR) also covers others.
- `source.address_incomplete`: one client has no street address.
- `layout.section_pages`: one client's immunization history runs onto a second
  page.

Run folders contain client information. Store and delete them according to
your health unit's policies.

## Customizing

Each letter starts with:

```typst
#import "setup.typ": *
#show: immuknow.letter // Apply the letter layout
```

Shared setup supplies the selected client's information, dates and configured
`immuknow` helpers. Call `#immuknow.client-block()`,
`#immuknow.overdue-diseases()` or `#immuknow.immunization-history()` where you
want them to appear. You do not need to pass `notice` to those helpers.
Use `to_student` and `to_guardian` directly in ordinary `if`/`else` wording:

```typst
#if to_student [you have] else if to_guardian [your child has] else [the named client has]
```

`no_records` and `up_to_date` are also booleans for ordinary `#if` wording.
`no_records` reflects the source history before exclusions; `up_to_date` means
there are no overdue diseases, independently of overdue immunizing agents.
The overdue starters use neutral bilingual no-records wording instead of claiming
that someone received no vaccines. To omit an entire section, wrap it in
`#if not no_records [ ... ]`. Change `no-records` on an overdue helper to `none`
to retain its list, `auto` for the bilingual message, or your own text/content.

The affirmative starter asserts `up_to_date`. The suspension starter explicitly
gets `ispa_up_to_date` from `immuknow.notice-flags(include-ispa: true)`, requires
an overdue ISPA disease and lists only ISPA diseases for the client's birth
cohort. In particular, varicella is included for births from January 1, 2010.
ISPA flags/filtering can require a usable birth date and assessment date.
Ordinary overdue notices still accept mixed ISPA and non-ISPA disease lists;
`ispa-only: true` is optional for disease lists and unsupported for agent lists.
These checks use upstream overdue facts; they do not assess exemptions or
legal grounds for suspension. Explicit notice assignments and A/B testing stay
available. A dynamic notice can use `requires: any` in its catalog entry and
branch on these flags within its wording.

History Settings explicitly enable dose validity. Fully unflagged histories still
render recorded-dose marks; partially flagged histories must be corrected or
explicitly displayed with `show-validity: false`. Only applicable legends appear.
Customize `legend-labels` with `valid`, `invalid`, and `unspecified` entries;
English and Canadian French defaults are supplied by Core.

The optional CSV `oiid` column carries the Ontario Immunization ID as text.
Settings expose `show-client-id` and `show-oiid`, allowing either, both, or
neither. Client ID remains the assignment identifier even when hidden.
With OIID display enabled, `missing-oiid: none` omits missing rows' lines,
`""` leaves the value blank, `auto` shows “Not available” / “Non disponible”,
and a string supplies custom text. Some clients may have an OIID while others
do not; an all-absent input cohort errors when OIID display is enabled.
Customize `id-label` and `oiid-label` without altering source facts.

The optional CSV `reader` column accepts `student` or `guardian`. An explicit
choice takes priority over age, including in the suspension order. Otherwise,
the default is student wording at age 16 or older and guardian wording under 16.
Unknown age without a reader choice makes both flags false, selecting neutral
wording. The flags are always booleans and cannot both be true. The address
block uses the same reader; provide the intended mailing destination in the
source address columns. Choosing a reader leaves age and birth date unchanged.
See [Core's intended-reader guide](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/getting_started.md#intended-reader)
for input validation and saved source facts.

`notice` remains available for client facts. The opening import, Settings
marker and `#show: immuknow.letter` line are essential setup; keep them in place.
Omit components a letter does not use, including QR calls. Add
`#immuknow.qr-code(..qr)` where a QR code should appear. The client block needs
only `window: envelope-window`; use `font-size: 11pt` or `details: "below"`
directly on that block when you want to change its defaults.
Settings connects client data to Core's helpers and supplies shared defaults;
`setup.typ` exposes those helpers under the `immuknow.` prefix. Keep both files
with the letter. General helpers such as `immuknow.link` use the same prefix.

| To change | Edit |
|---|---|
| Delivery and "as of" dates (every cycle) | `date_of_delivery`, `date_as_of` in `config/parameters.yaml` |
| Bundle size and grouping, encryption | `config/parameters.yaml` |
| Contact details, privacy wording and suspension dates | The `<version_id>.<language>.typ` files |
| Logo, signature, fonts, colours, QR appearance | `templates/settings.typ`, `templates/assets/` and signature calls in the letter |
| Letter wording | The `<version_id>.<language>.typ` files |
| Disease names on notices | `templates/translations/` (not `templates/lib/immuknow/locales/`, the library's defaults) |
| Which notices exist and who they apply to | `config/notice_versions.yaml` |
| Vaccine and disease mapping | `config/vaccine_reference.json`, `config/disease_normalization.json` |

Settings holds the shared defaults. To change one history table, pass named
options at its call in the letter:

```typst
#immuknow.immunization-history(show-age: true, font-size: 12pt, min-rows: 8)
```

Page options work the same way:

```typst
#immuknow.notice-page("Immunization Record", title-size: 18pt, allow-overflow: true)[
  #immuknow.immunization-history()
]
```

These choices affect only that call. Other pages and tables keep the defaults
from Settings. Use Settings when a choice should apply throughout the project.
`presentation.typ` loads the editable translation files; shared date and label
formatting functions come from `immuknow`.

The full Template maintains the starter project. Its templates use placeholder
contact details (`example.org`, `1-800-555-0100`), a placeholder logo and a
placeholder signature. Replace them before sending real notices. The dates in
`parameters.yaml` are examples. A Studio download contains the authored files
from that project; review them before sending real notices.

School validation is off in the full Template. To use it, set `school_validation.enabled: true` and
set `target_phu` to your health unit's name as it appears in the school list.
With `reference_file: null`, ImmuKnow uses the school list it ships with, which
updates when you upgrade ImmuKnow. To use your own list, put it in `config/` in
the same format and set `reference_file` to its file name. If that file is
missing, the run stops rather than falling back to ImmuKnow's list.

ImmuKnow checks `config/` strictly. Misspelled or retired settings stop the run
with a message saying what to change. The settings are described in ImmuKnow's
[configuration guide](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/configuration.md).

**After changing fonts**, run a sample notice in each language. Some fonts
store accented capitals in a way that fails ImmuKnow's client-details check.
FreeSerif from Ubuntu's `fonts-freefont-ttf` package (2021 and later) is a
known example.

**Using ImmuKnow Studio:** its ZIP is already a runnable project. When copying
changes into an existing project, review shared settings and assets before
replacing files. Copy the selected sample inputs and `sample.json` as well if
you want the same trial run. Then run `uv run python scripts/check.py --sample`.
Studio includes fonts and licences under `templates/fonts/` for manual
installation; native Typst uses system fonts.

## Updating ImmuKnow

1. Change the tag at the end of the ImmuKnow line in `pyproject.toml`, for
   example `@v2.1.0`.
2. `uv sync`
3. `uv run python scripts/sync_lib.py` copies the new shared library into
   `templates/lib/immuknow/`. ImmuKnow refuses to run with an outdated copy.
   Review the change with `git diff templates/lib`.
4. If you keep your own school list, compare it with the one in the new
   ImmuKnow release for schools that opened, closed or were renamed. This
   prints where ImmuKnow's list is. With `reference_file: null` there is
   nothing to do: runs use the new list automatically.
   ```bash
   uv run python -c "from immuknow.resources import resource_root; print(resource_root() / 'config' / 'school_reference.json')"
   ```
5. Compare your authored project with this repository for starter changes.
   `sync_lib.py` updates only the Core library; it preserves your letters,
   Settings, assets, translations and configuration.
6. Run `uv run python scripts/check.py --sample`. Template maintainers can also
   run `uv run --locked --group test pytest`.
7. Commit `uv.lock` together with any config and template changes. The generated
   `templates/lib/immuknow/` tree stays out of Git.

## Where ImmuKnow comes from

`pyproject.toml` pins ImmuKnow to reviewed commit `499dd2a` on
GitHub. This includes the merged template and dependency updates in
[Core PR #230](https://github.com/WDGPH/ImmuKnow/pull/230) and
[Core PR #229](https://github.com/WDGPH/ImmuKnow/pull/229); it is not a new release candidate:

```toml
dependencies = [
    "ImmuKnow @ git+https://github.com/WDGPH/ImmuKnow@499dd2a2a04e6d621e3720a4f0fe618727cf1bd5",
]
```

`uv.lock` records the same exact commit. Commit it so everyone runs
the same ImmuKnow.

To test changes in a local ImmuKnow checkout next to this repository,
uncomment these lines in `pyproject.toml`, then run `uv sync`. Comment them
again and run `uv sync` before committing.

```toml
[tool.uv.sources]
ImmuKnow = { path = "../ImmuKnow", editable = true }
```

## Troubleshooting

**`Typst executable not found` or `Unsupported compiler`**: install Typst
0.15.1, or point `TYPST_BIN` at it.

**`ImmuKnow library file differs from the supplied version`**: run
`uv run python scripts/sync_lib.py`.

**`rejected_input`**: open the `report.html` path printed by the run. It lists
each problem row and column. History formatting and overdue-agent coverage are
the usual causes.

**`Selected source … overlaps output workspace`**: choose an `--output` folder
outside `config/`, `templates/` and your input folder.

**Accented letters doubled in the client-details check (`ÉÉcole`)**: change
the font. See "After changing fonts" above.

## Studio starter snapshot

`studio-scaffold.json` lists the starter letters, Settings, assets, translations,
configuration, setup files and helper scripts that Studio bundles from a pinned
commit of this repository. It excludes `templates/lib/immuknow/`: Studio obtains
the shared library from installed Core. Studio supplies the selected fictional
client inputs when requested in the download dialog. Maintainer tests stay here
and are not bundled.

Studio records the source commit and original file hashes and verifies the local
snapshot during asset preparation. After changing a listed file, refresh Studio's
snapshot with its documented `python -m scripts.project_template` command.
A starter wording change requires a new Template snapshot; it does not require
a Core release. Normal Studio builds and downloads need no private repository access.
