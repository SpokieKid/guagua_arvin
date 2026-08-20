import base64

from printer_tool import build_pos_feed_cmd, build_pos_init_cmd, build_pos_raster_image_cmd

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None


MAX_WIDTH_58MM = 384
MAX_WIDTH_80MM = 576
BAND_HEIGHT = 8


# 24x24 测试字模：我
TEST_BITMAP_DATA = bytes([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1D, 0x60, 0x00, 0xF1, 0x10, 0x00, 0x11,
    0x00, 0x00, 0xFF, 0xF8, 0x00, 0x11, 0x00, 0x00, 0x11, 0x10, 0x00, 0x1F, 0x20, 0x00, 0xF0, 0xC0,
    0x00, 0x10, 0x88, 0x00, 0x13, 0x88, 0x00, 0x16, 0x48, 0x00, 0xF0, 0x30, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])


def build_density_cmd(density: int | None) -> bytes:
    if density is None:
        return b""
    if not 0 <= density <= 15:
        raise ValueError("density 必须在 0~15 之间")
    return bytes([0x12, 0x23, density])


def _load_font(size: int):
    if ImageFont is None:
        raise RuntimeError("缺少 Pillow，先执行: pip install Pillow")

    font_size = int(size * 0.88)
    for fp in [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]:
        try:
            return ImageFont.truetype(fp, font_size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _image_to_bitmap(img) -> bytes:
    width, height = img.size
    row_bytes = (width + 7) // 8
    data = bytearray(row_bytes * height)
    pixels = img.load()
    for row in range(height):
        for col in range(width):
            if pixels[col, row] == 0:
                data[row * row_bytes + col // 8] |= 1 << (7 - col % 8)
    return bytes(data)


def _measure_char(ch: str, font, draw) -> int:
    bbox = draw.textbbox((0, 0), ch, font=font)
    return bbox[2] - bbox[0]


def text_to_line_bitmaps(text: str, size: int, max_width: int) -> list[tuple[int, int, bytes]]:
    if Image is None or ImageDraw is None:
        raise RuntimeError("缺少 Pillow，先执行: pip install Pillow")

    font = _load_font(size)
    tmp = Image.new("1", (1, 1), 1)
    tmp_draw = ImageDraw.Draw(tmp)
    char_widths = [_measure_char(ch, font, tmp_draw) for ch in text]

    lines_text: list[str] = []
    index = 0
    while index < len(text):
        line_width = 0
        start = index
        while index < len(text):
            char_width = char_widths[index]
            if line_width + char_width > max_width and index > start:
                break
            line_width += char_width
            index += 1
        lines_text.append(text[start:index])

    results: list[tuple[int, int, bytes]] = []
    for line in lines_text:
        bbox = tmp_draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        img = Image.new("1", (line_width, size), 1)
        draw = ImageDraw.Draw(img)
        baseline_y = (size - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text((-bbox[0], baseline_y), line, font=font, fill=0)
        results.append((line_width, size, _image_to_bitmap(img)))
    return results


def split_raster_bands(width: int, height: int, bitmap: bytes) -> list[bytes]:
    row_bytes = (width + 7) // 8
    bands: list[bytes] = []
    for y in range(0, height, BAND_HEIGHT):
        band_height = min(BAND_HEIGHT, height - y)
        band_data = bitmap[y * row_bytes : (y + band_height) * row_bytes]
        bands.append(build_pos_raster_image_cmd(width, band_height, band_data, 0))
    return bands


def build_text_body(text: str | None, size: int, max_width: int) -> bytes:
    body = bytearray()
    if text:
        for width, height, bitmap in text_to_line_bitmaps(text, size, max_width):
            for band in split_raster_bands(width, height, bitmap):
                body += band
    else:
        for band in split_raster_bands(24, 24, TEST_BITMAP_DATA):
            body += band
    return bytes(body)


def build_text_payload(text: str | None, size: int, max_width: int, feed_lines: int, density: int | None) -> bytes:
    payload = bytearray()
    payload += build_pos_init_cmd()
    payload += build_density_cmd(density)
    payload += build_text_body(text=text, size=size, max_width=max_width)
    payload += build_pos_feed_cmd(feed_lines)
    return bytes(payload)


def payload_to_base64(payload: bytes) -> str:
    return base64.b64encode(payload).decode("ascii")

