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
    monkeypatch.setattr(sync_lib, "ROOT", tmp_path)
    monkeypatch.setattr(sync_lib, "TEMPLATES_DIR", templates)
    assert sync_lib.main() == 0
    verify_components(templates)
    assert [path.name for path in tmp_path.iterdir()] == ["templates"]
