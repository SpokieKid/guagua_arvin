
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import signal
import time
from typing import Any, Optional

from PIL import Image, ImageEnhance

from printer_tool import (
    DEFAULT_BAUDRATE,
    DEFAULT_PORT,
    _decode_status,
    _query_rt_status,
    _read_reply_bytes,
    _summarize_printer_health,
    build_pos_raster_image_cmd,
)

try:
    import serial as pyserial
except ImportError:
    pyserial = None

try:
    from escpos.printer import Serial as EscposSerial  # type: ignore
except Exception:
    EscposSerial = None


MAX_WIDTH_58MM = 384
MAX_WIDTH_80MM = 576
BAND_HEIGHT = 96
SPEED_MODE_TO_CHUNK_DELAY_MS = {
    "quality": 12.0,
    "balanced": 6.0,
    "fast": 0.0,
}
DITHER_NONE = "none"
DITHER_ORDERED = "ordered"
DITHER_SIERRA = "sierra"
# 兼容旧参数：历史版本用 floyd，现已统一迁移为 sierra。
DITHER_FLOYD_LEGACY = "floyd"
SEND_MODE_BURST = "burst"
SEND_MODE_PACED = "paced"
SMOOTH_MAX_CHUNK_SIZE = 128
DEFAULT_DIAG_RX_WAIT_MS = 25.0
DEFAULT_DIAG_RX_QUIET_MS = 8.0
DEFAULT_DIAG_STATUS_TIMEOUT_MS = 180.0
# 打印自检页：按规格书示例发送 ESC @ + DC2 T（1B 40 12 54）。
SELF_TEST_PAGE_CMD = b"\x1B\x40\x12\x54"
_SIGINT_REQUESTED = False


def _clamp_u8(value: int) -> int:
    """把任意整数限制到无符号字节范围 [0, 255]。"""
    return max(0, min(255, int(value)))


def _fit_width(gray: Image.Image, target_width: int, upscale: bool) -> Image.Image:
    """按目标宽度等比缩放图片。"""
    src_w, src_h = gray.size
    if src_w == target_width:
        return gray
    if src_w < target_width and not upscale:
        return gray
    ratio = target_width / float(src_w)
    new_h = max(1, int(round(src_h * ratio)))
    return gray.resize((target_width, new_h), Image.Resampling.LANCZOS)


def _quantize_gray(gray: Image.Image, levels: int) -> Image.Image:
    """在最终二值化前先做灰度量化（如 4/8 级）。"""
    if levels <= 1:
        return gray
    step = 255.0 / float(levels - 1)
    lut = []
    for i in range(256):
        q = int(round(i / step))
        lut.append(_clamp_u8(round(q * step)))
    return gray.point(lut)


def _binary_threshold(gray: Image.Image, threshold: int) -> Image.Image:
    """不使用抖动，直接阈值二值化。"""
    th = _clamp_u8(threshold)
    return gray.point(lambda p: 0 if p < th else 255, mode="1")


def _ordered_dither_to_1bit(gray: Image.Image, threshold: int) -> Image.Image:
    """Bayer 有序抖动，速度快、稳定性高。"""
    # 8x8 Bayer 矩阵，值域映射到 [0..63]
    bayer8 = [
        [0, 48, 12, 60, 3, 51, 15, 63],
        [32, 16, 44, 28, 35, 19, 47, 31],
        [8, 56, 4, 52, 11, 59, 7, 55],
        [40, 24, 36, 20, 43, 27, 39, 23],
        [2, 50, 14, 62, 1, 49, 13, 61],
        [34, 18, 46, 30, 33, 17, 45, 29],
        [10, 58, 6, 54, 9, 57, 5, 53],
        [42, 26, 38, 22, 41, 25, 37, 21],
    ]
    w, h = gray.size
    src = gray.load()
    out = Image.new("1", (w, h), 1)
    dst = out.load()
    base = _clamp_u8(threshold)
    for y in range(h):
        for x in range(w):
            delta = int((bayer8[y % 8][x % 8] - 31.5) * 2)  # 约 [-63..63]
            t = _clamp_u8(base + delta)
            dst[x, y] = 0 if src[x, y] < t else 1
    return out


def _sierra_lite_to_1bit(gray: Image.Image, threshold: int) -> Image.Image:
    """Sierra Lite 误差扩散抖动。

    与 ordered 相比，条纹更轻；与 Floyd 相比，计算更省且更稳。
    采用蛇形扫描（奇偶行方向相反）以降低方向性纹理。
    """
    w, h = gray.size
    buf = [float(px) for px in gray.tobytes()]
    out = Image.new("1", (w, h), 1)
    dst = out.load()
    th = float(_clamp_u8(threshold))

    for y in range(h):
        row = y * w
        next_row = (y + 1) * w
        if (y % 2) == 0:
            xs = range(w)
            for x in xs:
                idx = row + x
                old = buf[idx]
                new = 0.0 if old < th else 255.0
                dst[x, y] = 0 if new == 0.0 else 1
                err = old - new

                # Sierra Lite:
                # 当前行右侧 2/4；下一行左下 1/4；下一行正下 1/4。
                if x + 1 < w:
                    buf[idx + 1] += err * 0.5
                if y + 1 < h:
                    if x > 0:
                        buf[next_row + x - 1] += err * 0.25
                    buf[next_row + x] += err * 0.25
        else:
            xs = range(w - 1, -1, -1)
            for x in xs:
                idx = row + x
                old = buf[idx]
                new = 0.0 if old < th else 255.0
                dst[x, y] = 0 if new == 0.0 else 1
                err = old - new

                # 蛇形扫描镜像扩散方向。
                if x - 1 >= 0:
                    buf[idx - 1] += err * 0.5
                if y + 1 < h:
                    if x + 1 < w:
                        buf[next_row + x + 1] += err * 0.25
                    buf[next_row + x] += err * 0.25
    return out


def _apply_gamma(gray: Image.Image, gamma: float) -> Image.Image:
    """在灰度域做 gamma 校正。

    gamma > 1.0 通常能提亮暗部并保留更多细节。
    """
    if gamma <= 0:
        raise ValueError("gamma must be > 0")
    inv = 1.0 / gamma
    lut = [_clamp_u8(round(255.0 * ((i / 255.0) ** inv))) for i in range(256)]
    return gray.point(lut)


def _apply_contrast(gray: Image.Image, contrast: float) -> Image.Image:
    """调整灰度对比度。"""
    if contrast <= 0:
        raise ValueError("contrast must be > 0")
    if abs(contrast - 1.0) < 1e-9:
        return gray
    return ImageEnhance.Contrast(gray).enhance(contrast)


def preprocess_image(
    image_path: Path,
    target_width: int,
    upscale: bool,
    gray_depth: int,
    threshold: int,
    dither: str,
    invert: bool,
    gamma: float,
    contrast: float,
) -> Image.Image:
    """读取图片并转换成可打印的 1-bit 位图。

    流程：读取 -> 灰度化 -> 等比缩放 -> 灰度量化 ->
    gamma/contrast -> 抖动或阈值 -> 可选反相。
    """
    img = Image.open(image_path)
    gray = img.convert("L")
    gray = _fit_width(gray, target_width=target_width, upscale=upscale)
    gray = _quantize_gray(gray, levels=gray_depth)
    gray = _apply_gamma(gray, gamma=gamma)
    gray = _apply_contrast(gray, contrast=contrast)

    if dither == DITHER_ORDERED:
        bw = _ordered_dither_to_1bit(gray, threshold=threshold)
    elif dither == DITHER_SIERRA:
        bw = _sierra_lite_to_1bit(gray, threshold=threshold)
    elif dither == DITHER_FLOYD_LEGACY:
        # 兜底兼容：若外部绕过参数解析直接传入 floyd，仍按 sierra 执行。
        bw = _sierra_lite_to_1bit(gray, threshold=threshold)
    else:
        bw = _binary_threshold(gray, threshold=threshold)

    if invert:
        return bw.point(lambda p: 255 - p, mode="1")
    return bw


