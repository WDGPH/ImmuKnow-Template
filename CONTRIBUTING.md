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
immuknow project sync --replace
```

To test a local Core build, set `IMMUKNOW_BIN` to its executable. Project setup, checks and sample runs use Core's native commands. Legacy Python
helpers remain for compatibility and maintainer tests; they never import a
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
shared fictional sample run for presentation checks, selected CSV joins and
hold/release snapshots. Core owns the input and PDF
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
notices, user instructions and the recorded Core revision. It excludes generated Core
library files, Python helpers/setup, maintainer tests and real client data.
Python is used to build and consume the resource distribution; its exported
project requires only the native executable and installed fonts.

Build and inspect both distribution formats with:

```sh
uv build --out-dir dist
```

`immuknow_template.resources.project_files()` returns the project files and
source hashes. The two example-data helpers supply the fictional client CSV
and default selections separately. Git installs also report their Template
commit; a standalone wheel has no Git commit to report.

When updating Studio, change its Template dependency and lock alongside the
matching Core pin. Regenerate browser resources, verify previews and exercise a
downloaded project outside both checkouts using native `project sync`,
`project check --sample`, `run` and `rebundle` commands. The Python test harness
may inspect PDFs, but must not install Python tools into the downloaded project.
Preserve imported project files, including legacy helpers if supplied by users.

Starter notice IDs now omit `_v1`. Update entry filenames and assignments together when adopting these names in an existing project. Do not
rename saved-run artifacts; rebundling uses their recorded original identities.
