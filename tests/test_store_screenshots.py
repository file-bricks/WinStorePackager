from pathlib import Path

import pytest
from PIL import Image, ImageStat

import generate_store_screenshots as screenshots


def test_store_screenshot_generator_outputs_four_1920x1080_pngs(tmp_path: Path):
    project_root = Path(__file__).resolve().parent.parent

    paths = screenshots.build_store_screenshot_set(project_root, tmp_path)

    assert [path.name for path in paths] == list(screenshots.SCREENSHOT_FILES)
    for path in paths:
        assert path.is_file()
        with Image.open(path) as image:
            assert image.format == "PNG"
            assert image.size == screenshots.CANVAS_SIZE
            stats = ImageStat.Stat(image.convert("L"))
            assert stats.stddev[0] > 8, f"{path.name} looks blank"


@pytest.mark.parametrize("count", [3, 5])
def test_store_screenshots_reject_mismatched_frame_count(tmp_path, monkeypatch, count):
    monkeypatch.setattr(screenshots, "SCREENSHOT_FILES", tuple(f"{i}.png" for i in range(count)))
    monkeypatch.setattr(screenshots, "_load_package", lambda *args: {})
    for name in ("_load_ui_screenshot", "_load_icon", "_main_window_frame",
                 "_store_fields_frame", "_icon_generation_frame", "_workflow_frame"):
        monkeypatch.setattr(screenshots, name, lambda *args: object())

    with pytest.raises(ValueError):
        screenshots.build_store_screenshot_set(tmp_path, tmp_path)
    assert not list(tmp_path.glob("*.png"))