def image_to_raster_bytes(bw: Image.Image) -> bytes:
    """把 1-bit 图像打包为 ESC/POS 光栅字节（MSB first，1=黑点）。"""
    w, h = bw.size
    row_bytes = (w + 7) // 8
    pixels = bw.load()
    out = bytearray(row_bytes * h)
    for y in range(h):
        for x in range(w):
            # PIL '1' 模式：0=黑，255（或读取时的 1）=白
            if pixels[x, y] == 0:
                out[y * row_bytes + x // 8] |= 1 << (7 - (x % 8))
    return bytes(out)


def _build_heat_cmd(n1: Optional[int], n2: Optional[int], n3: Optional[int]) -> bytes:
    """构造 ESC 7 打印浓度/加热参数命令。"""
    if n1 is None and n2 is None and n3 is None:
        return b""
    if None in (n1, n2, n3):
        raise ValueError("heat params must be all set or all omitted: --heat-n1 --heat-n2 --heat-n3")
    for n in (n1, n2, n3):
        assert n is not None
        if not 0 <= n <= 255:
            raise ValueError("heat params must be in range 0..255")
    return bytes((0x1B, 0x37, n1, n2, n3))  # ESC 7 n1 n2 n3


def _choose_stable_band_height(height: int, requested: int, min_tail: int = 24) -> int:
    """自动选择更稳定的条带高度，尽量避免过短尾段。"""
    if requested <= 0:
        raise ValueError("requested band height must be positive")
    if height <= requested:
        return requested

    tail = height % requested
    if tail == 0 or tail >= min_tail:
        return requested

    # 在 [32, requested] 范围内找“尾段足够大”的候选值，优先接近 requested。
    best = requested
    best_gap = 10**9
    for cand in range(max(32, min_tail), requested + 1):
        t = height % cand
        if t == 0 or t >= min_tail:
            gap = abs(requested - cand)
            if gap < best_gap:
                best_gap = gap
                best = cand
    return best


def _build_raster_bands(
    width: int,
    height: int,
    raster: bytes,
    band_height: int,
    pad_last_band: bool,
) -> list[bytes]:
    """按垂直条带构建 GS v 0 图像命令。

    某些固件对“最后一段高度过短”比较敏感，开启 pad_last_band 后会在
    尾段补白到固定高度，降低底部断层概率。
    """
    row_bytes = (width + 7) // 8
    bands: list[bytes] = []
    y = 0
    while y < height:
        src_h = min(band_height, height - y)
        bh = src_h
        seg = raster[y * row_bytes : (y + src_h) * row_bytes]
        if pad_last_band and src_h < band_height:
            seg += b"\x00" * ((band_height - src_h) * row_bytes)
            bh = band_height
        bands.append(build_pos_raster_image_cmd(width=width, height=bh, data=seg, mode=0))
        y += src_h
    return bands


def _sigint_handler(_signum: int, _frame) -> None:
    """捕获 Ctrl+C：仅打标记，避免在信号处理器里做复杂 I/O。"""
    global _SIGINT_REQUESTED
    _SIGINT_REQUESTED = True


def _check_interrupt_requested() -> None:
    """若收到 Ctrl+C 请求，则抛出 KeyboardInterrupt。"""
    if _SIGINT_REQUESTED:
        raise KeyboardInterrupt("用户中断打印")


def _sleep_interruptible(seconds: float) -> None:
    """可中断睡眠：分片睡眠以便快速响应 Ctrl+C。"""
    if seconds <= 0:
        return
    end = time.monotonic() + seconds
    while True:
        _check_interrupt_requested()
        now = time.monotonic()
        if now >= end:
            return
        time.sleep(min(0.05, end - now))


class _SmoothRateLimiter:
    """恒速发送节流器。

    目标：把“突发写入 + 空档等待”改为更均匀的字节流发送节奏，
    降低出纸“顿挫感”和条带边界冲击。
    """

    def __init__(self, target_bps: float) -> None:
        if target_bps <= 0:
            raise ValueError("target_bps must be > 0")
        self._target_bps = float(target_bps)
        self._start_ts = time.monotonic()
        self._sent_bytes = 0

    def on_bytes_sent(self, written: int) -> None:
        """记录本次已发送字节，并按目标带宽补偿睡眠。"""
        if written <= 0:
            return
        self._sent_bytes += int(written)
        expect_elapsed = self._sent_bytes / self._target_bps
        wake_ts = self._start_ts + expect_elapsed
        sleep_s = wake_ts - time.monotonic()
        if sleep_s > 0:
            _sleep_interruptible(sleep_s)


def _resolve_effective_chunk_size(chunk_size: int, send_mode: str) -> int:
    """解析实际 chunk 大小。

    paced 模式会限制单次突发写入上限，降低“打满缓存再停顿”的观感；
    burst 模式保持原始 chunk 大小，追求连续吞吐。
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if send_mode not in (SEND_MODE_BURST, SEND_MODE_PACED):
        raise ValueError(f"unsupported send_mode: {send_mode}")
    if send_mode == SEND_MODE_BURST:
        return chunk_size
    return max(16, min(chunk_size, SMOOTH_MAX_CHUNK_SIZE))


def _write_interruptible(
    ser: "pyserial.Serial",
    payload: bytes,
    chunk_size: int,
    chunk_delay_s: float,
    smooth_limiter: Optional[_SmoothRateLimiter] = None,
) -> int:
    """按 chunk 写串口，chunk 之间可被 Ctrl+C 立即打断。"""
    sent = 0
    while sent < len(payload):
        _check_interrupt_requested()
        end = min(sent + chunk_size, len(payload))
        written = ser.write(payload[sent:end])
        if not written:
            raise RuntimeError("串口写入返回 0 字节")
        sent += written
        if smooth_limiter is not None:
            smooth_limiter.on_bytes_sent(written)
        if sent < len(payload):
            _sleep_interruptible(chunk_delay_s)
    return sent


def _bytes_hex_preview(data: bytes, max_bytes: int = 256) -> dict[str, Any]:
    """把原始字节压缩成可读摘要，避免诊断日志过大。"""
    head = data[:max_bytes]
    return {
        "len": len(data),
        "hex": head.hex(" "),
        "truncated": len(data) > max_bytes,
    }


def _diag_append_event(diag: Optional[dict[str, Any]], event: str, **fields: Any) -> None:
    """向诊断数据追加一条事件。"""
    if diag is None:
        return
    events = diag.setdefault("events", [])
    assert isinstance(events, list)
    item = {
        "ts_monotonic": round(time.monotonic(), 6),
        "event": event,
    }
    item.update(fields)
    events.append(item)


def _diag_collect_status_snapshot(ser: "pyserial.Serial", timeout_s: float) -> dict[str, Any]:
    """主动查询 DLE EOT 1~4，并返回原始值和解析值。"""
    raw: dict[int, Optional[int]] = {}
    decoded: dict[int, dict[str, Any]] = {}
    for n in (1, 2, 3, 4):
        val = _query_rt_status(ser=ser, n=n, timeout_s=timeout_s)
        raw[n] = val
        if val is not None:
            decoded[n] = _decode_status(status_n=n, val=val)
    healthy = None
    issues: list[str] = []
    if decoded:
        healthy, issues = _summarize_printer_health(decoded)
    return {
        "raw": {str(k): v for k, v in raw.items()},
        "decoded": {str(k): v for k, v in decoded.items()},
        "healthy": healthy,
        "issues": issues,
    }


def _resolve_diag_file_path(diag_file: Optional[Path]) -> Path:
    """解析诊断文件路径。未指定时自动生成时间戳文件名。"""
    if diag_file is not None:
        return diag_file
    stamp = time.strftime("%Y%m%d_%H%M%S")
    return Path.cwd() / f"print_pic_diag_{stamp}.json"


def _write_diag_json(path: Path, payload: dict[str, Any]) -> Path:
    """把诊断结果写入 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def print_self_test_with_raw(
    port: str,
    baudrate: int,
    chunk_size: int,
    chunk_delay_ms: float,
    send_mode: str,
    target_bps: int,
    read_reply: bool,
    status_check: bool,
    diagnostic: bool,
    diag_payload: Optional[dict[str, Any]],
) -> dict:
    """RAW 后端打印自检页（DC2 T）。"""
    if pyserial is None:
        raise RuntimeError("缺少 pyserial，请先安装：pip install pyserial")

    global _SIGINT_REQUESTED
    _SIGINT_REQUESTED = False

    diag = diag_payload if diagnostic else None
    if diagnostic and diag is None:
        diag = {}
    if diag is not None:
        diag.setdefault("events", [])

    paced_send = send_mode == SEND_MODE_PACED
    effective_chunk_size = _resolve_effective_chunk_size(chunk_size, send_mode=send_mode)
    result: dict = {
        "sent_bytes": 0,
        "reply_bytes": b"",
        "status_raw": {},
        "status_decoded": {},
        "healthy": None,
        "issues": [],
        "interrupted": False,
        "effective_chunk_size": effective_chunk_size,
        "diag": diag,
    }

    chunk_delay_s = max(0.0, chunk_delay_ms / 1000.0)
    if paced_send:
        # paced 模式由恒速器接管节奏，避免再叠加固定 chunk 延时。
        chunk_delay_s = 0.0
    smooth_limiter = _SmoothRateLimiter(target_bps=target_bps) if paced_send else None
    prev_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _sigint_handler)
    _diag_append_event(
        diag,
        "self_test_begin",
        port=port,
        baudrate=baudrate,
        payload_hex=SELF_TEST_PAGE_CMD.hex(" "),
        chunk_size=chunk_size,
        effective_chunk_size=effective_chunk_size,
        chunk_delay_ms=chunk_delay_ms,
        send_mode=send_mode,
        paced_send=paced_send,
        target_bps=target_bps,
        read_reply=read_reply,
        status_check=status_check,
    )
    try:
        with pyserial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=pyserial.EIGHTBITS,
            parity=pyserial.PARITY_NONE,
            stopbits=pyserial.STOPBITS_ONE,
            timeout=3,
            write_timeout=30.0,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        ) as ser:
            _diag_append_event(diag, "serial_opened")
            try:
                result["sent_bytes"] += _write_interruptible(
                    ser=ser,
                    payload=SELF_TEST_PAGE_CMD,
                    chunk_size=effective_chunk_size,
                    chunk_delay_s=chunk_delay_s,
                    smooth_limiter=smooth_limiter,
                )
                _diag_append_event(
                    diag,
                    "self_test_cmd_sent",
                    payload_len=len(SELF_TEST_PAGE_CMD),
                    sent_bytes_total=result["sent_bytes"],
                )
            except KeyboardInterrupt:
                result["interrupted"] = True
                _diag_append_event(diag, "keyboard_interrupt")
                try:
                    ser.write(b"\x18\x1B\x40")  # CAN + ESC @
                    ser.flush()
                    _diag_append_event(diag, "interrupt_cancel_sent", payload_hex="18 1b 40")
                except Exception:
                    _diag_append_event(diag, "interrupt_cancel_failed")
                    pass
                return result

            ser.flush()
            _diag_append_event(diag, "serial_flushed")

            if read_reply:
                result["reply_bytes"] = _read_reply_bytes(ser=ser, max_wait_s=0.5, quiet_wait_s=0.12)
                if result["reply_bytes"]:
                    _diag_append_event(diag, "final_reply", rx=_bytes_hex_preview(result["reply_bytes"]))

            if status_check:
                time.sleep(0.2)
                raw: dict[int, Optional[int]] = {}
                decoded: dict[int, dict] = {}
                for n in (1, 2, 3, 4):
                    val = _query_rt_status(ser=ser, n=n, timeout_s=0.5)
                    raw[n] = val
                    if val is not None:
                        decoded[n] = _decode_status(status_n=n, val=val)
                result["status_raw"] = raw
                result["status_decoded"] = decoded
                if decoded:
                    healthy, issues = _summarize_printer_health(decoded)
                    result["healthy"] = healthy
                    result["issues"] = issues
                _diag_append_event(
                    diag,
                    "final_status_snapshot",
                    status_raw={str(k): v for k, v in raw.items()},
                    status_decoded={str(k): v for k, v in decoded.items()},
                    healthy=result["healthy"],
                    issues=result["issues"],
                )
    except Exception as exc:
        _diag_append_event(
            diag,
            "self_test_error",
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise
    finally:
        _diag_append_event(diag, "self_test_end", interrupted=result["interrupted"])
        signal.signal(signal.SIGINT, prev_sigint)
    return result


def print_with_raw(
    bw: Image.Image,
    port: str,
    baudrate: int,
    feed: int,
    band_height: int,
    heat_cmd: bytes,
    chunk_size: int,
    chunk_delay_ms: float,
    send_mode: str,
    target_bps: int,
    inter_band_gap_ms: float,
    tail_bands: int,
    tail_delay_ms: float,
    pad_last_band: bool,
    auto_band_height: bool,
    min_tail_rows: int,
    feed_mode: str,
    read_reply: bool,
    status_check: bool,
    diagnostic: bool,
    diag_passive_rx: bool,
    diag_active_status: bool,
    diag_snapshot_every_band: int,
    diag_rx_wait_ms: float,
    diag_rx_quiet_ms: float,
    diag_status_timeout_ms: float,
    diag_payload: Optional[dict[str, Any]],
) -> dict:
    """RAW 后端打印：同一串口会话逐条带发送 GS v 0，支持 Ctrl+C 中断与可选诊断。"""
    if pyserial is None:
        raise RuntimeError("缺少 pyserial，请先安装：pip install pyserial")

    global _SIGINT_REQUESTED
    _SIGINT_REQUESTED = False

    diag = diag_payload if diagnostic else None
    if diagnostic and diag is None:
        diag = {}
    if diag is not None:
        diag.setdefault("events", [])

    w, h = bw.size
    effective_band_height = band_height
    if auto_band_height:
        effective_band_height = _choose_stable_band_height(
            height=h,
            requested=band_height,
            min_tail=min_tail_rows,
        )

    raster = image_to_raster_bytes(bw)
    bands = _build_raster_bands(
        width=w,
        height=h,
        raster=raster,
        band_height=effective_band_height,
        pad_last_band=pad_last_band,
    )
    paced_send = send_mode == SEND_MODE_PACED
    chunk_delay_s = max(0.0, chunk_delay_ms / 1000.0)
    if paced_send:
        # paced 模式由恒速器接管节奏，避免再叠加固定 chunk 延时。
        chunk_delay_s = 0.0
    inter_band_gap_s = max(0.0, inter_band_gap_ms / 1000.0) if paced_send else 0.0
    tail_delay_s = max(0.0, tail_delay_ms / 1000.0)
    tail_bands = max(0, int(tail_bands))
    tail_start = max(0, len(bands) - tail_bands)
    effective_chunk_size = _resolve_effective_chunk_size(chunk_size, send_mode=send_mode)
    smooth_limiter = _SmoothRateLimiter(target_bps=target_bps) if paced_send else None

    result: dict = {
        "sent_bytes": 0,
        "reply_bytes": b"",
        "status_raw": {},
        "status_decoded": {},
        "healthy": None,
        "issues": [],
        "interrupted": False,
        "effective_band_height": effective_band_height,
        "effective_chunk_size": effective_chunk_size,
        "diag": diag,
    }

    prev_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _sigint_handler)
    _diag_append_event(
        diag,
        "raw_print_begin",
        port=port,
        baudrate=baudrate,
        image_size={"width": w, "height": h},
        band_height_requested=band_height,
        band_height_effective=effective_band_height,
        band_count=len(bands),
        chunk_size=chunk_size,
        effective_chunk_size=effective_chunk_size,
        chunk_delay_ms=chunk_delay_ms,
        send_mode=send_mode,
        paced_send=paced_send,
        target_bps=target_bps,
        inter_band_gap_ms=inter_band_gap_ms,
        tail_bands=tail_bands,
        tail_delay_ms=tail_delay_ms,
        pad_last_band=pad_last_band,
        auto_band_height=auto_band_height,
        min_tail_rows=min_tail_rows,
        feed=feed,
        feed_mode=feed_mode,
        read_reply=read_reply,
        status_check=status_check,
        diag_passive_rx=diag_passive_rx,
        diag_active_status=diag_active_status,
        diag_snapshot_every_band=diag_snapshot_every_band,
    )
    try:
        with pyserial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=pyserial.EIGHTBITS,
            parity=pyserial.PARITY_NONE,
            stopbits=pyserial.STOPBITS_ONE,
            timeout=3,
            write_timeout=30.0,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        ) as ser:
            _diag_append_event(diag, "serial_opened")
            try:
                init_cmd = b"\x1B\x40" + heat_cmd
                result["sent_bytes"] += _write_interruptible(
                    ser=ser,
                    payload=init_cmd,
                    chunk_size=effective_chunk_size,
                    chunk_delay_s=chunk_delay_s,
                    smooth_limiter=smooth_limiter,
                )
                _diag_append_event(
                    diag,
                    "init_sent",
                    payload_len=len(init_cmd),
                    sent_bytes_total=result["sent_bytes"],
                )

                for i, band_cmd in enumerate(bands):
                    band_index = i + 1
                    started = time.monotonic()
                    result["sent_bytes"] += _write_interruptible(
                        ser=ser,
                        payload=band_cmd,
                        chunk_size=effective_chunk_size,
                        chunk_delay_s=chunk_delay_s,
                        smooth_limiter=smooth_limiter,
                    )
                    elapsed_ms = (time.monotonic() - started) * 1000.0
                    _diag_append_event(
                        diag,
                        "band_sent",
                        band_index=band_index,
                        band_total=len(bands),
                        payload_len=len(band_cmd),
                        sent_bytes_total=result["sent_bytes"],
                        elapsed_ms=round(elapsed_ms, 3),
                        tail_guard=bool(i >= tail_start),
                    )

                    if diagnostic and diag_passive_rx:
                        rx = _read_reply_bytes(
                            ser=ser,
                            max_wait_s=max(0.0, diag_rx_wait_ms / 1000.0),
                            quiet_wait_s=max(0.0, diag_rx_quiet_ms / 1000.0),
                        )
                        if rx:
                            _diag_append_event(
                                diag,
                                "band_passive_rx",
                                band_index=band_index,
                                rx=_bytes_hex_preview(rx),
                            )

                    if (
                        diagnostic
                        and diag_active_status
                        and (band_index % diag_snapshot_every_band == 0)
                    ):
                        snap = _diag_collect_status_snapshot(
                            ser=ser,
                            timeout_s=max(0.01, diag_status_timeout_ms / 1000.0),
                        )
                        _diag_append_event(
                            diag,
                            "band_status_snapshot",
                            band_index=band_index,
                            snapshot=snap,
                        )

                    if i >= tail_start:
                        _diag_append_event(
                            diag,
                            "tail_guard_sleep",
                            band_index=band_index,
                            sleep_ms=round(tail_delay_s * 1000.0, 3),
                        )
                        _sleep_interruptible(tail_delay_s)

                    if i < len(bands) - 1 and inter_band_gap_s > 0:
                        _diag_append_event(
                            diag,
                            "inter_band_gap_sleep",
                            band_index=band_index,
                            sleep_ms=round(inter_band_gap_s * 1000.0, 3),
                        )
                        _sleep_interruptible(inter_band_gap_s)

                if feed > 0:
                    if feed_mode == "escd":
                        # ESC d n：按“行”走纸，部分机型比连发 LF 更稳定。
                        feed_cmd = bytes((0x1B, 0x64, min(255, feed)))
                    else:
                        feed_cmd = b"\n" * feed
                    result["sent_bytes"] += _write_interruptible(
                        ser=ser,
                        payload=feed_cmd,
                        chunk_size=effective_chunk_size,
                        chunk_delay_s=chunk_delay_s,
                        smooth_limiter=smooth_limiter,
                    )
                    _diag_append_event(
                        diag,
                        "feed_sent",
                        payload_len=len(feed_cmd),
                        sent_bytes_total=result["sent_bytes"],
                        feed_mode=feed_mode,
                    )
            except KeyboardInterrupt:
                # 尽量清空/复位，减少后续乱码和纸张浪费。
                result["interrupted"] = True
                _diag_append_event(diag, "keyboard_interrupt")
                try:
                    ser.write(b"\x18\x1B\x40")  # CAN + ESC @
                    ser.flush()
                    _diag_append_event(diag, "interrupt_cancel_sent", payload_hex="18 1b 40")
                except Exception:
                    _diag_append_event(diag, "interrupt_cancel_failed")
                    pass
                return result

            ser.flush()
            _diag_append_event(diag, "serial_flushed")

            if read_reply:
                result["reply_bytes"] = _read_reply_bytes(ser=ser, max_wait_s=0.5, quiet_wait_s=0.12)
                if result["reply_bytes"]:
                    _diag_append_event(diag, "final_reply", rx=_bytes_hex_preview(result["reply_bytes"]))

            if status_check:
                time.sleep(0.2)
                raw: dict[int, Optional[int]] = {}
                decoded: dict[int, dict] = {}
                for n in (1, 2, 3, 4):
                    val = _query_rt_status(ser=ser, n=n, timeout_s=0.5)
                    raw[n] = val
                    if val is not None:
                        decoded[n] = _decode_status(status_n=n, val=val)
                result["status_raw"] = raw
                result["status_decoded"] = decoded
                if decoded:
                    healthy, issues = _summarize_printer_health(decoded)
                    result["healthy"] = healthy
                    result["issues"] = issues
                _diag_append_event(
                    diag,
                    "final_status_snapshot",
                    status_raw={str(k): v for k, v in raw.items()},
                    status_decoded={str(k): v for k, v in decoded.items()},
                    healthy=result["healthy"],
                    issues=result["issues"],
                )
    except Exception as exc:
        _diag_append_event(
            diag,
            "raw_print_error",
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise
    finally:
        _diag_append_event(diag, "raw_print_end", interrupted=result["interrupted"])
        signal.signal(signal.SIGINT, prev_sigint)
    return result


def print_with_escpos(
    bw: Image.Image,
    port: str,
    baudrate: int,
    feed: int,
    impl: str,
    fragment_height: int,
    high_density_vertical: bool,
    high_density_horizontal: bool,
    heat_cmd: bytes,
) -> None:
    """使用 python-escpos 后端打印位图。"""
    if EscposSerial is None:
        raise RuntimeError("python-escpos is not installed")

    printer = EscposSerial(
        devfile=port,
        baudrate=baudrate,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=3.0,
        dsrdtr=False,
    )
    try:
        if heat_cmd:
            printer._raw(heat_cmd)
        printer.image(
            bw,
            impl=impl,
            fragment_height=fragment_height,
            center=False,
            high_density_vertical=high_density_vertical,
            high_density_horizontal=high_density_horizontal,
        )
        if feed > 0:
            printer.text("\n" * feed)
    finally:
        printer.close()


def parse_args() -> argparse.Namespace:
    """定义并解析命令行参数。"""
    p = argparse.ArgumentParser(
        description="MY-638 ESC/POS 图片打印工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--image", required=False, type=Path, default=None, help="待打印图片路径（支持 PNG/JPG/BMP 等）；自检模式可不填")
    p.add_argument(
        "--self-test",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="打印自检页（发送 ESC @ + DC2 T，即 1B 40 12 54）",
    )
    p.add_argument(
        "--width",
        type=int,
        default=MAX_WIDTH_58MM,
        help="目标打印宽度（点）。58mm 常用 384，80mm 常用 576",
    )
    p.add_argument("--upscale", action="store_true", help="若原图宽度小于 --width，允许放大到目标宽度")
    p.add_argument("--gray-depth", type=int, choices=(1, 4, 8), default=8, help="二值化前灰度级模拟（1/4/8）")
    p.add_argument("--gamma", type=float, default=1.15, help="灰度 gamma，>1 通常可提亮暗部细节")
    p.add_argument("--contrast", type=float, default=1.02, help="灰度对比度系数，>1 增强层次，<1 降低反差")
    p.add_argument("--threshold", type=int, default=170, help="二值化阈值 0~255，越低越黑，越高越白")
    p.add_argument(
        "--dither",
        choices=(DITHER_NONE, DITHER_ORDERED, DITHER_SIERRA, DITHER_FLOYD_LEGACY),
        default=DITHER_SIERRA,
        help="抖动算法：none/ordered/sierra（floyd 为兼容旧值，会自动迁移到 sierra）",
    )
    p.add_argument("--invert", action="store_true", help="打印前黑白反相")
    p.add_argument("--backend", choices=("auto", "escpos", "raw"), default="auto", help="打印后端：auto/escpos/raw")
    p.add_argument("--impl", choices=("bitImageRaster", "graphics", "bitImageColumn"), default="bitImageRaster", help="escpos 后端图像实现模式")
    p.add_argument("--fragment-height", type=int, default=960, help="escpos 后端图像分片高度")
    p.add_argument("--low-density-vertical", action="store_true", help="escpos 后端：关闭纵向高密度")
    p.add_argument("--low-density-horizontal", action="store_true", help="escpos 后端：关闭横向高密度")
    p.add_argument("--port", default=DEFAULT_PORT, help="串口设备路径，例如 /dev/cu.usbserial-0001")
    p.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="串口波特率，例如 9600")
    p.add_argument("--feed", type=int, default=3, help="打印结束后的额外走纸行数")
    p.add_argument(
        "--feed-mode",
        choices=("escd", "lf"),
        default="escd",
        help="走纸命令：escd=ESC d n（更稳），lf=连续 LF",
    )
    p.add_argument("--band-height", type=int, default=BAND_HEIGHT, help="RAW 后端条带高度（点）")
    p.add_argument(
        "--speed-mode",
        choices=("quality", "balanced", "fast"),
        default="balanced",
        help="RAW 发送速度档位：quality 稳定优先，fast 速度优先",
    )
    p.add_argument("--chunk-size", type=int, default=64, help="RAW 串口每次写入的 chunk 大小（字节）")
    p.add_argument(
        "--chunk-delay-ms",
        type=float,
        default=None,
        help="RAW 串口 chunk 间隔毫秒；设置后会覆盖 --speed-mode",
    )
    p.add_argument(
        "--send-mode",
        choices=(SEND_MODE_BURST, SEND_MODE_PACED),
        default=None,
        help="RAW 发送模式：burst=连续吞吐优先，paced=恒速节奏优先",
    )
    p.add_argument(
        "--smooth-send",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="兼容旧参数：--smooth-send 等价 send-mode=paced，--no-smooth-send 等价 send-mode=burst",
    )
    p.add_argument(
        "--target-bps",
        type=int,
        default=8500,
        help="平滑发送目标速率（字节/秒），建议低于串口理论吞吐",
    )
    p.add_argument(
        "--inter-band-gap-ms",
        type=float,
        default=1.0,
        help="相邻条带之间的额外间隔（毫秒），用于平滑机械节奏",
    )
    p.add_argument("--tail-bands", type=int, default=2, help="对最后 N 个条带启用尾段保护（额外延时）")
    p.add_argument("--tail-delay-ms", type=float, default=90.0, help="尾段保护时每个条带额外延时（毫秒）")
    p.add_argument(
        "--auto-band-height",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="自动调整条带高度以避免尾段过短",
    )
    p.add_argument("--min-tail-rows", type=int, default=24, help="自动调高条带时要求的最小尾段行数")
    p.add_argument(
        "--pad-last-band",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="是否把最后不足一整段的条带补白到整段高度",
    )
    p.add_argument("--heat-n1", type=int, default=None, help="ESC 7 n1：最多加热点（单位 8dots）")
    p.add_argument("--heat-n2", type=int, default=None, help="ESC 7 n2：加热时间（单位 10us）")
    p.add_argument("--heat-n3", type=int, default=None, help="ESC 7 n3：加热间隔（单位 10us）")
    p.add_argument("--dry-run", action="store_true", help="仅做预处理并打印参数，不发送到打印机")
    p.add_argument(
        "--read-reply",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="是否读取串口回包（部分机型开启会增加异常输出风险）",
    )
    p.add_argument(
        "--status-check",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="是否发送实时状态查询（部分机型开启会增加异常输出风险）",
    )
    p.add_argument(
        "--diagnostic",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="开启诊断模式：记录条带发送、回显和状态快照到 JSON 文件",
    )
    p.add_argument(
        "--diag-file",
        type=Path,
        default=None,
        help="诊断文件路径（仅 --diagnostic 时生效；不填则自动生成文件名）",
    )
    p.add_argument(
        "--diag-passive-rx",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="诊断模式下：每个条带后被动读取串口回显",
    )
    p.add_argument(
        "--diag-active-status",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="诊断模式下：主动发送 DLE EOT 状态查询（更侵入，默认关）",
    )
    p.add_argument(
        "--diag-snapshot-every-band",
        type=int,
        default=1,
        help="诊断模式下主动状态查询频率（每 N 个条带查询一次）",
    )
    p.add_argument(
        "--diag-rx-wait-ms",
        type=float,
        default=DEFAULT_DIAG_RX_WAIT_MS,
        help="诊断模式被动回显读取最大等待时长（毫秒）",
    )
    p.add_argument(
        "--diag-rx-quiet-ms",
        type=float,
        default=DEFAULT_DIAG_RX_QUIET_MS,
        help="诊断模式回显读取静默截止时长（毫秒）",
    )
    p.add_argument(
        "--diag-status-timeout-ms",
        type=float,
        default=DEFAULT_DIAG_STATUS_TIMEOUT_MS,
        help="诊断模式主动状态查询超时（毫秒）",
    )
    p.add_argument("--save-bw", type=Path, default=None, help="将预处理后的 1-bit 图片另存到指定路径")
    return p.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    """在图像处理和串口发送前校验参数合法性。"""
    if args.self_test:
        # 自检模式不依赖图片和图像参数。
        pass
    else:
        if args.image is None:
            raise ValueError("--image is required when --self-test is not enabled")
        if not args.image.exists():
            raise FileNotFoundError(f"image not found: {args.image}")
        if args.width <= 0:
            raise ValueError("--width must be positive")
        if args.width > MAX_WIDTH_80MM:
            raise ValueError(f"--width too large: {args.width}, max supported default is {MAX_WIDTH_80MM}")

    if args.band_height <= 0:
        raise ValueError("--band-height must be positive")
    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be positive")
    if args.chunk_delay_ms is not None and args.chunk_delay_ms < 0:
        raise ValueError("--chunk-delay-ms must be >= 0")
    if args.target_bps <= 0:
        raise ValueError("--target-bps must be > 0")
    if args.inter_band_gap_ms < 0:
        raise ValueError("--inter-band-gap-ms must be >= 0")
    if args.gamma <= 0:
        raise ValueError("--gamma must be > 0")
    if args.contrast <= 0:
        raise ValueError("--contrast must be > 0")
    if args.tail_bands < 0:
        raise ValueError("--tail-bands must be >= 0")
    if args.tail_delay_ms < 0:
        raise ValueError("--tail-delay-ms must be >= 0")
    if args.min_tail_rows < 0:
        raise ValueError("--min-tail-rows must be >= 0")
    if args.diag_snapshot_every_band <= 0:
        raise ValueError("--diag-snapshot-every-band must be > 0")
    if args.diag_rx_wait_ms < 0:
        raise ValueError("--diag-rx-wait-ms must be >= 0")
    if args.diag_rx_quiet_ms < 0:
        raise ValueError("--diag-rx-quiet-ms must be >= 0")
    if args.diag_status_timeout_ms <= 0:
        raise ValueError("--diag-status-timeout-ms must be > 0")


