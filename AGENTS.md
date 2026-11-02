# Contributor guidance

Follow the [shared language and project responsibilities](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/documentation.md#shared-language-and-project-responsibilities).

This Template owns local project setup, helper commands, readiness checks and
project tests. Keep their instructions in the [README](README.md). Link to
[ImmuKnow Core](https://github.com/WDGPH/ImmuKnow) for native contracts and
[ImmuKnow Studio](https://github.com/WDGPH/ImmuKnow-Studio) for the browser
workflow.

Follow the [shared testing strategy](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/testing.md#testing-across-the-projects).
Test helper commands, paths, readiness checks and the handoff to Core. Keep one
shared native sample journey; do not duplicate Core's validation suite. Studio
downloads include the user-facing setup and sample check, not maintainer tests.

Use plausible fictional sample records for notice development. Keep deliberately
invalid data in test fixtures. Do not commit real client data or private assets.

Documentation describes current behavior; Git history records how it changed.
Keep pull request descriptions short and plain, focused on rationale and the
result for users. Omit agent attribution and detailed verification logs.

Studio copies an allowlisted scaffold from a pinned Template commit. Make setup
and helper changes here, then refresh Studio's snapshot and provenance through
its documented command. Do not hand-edit the copied scaffold in Studio.

Prefer clear, direct authoring and abstractions that earn their complexity. Follow
Core's [authoring principles](https://github.com/WDGPH/ImmuKnow/blob/main/docs/developer_guide/documentation.md#template-authoring-principles).
