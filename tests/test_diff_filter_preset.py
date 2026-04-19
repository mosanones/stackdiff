"""Tests for diff_filter_preset module."""
import pytest
from stackdiff.diff_filter_preset import (
    FilterPreset,
    load_preset,
    list_presets,
    save_preset,
    BUILTIN_PRESETS,
)


@pytest.fixture
def preset_dir(tmp_path):
    return str(tmp_path / "presets")


def test_load_builtin_preset():
    preset = load_preset("secrets")
    assert preset.name == "secrets"
    assert any("password" in p for p in preset.include)


def test_load_all_builtins():
    for name in BUILTIN_PRESETS:
        p = load_preset(name)
        assert p.name == name
        assert p.description


def test_load_missing_raises():
    with pytest.raises(KeyError, match="notapreset"):
        load_preset("notapreset")


def test_list_presets_includes_builtins():
    presets = list_presets()
    names = [p.name for p in presets]
    for name in BUILTIN_PRESETS:
        assert name in names


def test_save_and_load_custom_preset(preset_dir):
    custom = FilterPreset(
        name="custom",
        description="My custom preset",
        include=["*db*"],
        exclude=["*test*"],
    )
    save_preset(custom, preset_dir)
    loaded = load_preset("custom", presets_dir=preset_dir)
    assert loaded.name == "custom"
    assert loaded.include == ["*db*"]
    assert loaded.exclude == ["*test*"]


def test_custom_preset_overrides_builtin_name(preset_dir):
    override = FilterPreset(
        name="secrets",
        description="Override secrets",
        include=["*my_secret*"],
        exclude=[],
    )
    save_preset(override, preset_dir)
    loaded = load_preset("secrets", presets_dir=preset_dir)
    assert loaded.include == ["*my_secret*"]


def test_list_presets_includes_custom(preset_dir):
    custom = FilterPreset(name="infra2", description="infra2", include=["*"], exclude=[])
    save_preset(custom, preset_dir)
    names = [p.name for p in list_presets(presets_dir=preset_dir)]
    assert "infra2" in names


def test_preset_as_dict():
    p = load_preset("endpoints")
    d = p.as_dict()
    assert d["name"] == "endpoints"
    assert "include" in d
    assert "exclude" in d
    assert "description" in d


def test_save_creates_file(preset_dir):
    import os
    p = FilterPreset(name="x", description="x", include=[], exclude=[])
    path = save_preset(p, preset_dir)
    assert os.path.exists(path)