def _resolve_backend(backend: str) -> str:
    """解析后端参数：auto 时根据环境自动选择。"""
    if backend == "auto":
        return "escpos" if EscposSerial is not None else "raw"
    return backend


def _resolve_chunk_delay(args: argparse.Namespace) -> tuple[float, str]:
    """解析最终 chunk 延时：手动参数优先于 speed-mode 档位。"""
    if args.chunk_delay_ms is not None:
        return float(args.chunk_delay_ms), "manual"
    return SPEED_MODE_TO_CHUNK_DELAY_MS[args.speed_mode], args.speed_mode


def _resolve_send_mode(args: argparse.Namespace) -> tuple[str, str]:
    """解析最终发送模式，并兼容旧参数 smooth-send。"""
    if args.send_mode is not None:
        if args.smooth_send is not None:
            compat_mode = SEND_MODE_PACED if args.smooth_send else SEND_MODE_BURST
            if compat_mode != args.send_mode:
                return args.send_mode, "send_mode_override_smooth_send"
        return args.send_mode, "send_mode"
    if args.smooth_send is None:
        return SEND_MODE_BURST, "default"
    return (SEND_MODE_PACED if args.smooth_send else SEND_MODE_BURST), "smooth_send_compat"


def _resolve_dither_mode(dither: str) -> tuple[str, Optional[str]]:
    """解析最终抖动模式，并兼容旧值 floyd。

    返回：
    - mode: 最终生效的抖动模式（none/ordered/sierra）
    - note: 可选提示文案；为 None 表示无需提示
    """
    normalized = str(dither).strip().lower()
    if normalized == DITHER_FLOYD_LEGACY:
        return (
            DITHER_SIERRA,
            "检测到 dither=floyd（旧模式），已自动迁移为 sierra：可降低乱码风险并减轻条纹。",
        )
    if normalized in (DITHER_NONE, DITHER_ORDERED, DITHER_SIERRA):
        return normalized, None
    raise ValueError(f"unsupported dither: {dither}")


