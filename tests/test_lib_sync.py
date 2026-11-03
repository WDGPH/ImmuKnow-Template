"""templates/lib/immuknow must match the installed ImmuKnow byte for byte."""

import shutil

import pytest
from immuknow.component_resources import verify_components

import sync_lib
from project import LIBRARY, TEMPLATES_DIR


def test_library_matches_installed_immuknow():
    verify_components(TEMPLATES_DIR)


def test_sync_replaces_a_changed_library(monkeypatch, tmp_path):
    templates = tmp_path / "templates"
    shutil.copytree(TEMPLATES_DIR / LIBRARY, templates / LIBRARY)
    (templates / LIBRARY / "lib.typ").write_text("// edited\n", encoding="utf-8")
    (templates / LIBRARY / "extra.typ").write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        verify_components(templates)
    monkeypatch.setattr(sync_lib, "TEMPLATES_DIR", templates)
    assert sync_lib.main() == 0
    verify_components(templates)
    assert [path.name for path in tmp_path.iterdir()] == ["templates"]


def test_missing_library_is_generated_and_changed_library_requires_explicit_refresh(
    tmp_path,
):
    templates = tmp_path / "templates"
    templates.mkdir()
    sync_lib.ensure_library(templates)
    verify_components(templates)
    changed = templates / LIBRARY / "lib.typ"
    changed.write_text("// local change\n")
    with pytest.raises(ValueError, match="differs"):
        sync_lib.ensure_library(templates)
    assert changed.read_text() == "// local change\n"
    sync_lib.ensure_library(templates, replace=True)
    verify_components(templates)


def test_missing_library_does_not_follow_a_linked_parent(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (templates / "lib").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="linked"):
        sync_lib.ensure_library(templates)
    assert not list(outside.iterdir())
