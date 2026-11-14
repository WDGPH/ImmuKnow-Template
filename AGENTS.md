# Contributor guidance

Read [README.md](README.md) for operators and [CONTRIBUTING.md](CONTRIBUTING.md)
for maintainers. Follow the shared
[project responsibilities](https://docs.phiz.ca/immuknow/latest/ecosystem/),
[documentation principles](https://docs.phiz.ca/immuknow/latest/developer_guide/documentation/)
and [testing boundaries](https://docs.phiz.ca/immuknow/latest/developer_guide/testing/#test-ownership-and-execution).

Template owns authored starter notices, Settings and convenience wrappers,
display translations, example branding, project configuration, reference lists
and the shared fictional clients. Core owns the native engine, schemas and
shared Typst APIs. Studio owns browser editing, previews, fonts, drafts and
project import/export; link to its
[manual](https://docs.phiz.ca/immuknow-studio/latest/) for those workflows.

Use Core's native commands for setup, checks and runs. Keep the privacy hook,
packaging, starter presentation checks and one representative native sample
journey here; do not duplicate Core's validation suite. Python remains a
maintainer/build dependency. Exported operator projects require no Python or uv.

Keep authored files and relative paths intact. Never edit installed packages or
Core's copied shared library. Build copies and generated outputs stay ignored.
Studio consumes a reviewed Template package and matching Core pin; its own guide
owns dependency adoption and browser checks.

Use plausible fictional sample records; keep deliberately invalid data in tests.
Never commit real client data or private assets. Keep current behavior in docs,
completed plans and detailed work evidence outside the repository, and PR
summaries short and plain. Preserve third-party attribution. Prefer direct
solutions that follow Core's
[authoring principles](https://docs.phiz.ca/immuknow/latest/developer_guide/templates/).
