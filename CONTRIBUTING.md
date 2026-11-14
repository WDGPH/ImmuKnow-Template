# Maintaining this project

Template owns authored starter notices, Settings and convenience wrappers,
display translations, example branding, project configuration, reference lists
and the shared fictional clients. Operator setup and customization belong in
the [README](README.md).

ImmuKnow owns the native engine, schemas and shared Typst APIs. Follow its
[authoring guide](https://docs.phiz.ca/immuknow/latest/developer_guide/templates/)
and [testing boundaries](https://docs.phiz.ca/immuknow/latest/developer_guide/testing/#test-ownership-and-execution).
[ImmuKnow Studio](https://docs.phiz.ca/immuknow-studio/latest/development/)
owns browser editing, previews and downloads, along with its dependency-update
and browser verification procedures.

## Build the reviewed ImmuKnow

`immuknow-revision.txt` is the authoritative reviewed ImmuKnow source commit. Use a
matching executable from ImmuKnow's
[release archives](https://docs.phiz.ca/immuknow/latest/developer_guide/releases/)
when available. For a source build, install the Rust toolchain required by that
commit and run:

```sh
cargo install --git https://github.com/WDGPH/ImmuKnow \
  --rev "$(cat immuknow-revision.txt)" --locked
immuknow project sync --replace
```

For tests, set `IMMUKNOW_BIN` to an executable outside PATH. Tests and operators
use ImmuKnow's public native commands. When updating the pin, refresh the complete
shared library and verify the sample journey; keep the pin and related project
changes together. Never modify generated shared resources. Reference lists
remain a separate Template responsibility.

## Checks before committing

Install Python 3.11 or later and [uv](https://docs.astral.sh/uv/), then from the
repository root:

```sh
uv sync --locked --group test
uv run --locked prek install
uv run --locked ruff check --no-fix .
uv run --locked ruff format --check .
uv run --locked --group test pytest
```

Python is a maintainer and resource-packaging dependency. Operator projects use
the separately installed native executable and the fonts selected in Settings.
The commit hook rejects likely client-data files, including run output saved
outside `runs/`.

Tests cover the privacy hook, resource distributions, starter wording and layout,
explicit translation dependencies, and a representative native sample run.
ImmuKnow owns input validation, encryption, saved-report recovery and bundling tests;
do not reproduce its complete suite here. Use deliberately invalid data only
in test fixtures. CI installs the pinned ImmuKnow and sample fonts before running
these checks. Tracked authored files must remain unchanged by tests.

## Starter resources for Studio

`immuknow-template-resources` packages authored configuration, reference lists,
notices, operator instructions, fictional examples and the recorded ImmuKnow pin.
The installed files are read-only. Studio copies them before editing and gets
the complete shared Typst library from ImmuKnow.

Build the wheel and source archive with:

```sh
uv build --out-dir dist
```

`immuknow_template.resources.project_files()` returns the scaffold and its file
hashes. The example helper returns the shared client CSV. The scaffold includes
that CSV and its default selection in `sample.json`. Git installations report the actual Template commit;
a standalone wheel has no Git revision to report. Preserve that distinction.

The wheel excludes ImmuKnow's generated library, maintainer scripts, tests and Python
setup files from operator projects. The source archive includes packaging and
maintenance sources so its wheel can be rebuilt. Packaging tests check both
formats, authored additions, generated-file exclusions and native setup of an
exported project with no Python tools on PATH.

After a package change, hand the reviewed Template commit to Studio's maintainer.
Follow Studio's [dependency-update procedure](https://docs.phiz.ca/immuknow-studio/latest/development/#update-the-project-template)
there. An unpublished local candidate must be verified as such; never invent a
source revision or edit an installed package to simulate adoption.