def _print_prepare_summary(
    args: argparse.Namespace,
    bw: Image.Image,
    heat_cmd: bytes,
    chunk_delay_ms: float,
    chunk_delay_source: str,
    send_mode: str,
    send_mode_source: str,
    effective_chunk_size: int,
) -> None:
    """打印预检查信息，便于快速确认当前生效参数。"""
    w, h = bw.size
    print(
        f"预处理完成: {args.image} -> {w}x{h}, gray_depth={args.gray_depth}, "
        f"dither={args.dither}, threshold={args.threshold}"
    )
    print(
        f"速度参数: speed_mode={args.speed_mode}, effective_chunk_delay_ms={chunk_delay_ms:g} "
        f"(来源={chunk_delay_source})"
    )
    print(
        f"发送模式: send_mode={send_mode} (来源={send_mode_source}), target_bps={args.target_bps}, "
        f"effective_chunk_size={effective_chunk_size}, inter_band_gap_ms={args.inter_band_gap_ms:g}"
    )
    if send_mode == SEND_MODE_PACED and chunk_delay_ms > 0:
        print("提示: send_mode=paced 时，fixed chunk-delay 已自动忽略。")
    if send_mode == SEND_MODE_BURST:
        print("提示: send_mode=burst 时，不启用恒速限流与条带间固定等待。")
    print(
        f"图像调优: gamma={args.gamma:g}, contrast={args.contrast:g}; "
        f"尾段保护: bands={args.tail_bands}, delay_ms={args.tail_delay_ms:g}, pad_last_band={args.pad_last_band}"
    )
    print(
        f"链路保护: auto_band_height={args.auto_band_height}, min_tail_rows={args.min_tail_rows}, "
        f"feed_mode={args.feed_mode}, read_reply={args.read_reply}, status_check={args.status_check}"
    )
    if args.diagnostic:
        print(
            "诊断模式: enabled=True, "
            f"passive_rx={args.diag_passive_rx}, active_status={args.diag_active_status}, "
            f"snapshot_every_band={args.diag_snapshot_every_band}"
        )
    if heat_cmd:
        print(f"已启用热敏浓度参数: ESC 7 {args.heat_n1} {args.heat_n2} {args.heat_n3}")


