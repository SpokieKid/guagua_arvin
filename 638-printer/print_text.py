import argparse
import sys
import time
from printer_tool import (
    build_pos_raster_image_cmd, send_serial,
    _read_reply_bytes, _query_rt_status, _decode_status, _summarize_printer_health,
)

try:
    import serial as pyserial
except ImportError:
    pyserial = None


def _fix_argv():
    """argparse rejects values starting with '-'; pre-join -text <val> into --text=<val>."""
    argv = sys.argv[1:]
    fixed = []
    i = 0
    while i < len(argv):
        if argv[i] in ("-text", "--text") and i + 1 < len(argv):
            fixed.append(f"--text={argv[i + 1]}")
            i += 2
        else:
            fixed.append(argv[i])
            i += 1
    return fixed

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None

# 24x24 test bitmap: "我"
test_data = bytes([
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x1D,0x60,0x00,0xF1,0x10,0x00,0x11,
    0x00,0x00,0xFF,0xF8,0x00,0x11,0x00,0x00,0x11,0x10,0x00,0x1F,0x20,0x00,0xF0,0xC0,
    0x00,0x10,0x88,0x00,0x13,0x88,0x00,0x16,0x48,0x00,0xF0,0x30,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
])


MAX_WIDTH_58MM = 384
MAX_WIDTH_80MM = 576


def _load_font(size):
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


def _image_to_bitmap(img):
    w, h = img.size
    row_bytes = (w + 7) // 8
    data = bytearray(row_bytes * h)
    pixels = img.load()
    for row in range(h):
        for col in range(w):
            if pixels[col, row] == 0:
                data[row * row_bytes + col // 8] |= 1 << (7 - col % 8)
    return bytes(data)


def _measure_char(ch, font, draw):
    bbox = draw.textbbox((0, 0), ch, font=font)
    return bbox[2] - bbox[0]


def text_to_line_bitmaps(text, size, max_width):
    """Render text into horizontal line images, wrapping at max_width.
    Returns list of (width, height, bitmap_bytes)."""
    if Image is None:
        raise RuntimeError("Pillow required for -text. Install: pip install Pillow")
    font = _load_font(size)
    tmp = Image.new("1", (1, 1), 1)
    tmp_draw = ImageDraw.Draw(tmp)
    char_widths = [_measure_char(ch, font, tmp_draw) for ch in text]

    lines_text = []
    i = 0
    while i < len(text):
        line_w = 0
        start = i
        while i < len(text):
            cw = char_widths[i]
            if line_w + cw > max_width and i > start:
                break
            line_w += cw
            i += 1
        lines_text.append(text[start:i])

    results = []
    for line in lines_text:
        bbox = tmp_draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        img = Image.new("1", (line_w, size), 1)
        draw = ImageDraw.Draw(img)
        y = (size - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text((-bbox[0], y), line, font=font, fill=0)
        results.append((line_w, size, _image_to_bitmap(img)))
    return results


BAND_HEIGHT = 8


def _split_raster_bands(width, height, bmp):
    """Split a raster bitmap into list of per-band GS v 0 commands."""
    row_bytes = (width + 7) // 8
    bands = []
    for y in range(0, height, BAND_HEIGHT):
        bh = min(BAND_HEIGHT, height - y)
        band_data = bmp[y * row_bytes : (y + bh) * row_bytes]
        bands.append(build_pos_raster_image_cmd(width, bh, band_data, 0))
    return bands


def main():
    """脚本入口：解析参数，生成文字位图，并通过串口发送到打印机。"""
    parser = argparse.ArgumentParser(description="Print text or test bitmap to 638 printer")
    parser.add_argument("--text", type=str, default=None, help="要打印的文字；为空时打印内置测试字模")
    parser.add_argument("-s", type=int, default=24, help="字形高度（像素），越大字越高，默认 24")
    parser.add_argument("-d", type=int, default=None,
                        help="打印浓度 0~15，值越大越黑；使用 DC2 # n 指令")
    parser.add_argument("-w", type=int, default=384,
                        help="最大打印宽度（点），58mm 常用 384，80mm 常用 576")
    parser.add_argument("-f", type=int, default=3,
                        help="打印完成后额外走纸行数，默认 3")
    parser.add_argument("--port", type=str, default="/dev/cu.usbserial-0001",
                        help="串口设备路径，例如 /dev/cu.usbserial-0001")
    parser.add_argument("--baudrate", type=int, default=115200,
                        help="串口波特率，默认 115200")
    args = parser.parse_args(_fix_argv())

    density_cmd = b""
    if args.d is not None:
        if not 0 <= args.d <= 15:
            print("error: -d must be 0~15")
            return
        density_cmd = bytes([0x12, 0x23, args.d])

    if args.text:
        lines = text_to_line_bitmaps(args.text, args.s, args.w)
        bands = []
        for w, h, bmp in lines:
            bands += _split_raster_bands(w, h, bmp)
    else:
        bands = _split_raster_bands(24, 24, test_data)

    port = args.port
    baudrate = args.baudrate
    band_delay_s = 0.06

    if pyserial is None:
        raise RuntimeError("pyserial is required. pip install pyserial")

    sent = 0
    with pyserial.Serial(port=port, baudrate=baudrate, timeout=3,
                         write_timeout=30, xonxoff=False, rtscts=False, dsrdtr=False) as ser:
        init_cmd = b"\x1B\x40" + density_cmd
        ser.write(init_cmd)
        ser.flush()
        sent += len(init_cmd)

        for band_cmd in bands:
            ser.write(band_cmd)
            ser.flush()
            sent += len(band_cmd)
            time.sleep(band_delay_s)

        feed_cmd = b"\n" * args.f
        ser.write(feed_cmd)
        ser.flush()
        sent += len(feed_cmd)

        reply = _read_reply_bytes(ser, max_wait_s=0.5, quiet_wait_s=0.12)

        time.sleep(0.2)
        status_raw = {}
        status_decoded = {}
        for n in (1, 2, 3, 4):
            val = _query_rt_status(ser, n=n, timeout_s=0.5)
            status_raw[n] = val
            if val is not None:
                status_decoded[n] = _decode_status(status_n=n, val=val)
        healthy, issues = _summarize_printer_health(status_decoded) if status_decoded else (None, [])

    print("sent", sent, "reply_len", len(reply),
          "status", status_raw, "healthy", healthy)


if __name__ == "__main__":
    main()
