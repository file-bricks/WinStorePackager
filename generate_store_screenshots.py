from __future__ import annotations

import json
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

CANVAS_SIZE = (1920, 1080)
SCREENSHOT_FILES = (
    "01-main-window.png",
    "02-store-fields.png",
    "03-icon-generation.png",
    "04-msix-wack-workflow.png",
)

BG = (246, 248, 251)
CARD = (255, 255, 255)
INK = (29, 34, 43)
MUTED = (91, 101, 116)
BLUE = (0, 120, 212)
GREEN = (16, 124, 16)
ORANGE = (202, 95, 0)
LINE = (213, 220, 229)


def build_store_screenshot_set(
    project_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> list[Path]:
    root = Path(project_root or Path(__file__).resolve().parent).resolve(strict=False)
    out = Path(output_dir or root / "releases" / "windowsstore" / "screenshots")
    out.mkdir(parents=True, exist_ok=True)

    package = _load_package(root / "store_package.json")
    product = str(package.get("app_name") or "WinStorePackager")
    ui = _load_ui_screenshot(root)
    icon = _load_icon(root)

    frames = [
        _main_window_frame(product, ui, icon),
        _store_fields_frame(product, package, ui, icon),
        _icon_generation_frame(product, root, icon),
        _workflow_frame(product, ui, icon),
    ]

    paths: list[Path] = []
    for name, image in zip(SCREENSHOT_FILES, frames, strict=True):
        path = out / name
        image.save(path, format="PNG", optimize=True)
        paths.append(path)
    return paths


def _main_window_frame(product: str, ui: Image.Image, icon: Image.Image) -> Image.Image:
    canvas = _canvas()
    draw = ImageDraw.Draw(canvas)
    _header(canvas, draw, icon, product, "Prepare Python desktop apps for Microsoft Store packaging")

    screenshot = ImageOps.contain(ui, (1390, 760), Image.Resampling.LANCZOS)
    _paste_card(canvas, screenshot, (90, 220), title="Desktop workflow")

    _card(draw, (1130, 220, 1830, 838))
    _section_title(draw, "What this screen shows", (1170, 260))
    bullets = [
        "App identity, version, package name",
        "Store-safe Publisher placeholder",
        "Project, icon, source, and output paths",
        "README, license, and description inputs",
    ]
    y = 340
    for bullet in bullets:
        y = _bullet(draw, bullet, (1170, y), width=560, color=BLUE)
    _note(
        draw,
        "Demo data only. No Partner Center ID, certificate path, password, or private project path is shown.",
        (1170, 650),
        560,
        height=160,
    )
    return canvas


def _store_fields_frame(
    product: str,
    package: dict[str, object],
    ui: Image.Image,
    icon: Image.Image,
) -> Image.Image:
    canvas = _canvas()
    draw = ImageDraw.Draw(canvas)
    _header(canvas, draw, icon, product, "Review Store metadata before MSIX build and Partner Center submission")

    _card(draw, (90, 210, 820, 1000))
    _section_title(draw, "Store metadata profile", (130, 250))
    rows = [
        ("App name", str(package.get("app_name", product))),
        ("Identity", str(package.get("identity_name", "YourPublisher.WinStorePackager"))),
        ("Version", str(package.get("version", "2.3.0.0"))),
        ("Category", str(package.get("category", "Developer Tools"))),
        ("Age rating", str(package.get("age_rating", "3+"))),
        ("Capabilities", str(package.get("capabilities", "internetClient,runFullTrust"))),
        ("Executable", str(package.get("executable", "WinStorePackager.exe"))),
    ]
    y = 330
    for label, value in rows:
        y = _field_row(draw, label, value, (130, y), width=620)

    _card(draw, (890, 210, 1830, 1000))
    _section_title(draw, "Privacy-safe listing checklist", (930, 250))
    checks = [
        "Privacy URL points to the public repository policy",
        "Support URL points to GitHub Issues",
        "Publisher DN stays a placeholder until Partner Center entry",
        "Generated profile excludes SDK paths, certificates, and passwords",
    ]
    y = 330
    for item in checks:
        y = _check(draw, item, (930, y))
    preview = ImageOps.contain(ui, (520, 190), Image.Resampling.LANCZOS)
    _paste_card(canvas, preview, (930, 690), title="Manifest source data")
    return canvas


def _icon_generation_frame(product: str, root: Path, icon: Image.Image) -> Image.Image:
    canvas = _canvas()
    draw = ImageDraw.Draw(canvas)
    _header(canvas, draw, icon, product, "Generate Microsoft Store asset sizes from one source icon")

    _card(draw, (90, 205, 720, 870))
    _section_title(draw, "Source icon", (130, 250))
    large_icon = ImageOps.contain(icon, (360, 360), Image.Resampling.LANCZOS)
    canvas.paste(large_icon, (225, 330), large_icon if large_icon.mode == "RGBA" else None)
    _note(draw, "The generator keeps Store assets deterministic and rebuildable for every submission.", (145, 735), 520)

    _card(draw, (790, 205, 1830, 870))
    _section_title(draw, "Store asset outputs", (830, 250))
    assets = [
        ("Square44x44Logo.png", "44 x 44"),
        ("Square150x150Logo.png", "150 x 150"),
        ("Square310x310Logo.png", "310 x 310"),
        ("Wide310x150Logo.png", "310 x 150"),
    ]
    x, y = 850, 340
    for index, (filename, label) in enumerate(assets):
        asset = _load_asset(root / "store_assets" / filename, icon)
        box_x = x + (index % 2) * 460
        box_y = y + (index // 2) * 240
        _mini_asset_card(canvas, draw, asset, filename, label, (box_x, box_y))
    _note(draw, "All screenshots use neutral demo content and avoid local private paths.", (850, 800), 740)
    return canvas


def _workflow_frame(product: str, ui: Image.Image, icon: Image.Image) -> Image.Image:
    canvas = _canvas()
    draw = ImageDraw.Draw(canvas)
    _header(canvas, draw, icon, product, "Dogfood the Windows Store release workflow")

    screenshot = ImageOps.contain(ui, (780, 560), Image.Resampling.LANCZOS)
    _paste_card(canvas, screenshot, (90, 270), title="WinStorePackager prepares itself")

    _card(draw, (950, 245, 1830, 840))
    _section_title(draw, "Release gate sequence", (990, 285))
    steps = [
        ("1", "Build EXE", "Create dist/WinStorePackager.exe outside OneDrive build roots."),
        ("2", "Generate manifest and assets", "Use Store metadata plus tracked icon assets."),
        ("3", "Build and sign MSIX", "Requires Windows SDK and local certificate material."),
        ("4", "Run WACK", "Elevated Windows App Certification Kit run writes the final report."),
    ]
    y = 360
    for number, title, detail in steps:
        y = _step(draw, number, title, detail, (995, y), width=760)
    _note(draw, "This screenshot set completes the non-admin listing artifact. WACK and Partner Center remain explicit external gates.", (990, 760), 760)
    return canvas


def _canvas() -> Image.Image:
    image = Image.new("RGB", CANVAS_SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, CANVAS_SIZE[0], 150), fill=(31, 45, 61))
    draw.rectangle((0, 150, CANVAS_SIZE[0], 154), fill=BLUE)
    return image


def _load_package(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_ui_screenshot(root: Path) -> Image.Image:
    image = Image.open(root / "README" / "screenshots" / "main.png").convert("RGB")
    width, height = image.size
    # The source capture includes the Windows taskbar. Keep the application window only.
    crop_bottom = max(1, height - 46)
    return image.crop((0, 0, width, crop_bottom))


def _load_icon(root: Path) -> Image.Image:
    for candidate in ("WinStorePackager.png", "WinStorePackager.ico", "WinstorePackager_icon.jpg"):
        path = root / candidate
        if path.exists():
            return Image.open(path).convert("RGBA")
    return Image.new("RGBA", (512, 512), (0, 120, 212, 255))


def _load_asset(path: Path, fallback: Image.Image) -> Image.Image:
    if path.exists():
        return Image.open(path).convert("RGBA")
    return fallback.copy()


def _header(canvas: Image.Image, draw: ImageDraw.ImageDraw, icon: Image.Image, product: str, subtitle: str) -> None:
    icon_small = ImageOps.contain(icon, (76, 76), Image.Resampling.LANCZOS)
    canvas.paste(icon_small, (90, 37), icon_small if icon_small.mode == "RGBA" else None)
    draw.text((190, 35), product, font=_font(48, bold=True), fill=(255, 255, 255))
    draw.text((192, 96), subtitle, font=_font(25), fill=(218, 230, 242))


def _paste_card(canvas: Image.Image, content: Image.Image, xy: tuple[int, int], *, title: str) -> None:
    x, y = xy
    width, height = content.size
    shadow = Image.new("RGBA", (width + 32, height + 96), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((16, 16, width + 16, height + 80), radius=26, fill=(0, 0, 0, 52))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(shadow, (x - 16, y - 16), shadow)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x, y, x + width, y + height + 58), radius=22, fill=CARD, outline=LINE, width=2)
    draw.text((x + 24, y + 18), title, font=_font(24, bold=True), fill=INK)
    canvas.paste(content, (x, y + 58))


def _card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=24, fill=CARD, outline=LINE, width=2)