def _build_diag_payload(
    args: argparse.Namespace,
    bw: Image.Image,
    chunk_delay_ms: float,
    chunk_delay_source: str,
    send_mode: str,
    send_mode_source: str,
    effective_chunk_size: int,
) -> dict[str, Any]:
    """构造诊断文件的基础信息。"""
    w, h = bw.size
    return {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "manual_reference": {
            "source": "MinerU_markdown_MY-628_638规格书.md",
            "section": "状态指令（GS r / DLE EOT）",
            "note": "状态位含义按该规格书实现，不做推测。",
        },
        "job": {
            "image": str(args.image),
            "image_size": {"width": w, "height": h},
            "port": args.port,
            "baudrate": args.baudrate,
            "backend": args.backend,
            "feed": args.feed,
            "feed_mode": args.feed_mode,
            "width": args.width,
            "upscale": args.upscale,
            "gray_depth": args.gray_depth,
            "gamma": args.gamma,
            "contrast": args.contrast,
            "threshold": args.threshold,
            "dither": args.dither,
            "invert": args.invert,
            "band_height": args.band_height,
            "speed_mode": args.speed_mode,
            "chunk_size": args.chunk_size,
            "effective_chunk_size": effective_chunk_size,
            "chunk_delay_ms": chunk_delay_ms,
            "chunk_delay_source": chunk_delay_source,
            "send_mode": send_mode,
            "send_mode_source": send_mode_source,
            "smooth_send": args.smooth_send,
            "target_bps": args.target_bps,
            "inter_band_gap_ms": args.inter_band_gap_ms,
            "tail_bands": args.tail_bands,
            "tail_delay_ms": args.tail_delay_ms,
            "auto_band_height": args.auto_band_height,
            "min_tail_rows": args.min_tail_rows,
            "pad_last_band": args.pad_last_band,
            "read_reply": args.read_reply,
            "status_check": args.status_check,
            "diagnostic": args.diagnostic,
            "diag_passive_rx": args.diag_passive_rx,
            "diag_active_status": args.diag_active_status,
            "diag_snapshot_every_band": args.diag_snapshot_every_band,
            "diag_rx_wait_ms": args.diag_rx_wait_ms,
            "diag_rx_quiet_ms": args.diag_rx_quiet_ms,
            "diag_status_timeout_ms": args.diag_status_timeout_ms,
            "heat": {
                "enabled": args.heat_n1 is not None,
                "n1": args.heat_n1,
                "n2": args.heat_n2,
                "n3": args.heat_n3,
            },
        },
        "events": [],
    }


