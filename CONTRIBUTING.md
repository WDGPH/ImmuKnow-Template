# Maintaining this project

User setup and notice customization belong in the [README](README.md). This
guide covers the reviewed Core revision, tests and the resource package used
by Studio. Keep examples fictional and project instructions in plain language.

## Build the reviewed Core

`core-revision.txt` records the reviewed ImmuKnow source commit. Install Rust
1.92 or later, then run:

```sh
cargo install --git https://github.com/WDGPH/ImmuKnow \
  --rev "$(cat core-revision.txt)" --locked
python scripts/sync_lib.py
```

To test a local Core build, set `IMMUKNOW_BIN` to its executable. The helpers
call Core's `run`, `prepare` and `resources` commands; they never import a
Python Core package. No separate Typst executable is used.

When updating Core, change the recorded commit, refresh the complete generated
library, and run the sample journey. Review reference data separately: upgrading
the application does not replace project settings or school lists. Keep the
recorded revision and related project changes in the same commit.

## Checks before committing

Install [uv](https://docs.astral.sh/uv/), then:

```sh
uv sync --locked --group test
uv run --locked prek install
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked --group test pytest
```

Python dependencies are for project checks and the Studio resource package,
not the notice-processing engine. Tests use a real native executable and one
six-client sample run for presentation checks. Core owns the input and PDF
validation suite; do not repeat it here. The commit check rejects client-data
files even when run output is accidentally placed outside `runs/`.

CI builds the pinned Rust application, installs the example fonts, then checks
the project, helpers and resource distributions. Tests must leave tracked
files unchanged. Generated library files and output folders stay out of Git.

## Starter resources for Studio

The `immuknow-template-resources` Python package contains project files for
Studio to read. It has no dependency on the former Python Core application.
The installed files are read-only; Studio copies them to a project before
changing them. The package includes configuration, optional reference lists,
notices, helpers and the recorded Core revision. It excludes generated Core
library files, maintainer tests and real client data.

Build and inspect both distribution formats with:

```sh
uv build --out-dir dist
```

`immuknow_template.resources.project_files()` returns the project files and
source hashes. The two example-data helpers supply the fictional client CSV
and default selections separately. Git installs also report their Template
commit; a standalone wheel has no Git commit to report.

Studio must update its Template dependency and lock when adopting this PR. Its
integration also needs the native Core commands, unversioned schema filenames,
and the matching exported library. Those Studio changes belong in its repository;
this Template PR supplies the compatible project files and package.

Before updating Studio's Template pin, change `scripts/project_template.py` to
read `core-revision.txt` instead of looking for a Python Core dependency in
`uv.lock`. Its preparation, resource and build-info scripts must call the native
commands; its font preparation and CI must stop installing or importing Python
Core. Update the contract-preparation script to use `rendering.json` and
`report.json`. Test a browser preview and a downloaded project together before
adopting the new pin. The installed Template resource API and fictional example
paths are unchanged.

Studio's downloaded-project tests must also read `render_report` rather than
`render_summary`, and replace warning-token acceptance and Python rebundling
with native `rebundle` holds/releases. Keep the browser's build identity fields,
but compose them from the reviewed executable build and exported resource hashes;
`resources` returns hashes, not the former Python build-info object. Do not infer
a source commit from `immuknow --version` alone.
