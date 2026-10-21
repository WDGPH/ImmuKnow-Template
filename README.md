# ImmuKnow Project Template

A starting point for running [ImmuKnow](https://github.com/WDGPH/ImmuKnow)
immunization notices for one public health unit, without working inside the
ImmuKnow codebase.

ImmuKnow does all the processing. This repository holds what belongs to your
health unit:

| This repository | ImmuKnow |
|---|---|
| `config/`: run dates, notice catalog, vaccine and disease reference data | Processing, checks and the CSV input schema |
| `templates/`: your notice wording, layout, logo and translations | The shared Typst library (`templates/lib/immuknow/`, copied here) |
| `input/`: your cohort CSVs (never committed) | |
| `output/`: one folder per run (never committed) | |

The layout of `config/` and `templates/` matches an ImmuKnow Studio export, so
a project exported from Studio can replace them directly.

## Repository structure

```
immuknow-template/
├── config/
│   ├── parameters.yaml           # Dates, bundling, encryption, compiler settings
│   ├── notice_versions.yaml      # Notice versions and who each applies to
│   ├── vaccine_reference.json    # Vaccine agent → diseases it covers
│   ├── disease_normalization.json
│   └── school_reference.json     # ImmuKnow's school list, copied unchanged
├── templates/
│   ├── <version_id>.<language>.typ  # One file per notice and language
│   ├── settings.typ              # Contact details, fonts, colours, QR code, display choices
│   ├── presentation.typ
│   ├── translations/             # Disease names shown on notices
│   ├── assets/                   # logo.png, signature.png
│   └── lib/immuknow/             # Shared library: do not edit (see "Updating ImmuKnow")
├── input/sample/                 # Synthetic sample cohort and assignments
├── scripts/
│   ├── run.py                    # Run ImmuKnow with this project's folders
│   ├── check.py                  # Check this machine and project are ready
│   ├── check_client_data.py      # Refuse client data files (pre-commit and CI)
│   └── sync_lib.py               # Refresh templates/lib/immuknow after an upgrade
└── tests/
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/). It installs the Python version named in
  `.python-version`.
- [Typst 0.15.1](https://typst.app/docs/changelog/0.15.1/), exactly. ImmuKnow
  rejects other versions. Put `typst` on `PATH`, set `TYPST_BIN`, or set
  `typst.bin` in `config/parameters.yaml`.
- The fonts named in `templates/settings.typ`. The default is FreeSans (GNU
  FreeFont). Typst uses fonts installed on your system.

## Installation

`uv sync` installs the ImmuKnow release named in `pyproject.toml` from GitHub.
You don't need a copy of the ImmuKnow code.

```bash
git clone <this repository> immuknow-template
cd immuknow-template
uv sync
uv run pre-commit install
uv run python scripts/check.py --sample
```

`pre-commit install` adds a Git hook that refuses to commit files that may hold
client information: spreadsheets, PDFs, run records, and anything in `input/`
or `output/` other than the sample. Git doesn't copy hooks when you clone, so
everyone who commits runs this once in their clone. CI runs the same check.

`check.py` reports the ImmuKnow version, whether `config/parameters.yaml` is
valid, the Typst version, whether `templates/lib/immuknow` matches ImmuKnow and
which languages each notice has. It uses the same checks as a run. `--sample`
also runs the sample cohort into a temporary folder and lists its warnings by
type. A font that isn't installed shows up there as `compiler.font_substitution`. The temporary folder is
deleted afterwards. For the full report, run the sample with `scripts/run.py`
(see "Running notices").

To run the tests, use `uv run pytest`. Add `-m "not pipeline"` to skip the
full sample run.

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
uv run python scripts/run.py input/sample/rodent_dataset.csv \
  --notice-assignments input/sample/assignments.json
```

Paths are relative to your current folder. `run.py` fills in `--config config/`,
`--templates templates/` and `--output output/`. Any other option is passed to
ImmuKnow unchanged. For example, `--input-encoding cp1252` reads a CSV saved by
Excel on Windows. See `uv run immuknow --help` for every option.

The output folder must not be inside `config/`, `templates/` or a folder you
read input from. ImmuKnow refuses to run if it is.

### Input CSV

The full rules are in ImmuKnow's
[getting started guide](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/getting_started.md).
The main points:

- Required columns: `school_name`, `client_id` (10 digits), `first_name`,
  `last_name`, `date_of_birth`, `city`, `imms_given`.
- Optional columns: address fields, `overdue_disease`, `overdue_agent`,
  `board_name`, `board_id`, `school_id`, `version_id`. Other columns are ignored.
- **Every history entry ends with a semicolon, including the last:**
  `Aug 20, 2013 - DTaP-IPV-Hib; Oct 3, 2014 - Var;`. Use `-;` for no history.
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
output/<run-id>/
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
| `completed_with_failures` | Some notices could not be produced | 1 |
| `rejected_input` | The CSV has errors; no notices were made | 1 |
| `failed_setup` | A config, template or Typst problem stopped the run | 1 |

Notices with warnings are held in `bundles/review/`. Once you've checked one,
release it with the token shown in `report.html`:

```bash
uv run immuknow-rebundle output/<run-id> --accept-warning <token> --reason "Checked layout"
```

The sample run finishes `completed_with_warnings` on purpose. Its warnings show
what review looks like: one client has no street address, one history runs
onto a second page, and each notice has several links.

Run folders contain client information. Store and delete them according to
your health unit's policies.

## Customizing

| To change | Edit |
|---|---|
| Delivery and "as of" dates (every cycle) | `date_of_delivery`, `date_as_of` in `config/parameters.yaml` |
| Bundle size and grouping, encryption | `config/parameters.yaml` |
| Contact details, logo, signature, fonts, colours, QR code | `templates/settings.typ`, `templates/assets/` |
| Letter wording | The `<version_id>.<language>.typ` files |
| Disease names on notices | `templates/translations/` (not `templates/lib/immuknow/locales/`, the library's defaults) |
| Which notices exist and who they apply to | `config/notice_versions.yaml` |
| Vaccine and disease mapping | `config/vaccine_reference.json`, `config/disease_normalization.json` |

The starting files are ImmuKnow's defaults. The templates use placeholder
contact details (`example.org`, `1-800-555-0100`), a placeholder logo and a
placeholder signature. Replace them before sending real notices. The dates in
`parameters.yaml` are examples.

School validation is off. To use it, set `school_validation.enabled: true` and
set `target_phu` to your health unit's name as it appears in
`config/school_reference.json`. That file is ImmuKnow's school list, copied
unchanged; don't edit it.

ImmuKnow checks `config/` strictly. Misspelled or retired settings stop the run
with a message saying what to change. The settings are described in ImmuKnow's
[configuration guide](https://github.com/WDGPH/ImmuKnow/blob/main/docs/user_guide/configuration.md).

**After changing fonts**, run a sample notice in each language. Some fonts
store accented capitals in a way that fails ImmuKnow's client-details check.
FreeSerif from Ubuntu's `fonts-freefont-ttf` package (2021 and later) is a
known example.

**Using ImmuKnow Studio:** replace `config/` and `templates/` with those from
the exported project, then run `uv run python scripts/check.py --sample`.

## Updating ImmuKnow

1. Change the tag at the end of the ImmuKnow line in `pyproject.toml`, for
   example `@v2.1.0`.
2. `uv sync`
3. `uv run python scripts/sync_lib.py` copies the new shared library into
   `templates/lib/immuknow/`. ImmuKnow refuses to run with an outdated copy.
   Review the change with `git diff templates/lib`.
4. Copy ImmuKnow's school list into `config/`:
   ```bash
   uv run python -c "import shutil; from immuknow.resources import resource_root; shutil.copy(resource_root() / 'config' / 'school_reference.json', 'config/')"
   ```
5. Compare your `templates/` and `config/` with ImmuKnow's defaults for new or
   renamed settings. The script prints where ImmuKnow's copies are.
6. `uv run python scripts/check.py --sample` and `uv run pytest`.
7. Commit `uv.lock` together with any config and template changes.

## Where ImmuKnow comes from

`pyproject.toml` pins ImmuKnow to a release tag on GitHub:

```toml
dependencies = [
    "ImmuKnow @ git+https://github.com/WDGPH/ImmuKnow@v2.0.0",
]
```

`uv.lock` records the exact commit behind the tag. Commit it so everyone runs
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