def _build_self_test_diag_payload(
    args: argparse.Namespace,
    chunk_delay_ms: float,
    chunk_delay_source: str,
    send_mode: str,
    send_mode_source: str,
    effective_chunk_size: int,
) -> dict[str, Any]:
    """构造自检模式诊断文件基础信息。"""
    return {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "manual_reference": {
            "source": "MinerU_markdown_MY-628_638规格书.md",
            "section": "其他指令：打印自测页（DC2 T）",
            "note": "自检页命令按规格书示例 ESC @ + DC2 T 实现。",
        },
        "job": {
            "mode": "self_test",
            "port": args.port,
            "baudrate": args.baudrate,
            "backend": args.backend,
            "chunk_size": args.chunk_size,
            "effective_chunk_size": effective_chunk_size,
            "chunk_delay_ms": chunk_delay_ms,
            "chunk_delay_source": chunk_delay_source,
            "send_mode": send_mode,
            "send_mode_source": send_mode_source,
            "smooth_send": args.smooth_send,
            "target_bps": args.target_bps,
            "read_reply": args.read_reply,
            "status_check": args.status_check,
            "diagnostic": args.diagnostic,
            "self_test_payload_hex": SELF_TEST_PAGE_CMD.hex(" "),
        },
        "events": [],
    }