def _section_title(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int]) -> None:
    draw.text(xy, text, font=_font(34, bold=True), fill=INK)


def _field_row(draw: ImageDraw.ImageDraw, label: str, value: str, xy: tuple[int, int], *, width: int) -> int:
    x, y = xy
    draw.text((x, y), label.upper(), font=_font(17, bold=True), fill=MUTED)
    draw.rounded_rectangle((x, y + 30, x + width, y + 78), radius=10, fill=(247, 249, 252), outline=LINE)
    draw.text((x + 18, y + 42), _ellipsize(value, 54), font=_font(23), fill=INK)
    return y + 95


def _bullet(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    *,
    width: int,
    color: tuple[int, int, int],
) -> int:
    x, y = xy
    draw.ellipse((x, y + 8, x + 14, y + 22), fill=color)
    return _wrapped(draw, text, (x + 28, y), width, font=_font(23), fill=INK, line_gap=7) + 24


def _check(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int]) -> int:
    x, y = xy
    draw.rounded_rectangle((x, y + 2, x + 32, y + 34), radius=8, fill=(226, 246, 230), outline=(174, 222, 184))
    draw.line((x + 8, y + 19, x + 15, y + 27, x + 26, y + 10), fill=GREEN, width=4)
    return _wrapped(draw, text, (x + 50, y), 760, font=_font(25), fill=INK, line_gap=8) + 26


