from pathlib import Path

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