def _print_self_test_prepare_summary(
    args: argparse.Namespace,
    chunk_delay_ms: float,
    chunk_delay_source: str,
    send_mode: str,
    send_mode_source: str,
    effective_chunk_size: int,
) -> None:
    """打印自检模式预检查信息。"""
    print(f"自检模式: enabled=True, payload_hex={SELF_TEST_PAGE_CMD.hex(' ')}")
    print(
        f"设备参数: port={args.port}, baudrate={args.baudrate}, backend={args.backend}, "
        f"read_reply={args.read_reply}, status_check={args.status_check}"
    )
    print(
        f"发送参数: chunk_size={args.chunk_size}, speed_mode={args.speed_mode}, "
        f"effective_chunk_delay_ms={chunk_delay_ms:g} (来源={chunk_delay_source})"
    )
    print(
        f"发送模式: send_mode={send_mode} (来源={send_mode_source}), target_bps={args.target_bps}, "
        f"effective_chunk_size={effective_chunk_size}"
    )
    if send_mode == SEND_MODE_PACED and chunk_delay_ms > 0:
        print("提示: send_mode=paced 时，fixed chunk-delay 已自动忽略。")
    if send_mode == SEND_MODE_BURST:
        print("提示: send_mode=burst 时，不启用恒速限流。")
    if args.diagnostic:
        print("诊断模式: enabled=True（自检流程将记录发送与状态）")