def _note(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, *, height: int = 118) -> None:
    x, y = xy
    draw.rounded_rectangle((x, y, x + width, y + height), radius=16, fill=(255, 250, 232), outline=(241, 209, 140))
    _wrapped(draw, text, (x + 20, y + 20), width - 40, font=_font(20), fill=(94, 69, 12), line_gap=6)


def _mini_asset_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    asset: Image.Image,
    filename: str,
    label: str,
    xy: tuple[int, int],
) -> None:
    x, y = xy
    draw.rounded_rectangle((x, y, x + 390, y + 180), radius=18, fill=(247, 249, 252), outline=LINE)
    preview = ImageOps.contain(asset, (112, 112), Image.Resampling.LANCZOS)
    px = x + 30 + (112 - preview.width) // 2
    py = y + 34 + (112 - preview.height) // 2
    canvas.paste(preview, (px, py), preview if preview.mode == "RGBA" else None)
    draw.text((x + 170, y + 42), filename, font=_font(21, bold=True), fill=INK)
    draw.text((x + 170, y + 82), label, font=_font(24), fill=BLUE)
    draw.text((x + 170, y + 122), "tracked Store asset", font=_font(18), fill=MUTED)


def _step(
    draw: ImageDraw.ImageDraw,
    number: str,
    title: str,
    detail: str,
    xy: tuple[int, int],
    *,
    width: int,
) -> int:
    x, y = xy
    draw.ellipse((x, y, x + 50, y + 50), fill=BLUE)
    draw.text((x + 17, y + 10), number, font=_font(24, bold=True), fill=(255, 255, 255))
    draw.text((x + 75, y - 2), title, font=_font(26, bold=True), fill=INK)
    bottom = _wrapped(draw, detail, (x + 75, y + 34), width - 75, font=_font(20), fill=MUTED, line_gap=5)
    return bottom + 26


def _wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    width: int,
    *,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    line_gap: int,
) -> int:
    x, y = xy
    avg_char_width = max(8, int(draw.textlength("ABCDEFGHIJKLMNOPQRSTUVWXYZ", font=font) / 26))
    chars = max(12, width // avg_char_width)
    bottom = y
    for line in wrap(text, width=chars):
        draw.text((x, bottom), line, font=font, fill=fill)
        bbox = draw.textbbox((x, bottom), line, font=font)
        bottom = bbox[3] + line_gap
    return bottom


def _ellipsize(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "..."


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "seguisb.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    roots = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts")]
    for root in roots:
        for name in names:
            path = root / name
            if path.exists():
                return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> int:
    paths = build_store_screenshot_set()
    print("Generated Store screenshots:")
    for path in paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
