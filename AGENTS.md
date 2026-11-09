# Contributor guidance

Follow the [shared language and project responsibilities](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/documentation.md).

Template owns authored starter letters, Settings, display translations, example
branding, project configuration, local setup, helper commands, readiness checks
and starter presentation tests. Core ships the shared library, schemas and generic
native project commands; project settings and reference lists belong here.
Template owns the shared fictional example clients for notice development.
Studio uses them for previews and consumes a pinned resource package. Keep
user instructions in the [README](README.md), and maintainer instructions in [CONTRIBUTING.md](CONTRIBUTING.md). Link to
[ImmuKnow Core](https://github.com/WDGPH/ImmuKnow) for native contracts and
[ImmuKnow Studio](https://github.com/WDGPH/ImmuKnow-Studio) for the browser
workflow.

Follow the [shared testing strategy](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/testing.md).
Test helper commands, paths, readiness checks and the handoff to Core. Keep one
shared native sample journey plus starter wording/page-count checks; do not
duplicate Core's validation suite. Studio downloads use native setup and sample
commands and omit Python tooling and maintainer tests.

Use plausible fictional sample records for notice development. Keep deliberately
invalid data in test fixtures. Do not commit real client data or private assets.

Documentation describes current behavior; Git history records how it changed.
Keep pull request descriptions short and plain, focused on rationale and the
result for users. Omit agent attribution and detailed verification logs.

Studio installs the resource package from a pinned Template commit.
Make setup and helper changes here, then update Studio's dependency and lock.
Never edit installed resources. Build copies belong in generated output only.

Prefer clear, direct authoring and abstractions that earn their complexity. Follow
Core's [authoring principles](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/templates.md).