def main() -> int:
    """程序入口：按固定顺序执行参数解析、预处理和打印。"""
    # 1) 解析命令行参数。
    args = parse_args()

    # 2) 校验参数和文件路径。
    _validate_args(args)

    # 3) 解析最终生效的发送速度参数。
    chunk_delay_ms, chunk_delay_source = _resolve_chunk_delay(args)
    send_mode, send_mode_source = _resolve_send_mode(args)
    dither_mode, dither_note = _resolve_dither_mode(args.dither)
    args.dither = dither_mode
    effective_chunk_size = _resolve_effective_chunk_size(
        args.chunk_size,
        send_mode=send_mode,
    )
    if dither_note:
        print(dither_note)

    # 4) 自检模式：直接发送 DC2 T 命令，不走图片预处理。
    if args.self_test:
        _print_self_test_prepare_summary(
            args=args,
            chunk_delay_ms=chunk_delay_ms,
            chunk_delay_source=chunk_delay_source,
            send_mode=send_mode,
            send_mode_source=send_mode_source,
            effective_chunk_size=effective_chunk_size,
        )

        if args.dry_run:
            print("dry_run=true，已跳过串口发送。")
            return 0

        diag_payload: Optional[dict[str, Any]] = None
        diag_file_path: Optional[Path] = None
        if args.diagnostic:
            diag_payload = _build_self_test_diag_payload(
                args=args,
                chunk_delay_ms=chunk_delay_ms,
                chunk_delay_source=chunk_delay_source,
                send_mode=send_mode,
                send_mode_source=send_mode_source,
                effective_chunk_size=effective_chunk_size,
            )
            diag_file_path = _resolve_diag_file_path(args.diag_file)
            print(f"诊断日志输出: {diag_file_path}")

        backend = _resolve_backend(args.backend)
        if backend != "raw":
            print("自检页命令仅支持 raw 后端，已自动切换为 raw。")

        try:
            result = print_self_test_with_raw(
                port=args.port,
                baudrate=args.baudrate,
                chunk_size=args.chunk_size,
                chunk_delay_ms=chunk_delay_ms,
                send_mode=send_mode,
                target_bps=args.target_bps,
                read_reply=args.read_reply,
                status_check=args.status_check,
                diagnostic=args.diagnostic,
                diag_payload=diag_payload,
            )
        except Exception as exc:
            if diag_payload is not None and diag_file_path is not None:
                diag_payload["result"] = {
                    "ok": False,
                    "interrupted": False,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
                saved_path = _write_diag_json(diag_file_path, diag_payload)
                print(f"诊断日志已保存（失败现场）: {saved_path}")
            raise

        if diag_payload is not None and diag_file_path is not None:
            diag_payload["result"] = {
                "ok": not bool(result.get("interrupted")),
                "interrupted": bool(result.get("interrupted")),
                "sent_bytes": int(result["sent_bytes"]),
                "reply_len": len(result["reply_bytes"]),
                "healthy": result["healthy"],
                "issues": list(result["issues"]),
                "effective_chunk_size": result.get("effective_chunk_size"),
            }
            saved_path = _write_diag_json(diag_file_path, diag_payload)
            print(f"诊断日志已保存: {saved_path}")

        if result.get("interrupted"):
            print("检测到 Ctrl+C：已停止自检页命令发送。")
            return 130

        print(f"自检页命令发送完成（backend=raw） port={args.port} baudrate={args.baudrate}")
        print(
            f"effective_chunk_size={result.get('effective_chunk_size')} "
            f"sent_bytes={result['sent_bytes']} reply_len={len(result['reply_bytes'])} "
            f"healthy={result['healthy']} issues={result['issues']}"
        )
        return 0

    # 5) 普通图片模式：将输入图片预处理为 1-bit 可打印位图。
    assert args.image is not None
    bw = preprocess_image(
        image_path=args.image,
        target_width=args.width,
        upscale=args.upscale,
        gray_depth=args.gray_depth,
        gamma=args.gamma,
        contrast=args.contrast,
        threshold=args.threshold,
        dither=args.dither,
        invert=args.invert,
    )

    # 6) 生成可选的 ESC 7 热敏浓度参数。
    heat_cmd = _build_heat_cmd(args.heat_n1, args.heat_n2, args.heat_n3)

    # 7) 按需保存预处理图。
    if args.save_bw is not None:
        bw.save(args.save_bw)

    # 8) 打印预检查摘要。
    _print_prepare_summary(
        args=args,
        bw=bw,
        heat_cmd=heat_cmd,
        chunk_delay_ms=chunk_delay_ms,
        chunk_delay_source=chunk_delay_source,
        send_mode=send_mode,
        send_mode_source=send_mode_source,
        effective_chunk_size=effective_chunk_size,
    )

    # 9) dry-run 模式只做预处理，不发串口。
    if args.dry_run:
        print("dry_run=true，已跳过串口发送。")
        return 0

    # 10) 若开启诊断，先准备诊断对象和输出路径。
    diag_payload: Optional[dict[str, Any]] = None
    diag_file_path: Optional[Path] = None
    if args.diagnostic:
        diag_payload = _build_diag_payload(
            args=args,
            bw=bw,
            chunk_delay_ms=chunk_delay_ms,
            chunk_delay_source=chunk_delay_source,
            send_mode=send_mode,
            send_mode_source=send_mode_source,
            effective_chunk_size=effective_chunk_size,
        )
        diag_file_path = _resolve_diag_file_path(args.diag_file)
        print(f"诊断日志输出: {diag_file_path}")

    # 11) 解析并执行打印后端。
    backend = _resolve_backend(args.backend)
    if args.diagnostic and backend != "raw":
        print("诊断模式仅支持 raw 后端，已自动切换为 raw。")
        backend = "raw"

    if backend == "escpos":
        try:
            print_with_escpos(
                bw=bw,
                port=args.port,
                baudrate=args.baudrate,
                feed=args.feed,
                impl=args.impl,
                fragment_height=args.fragment_height,
                high_density_vertical=not args.low_density_vertical,
                high_density_horizontal=not args.low_density_horizontal,
                heat_cmd=heat_cmd,
            )
            print(f"打印完成（backend=escpos） port={args.port} baudrate={args.baudrate}")
            return 0
        except Exception as exc:
            if args.backend == "escpos":
                raise
            print(f"escpos 后端失败（{type(exc).__name__}: {exc}），回退到 raw 后端...")

    # 12) 执行 raw 后端并输出结果。
    try:
        result = print_with_raw(
            bw=bw,
            port=args.port,
            baudrate=args.baudrate,
            feed=args.feed,
            band_height=args.band_height,
            heat_cmd=heat_cmd,
            chunk_size=args.chunk_size,
            chunk_delay_ms=chunk_delay_ms,
            send_mode=send_mode,
            target_bps=args.target_bps,
            inter_band_gap_ms=args.inter_band_gap_ms,
            tail_bands=args.tail_bands,
            tail_delay_ms=args.tail_delay_ms,
            pad_last_band=args.pad_last_band,
            auto_band_height=args.auto_band_height,
            min_tail_rows=args.min_tail_rows,
            feed_mode=args.feed_mode,
            read_reply=args.read_reply,
            status_check=args.status_check,
            diagnostic=args.diagnostic,
            diag_passive_rx=args.diag_passive_rx,
            diag_active_status=args.diag_active_status,
            diag_snapshot_every_band=args.diag_snapshot_every_band,
            diag_rx_wait_ms=args.diag_rx_wait_ms,
            diag_rx_quiet_ms=args.diag_rx_quiet_ms,
            diag_status_timeout_ms=args.diag_status_timeout_ms,
            diag_payload=diag_payload,
        )
    except Exception as exc:
        if diag_payload is not None and diag_file_path is not None:
            diag_payload["result"] = {
                "ok": False,
                "interrupted": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            saved_path = _write_diag_json(diag_file_path, diag_payload)
            print(f"诊断日志已保存（失败现场）: {saved_path}")
        raise

    if diag_payload is not None and diag_file_path is not None:
        diag_payload["result"] = {
            "ok": not bool(result.get("interrupted")),
            "interrupted": bool(result.get("interrupted")),
            "sent_bytes": int(result["sent_bytes"]),
            "reply_len": len(result["reply_bytes"]),
            "healthy": result["healthy"],
            "issues": list(result["issues"]),
            "effective_band_height": result.get("effective_band_height"),
            "effective_chunk_size": result.get("effective_chunk_size"),
        }
        saved_path = _write_diag_json(diag_file_path, diag_payload)
        print(f"诊断日志已保存: {saved_path}")

    if result.get("interrupted"):
        print("检测到 Ctrl+C：已停止后续发送并尝试取消缓存数据。")
        return 130

    print(f"打印完成（backend=raw） port={args.port} baudrate={args.baudrate}")
    print(f"effective_band_height={result.get('effective_band_height')}")
    print(f"effective_chunk_size={result.get('effective_chunk_size')}")
    print(
        f"sent_bytes={result['sent_bytes']} reply_len={len(result['reply_bytes'])} "
        f"healthy={result['healthy']} issues={result['issues']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
