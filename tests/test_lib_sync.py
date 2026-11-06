"""Library synchronization uses the executable's exported Typst resources."""

import pytest

import sync_lib
from project import LIBRARY


def test_missing_library_is_generated_and_changes_require_explicit_refresh(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()
    sync_lib.ensure_library(templates)
    original = sync_lib.library_files(templates / LIBRARY)
    changed = templates / LIBRARY / "lib.typ"
    changed.write_text("// local change\n")
    (templates / LIBRARY / "extra.typ").write_text("")
    with pytest.raises(ValueError, match="differs"):
        sync_lib.ensure_library(templates)
    assert changed.read_text() == "// local change\n"
    sync_lib.ensure_library(templates, replace=True)
    assert sync_lib.library_files(templates / LIBRARY) == original
    assert [path.name for path in tmp_path.iterdir()] == ["templates"]


def test_missing_library_does_not_follow_a_linked_parent(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (templates / "lib").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="linked"):
        sync_lib.ensure_library(templates)
    assert not list(outside.iterdir())


def test_linked_file_in_existing_library_is_rejected(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()
    sync_lib.ensure_library(templates)
    (templates / LIBRARY / "link.typ").symlink_to(tmp_path / "missing")
    with pytest.raises(ValueError, match="linked"):
        sync_lib.ensure_library(templates, replace=True)
