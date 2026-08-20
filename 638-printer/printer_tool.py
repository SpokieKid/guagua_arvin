#!/usr/bin/env python3
"""
638 printer glue layer.

This module intentionally does not contain business-level print content builders
(text templates, image file processing, or embedded sample glyphs/images).
Callers should provide ready-to-send payload bytes or bitmap bytes.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import time
from typing import Optional

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover
    serial = None


DEFAULT_PORT = "/dev/cu.usbserial-3"
DEFAULT_BAUDRATE = 9600


def u16le(value: int) -> bytes:
    if not 0 <= value <= 0xFFFF:
        raise ValueError(f"value out of range for u16: {value}")
    return bytes((value & 0xFF, (value >> 8) & 0xFF))


def hex_dump(data: bytes, width: int = 32) -> str:
    chunks = []
    for i in range(0, len(data), width):
        part = data[i : i + width]
        chunks.append(" ".join(f"{b:02X}" for b in part))
    return "\n".join(chunks)


def parse_hex_payload(text: str) -> bytes:
    compact = "".join(text.split())
    if len(compact) % 2 != 0:
        raise ValueError("hex payload length must be even")
    try:
        return bytes.fromhex(compact)
    except ValueError as exc:
        raise ValueError(f"invalid hex payload: {exc}") from exc


def build_pos_init_cmd() -> bytes:
    return b"\x1B\x40"


def build_pos_feed_cmd(lines: int) -> bytes:
    if lines < 0:
        raise ValueError("lines must be >= 0")
    return b"\n" * lines


def build_pos_cut_cmd(cut: Optional[str]) -> bytes:
    if cut == "half":
        return b"\x1D\x56\x01"
    if cut == "full":
        return b"\x1D\x56\x00"
    if cut in (None, "none"):
        return b""
    raise ValueError("cut must be one of: none, half, full")


def build_pos_job(
    body: bytes,
    add_init: bool = True,
    feed_lines: int = 0,
    cut: Optional[str] = None,
) -> bytes:
    out = bytearray()
    if add_init:
        out += build_pos_init_cmd()
    out += body
    out += build_pos_feed_cmd(feed_lines)
    out += build_pos_cut_cmd(cut)
    return bytes(out)


def build_pos_raster_image_cmd(width: int, height: int, data: bytes, mode: int = 0) -> bytes:
    if width <= 0 or height <= 0:
        raise ValueError("width/height must be positive")
    if mode not in (0, 1, 2, 3, 48, 49, 50, 51):
        raise ValueError("invalid GS v 0 mode")
    width_bytes = (width + 7) // 8
    expected = width_bytes * height
    if len(data) != expected:
        raise ValueError(
            f"bitmap data len mismatch for pos raster: got={len(data)}, expected={expected}"
        )
    out = bytearray()
    out += bytes((0x1D, 0x76, 0x30, mode))
    out += u16le(width_bytes)
    out += u16le(height)
    out += data
    return bytes(out)


def _bitmap_is_black(data: bytes, width: int, x: int, y: int, lsb_first: bool) -> bool:
    row_bytes = (width + 7) // 8
    idx = y * row_bytes + (x // 8)
    bit = (x % 8) if lsb_first else (7 - (x % 8))
    return bool((data[idx] >> bit) & 0x01)


def build_pos_esc_star24_image_cmd(
    width: int,
    height: int,
    data: bytes,
    lsb_first: bool = False,
) -> bytes:
    row_bytes = (width + 7) // 8
    expected = row_bytes * height
    if len(data) != expected:
        raise ValueError(
            f"bitmap data len mismatch for esc_star24: got={len(data)}, expected={expected}"
        )
    out = bytearray()
    out += b"\x1B\x33\x18"
    for y_base in range(0, height, 24):
        out += b"\x1B\x2A\x21"
        out += u16le(width)
        for x in range(width):
            for stripe in range(3):
                v = 0
                for b in range(8):
                    y = y_base + stripe * 8 + b
                    if y >= height:
                        continue
                    if _bitmap_is_black(data=data, width=width, x=x, y=y, lsb_first=lsb_first):
                        v |= 1 << (7 - b)
                out.append(v)
        out += b"\n"
    out += b"\x1B\x32"
    return bytes(out)


def _read_reply_bytes(ser: "serial.Serial", max_wait_s: float, quiet_wait_s: float) -> bytes:
    if max_wait_s <= 0:
        return b""
    data = bytearray()
    start = time.monotonic()
    last_data_at = start
    while True:
        now = time.monotonic()
        if now - start > max_wait_s:
            break
        waiting = ser.in_waiting
        if waiting > 0:
            data += ser.read(waiting)
            last_data_at = now
            continue
        if data and (now - last_data_at) >= quiet_wait_s:
            break
        time.sleep(0.01)
    return bytes(data)


def _query_rt_status(ser: "serial.Serial", n: int, timeout_s: float) -> Optional[int]:
    if n not in (1, 2, 3, 4):
        raise ValueError("n must be in (1,2,3,4)")
    old_timeout = ser.timeout
    try:
        ser.timeout = timeout_s
        ser.write(bytes((0x10, 0x04, n)))
        ser.flush()
        resp = ser.read(1)
        if len(resp) != 1:
            return None
        return resp[0]
    finally:
        ser.timeout = old_timeout


def _decode_status(status_n: int, val: int) -> dict:
    if status_n == 1:
        return {
            "raw": val,
            "online": not bool(val & 0x08),
            "cash_drawers_closed": bool(val & 0x04),
            "paper_torn_away": not bool(val & 0x80),
        }
    if status_n == 2:
        return {
            "raw": val,
            "cover_open": bool(val & 0x04),
            "feed_key_pressed": bool(val & 0x08),
            "paper_out": bool(val & 0x20),
            "error_present": bool(val & 0x40),
        }
    if status_n == 3:
        return {
            "raw": val,
            "cutter_error": bool(val & 0x08),
            "unrecoverable_error": bool(val & 0x20),
            "head_temp_or_voltage_error": bool(val & 0x40),
        }
    if status_n == 4:
        paper_sensor_bits_2_3 = val & 0x0C
        paper_sensor_bits_5_6 = val & 0x60
        paper_sensor_2_3_text = {
            0x00: "paper_sufficient",
            0x04: "paper_taken_away",
            0x0C: "paper_near_end",
        }.get(paper_sensor_bits_2_3, "paper_sensor_unknown")
        paper_sensor_5_6_text = {
            0x00: "paper_present",
            0x60: "paper_out",
        }.get(paper_sensor_bits_5_6, "paper_sensor_unknown")
        return {
            "raw": val,
            "paper_sensor_bits_2_3": paper_sensor_bits_2_3,
            "paper_sensor_bits_5_6": paper_sensor_bits_5_6,
            "paper_sensor_2_3_text": paper_sensor_2_3_text,
            "paper_sensor_5_6_text": paper_sensor_5_6_text,
            "paper_out": paper_sensor_bits_5_6 == 0x60,
        }
    raise ValueError(f"unsupported status_n={status_n}")


def _summarize_printer_health(decoded_status: dict[int, dict]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    s1 = decoded_status.get(1)
    s2 = decoded_status.get(2)
    s3 = decoded_status.get(3)
    s4 = decoded_status.get(4)
    if s1 is not None and not s1["online"]:
        issues.append("printer_offline")
    if s2 is not None:
        if s2["cover_open"]:
            issues.append("cover_open")
        if s2["paper_out"]:
            issues.append("paper_out(n2)")
        if s2["error_present"]:
            issues.append("error_present(n2)")
    if s3 is not None:
        if s3["cutter_error"]:
            issues.append("cutter_error")
        if s3["unrecoverable_error"]:
            issues.append("unrecoverable_error")
        if s3["head_temp_or_voltage_error"]:
            issues.append("head_temp_or_voltage_error")
    if s4 is not None and s4["paper_out"]:
        issues.append("paper_out(n4)")
    return len(issues) == 0, issues


def send_serial(
    port: str,
    baudrate: int,
    payload: bytes,
    chunk_size: int = 64,
    chunk_delay_s: float = 0.012,
    write_timeout_s: float = 30.0,
    write_retry: int = 1,
    flush_each_chunk: bool = False,
    flush_after_write: bool = False,
    read_reply: bool = True,
    reply_wait_s: float = 0.8,
    reply_quiet_s: float = 0.12,
    query_status: bool = True,
    status_delay_s: float = 0.2,
    status_timeout_s: float = 0.5,
) -> dict:
    if serial is None:
        raise RuntimeError("pyserial is required. Please install with: pip install pyserial")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if write_retry < 0:
        raise ValueError("write_retry must be >= 0")

    result: dict = {
        "sent_bytes": len(payload),
        "reply_bytes": b"",
        "status_raw": {},
        "status_decoded": {},
        "healthy": None,
        "issues": [],
    }

    with serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=3,
        write_timeout=write_timeout_s,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    ) as ser:
        for i in range(0, len(payload), chunk_size):
            chunk = payload[i : i + chunk_size]
            for attempt in range(write_retry + 1):
                try:
                    offset = 0
                    while offset < len(chunk):
                        written = ser.write(chunk[offset:])
                        if not written:
                            raise serial.SerialTimeoutException("write returned 0 bytes")
                        offset += written
                    if flush_each_chunk:
                        ser.flush()
                    break
                except serial.SerialTimeoutException:
                    if attempt >= write_retry:
                        raise
                    time.sleep(max(0.01, chunk_delay_s))
            if chunk_delay_s > 0:
                time.sleep(chunk_delay_s)
        if flush_after_write:
            ser.flush()
        if read_reply:
            result["reply_bytes"] = _read_reply_bytes(
                ser=ser,
                max_wait_s=reply_wait_s,
                quiet_wait_s=reply_quiet_s,
            )
        if query_status:
            if status_delay_s > 0:
                time.sleep(status_delay_s)
            raw: dict[int, Optional[int]] = {}
            decoded: dict[int, dict] = {}
            for n in (1, 2, 3, 4):
                val = _query_rt_status(ser=ser, n=n, timeout_s=status_timeout_s)
                raw[n] = val
                if val is not None:
                    decoded[n] = _decode_status(status_n=n, val=val)
            result["status_raw"] = raw
            result["status_decoded"] = decoded
            if decoded:
                healthy, issues = _summarize_printer_health(decoded)
                result["healthy"] = healthy
                result["issues"] = issues
    return result


def save_hex_if_needed(path: Optional[Path], payload: bytes) -> None:
    if path is None:
        return
    path.write_text(hex_dump(payload) + "\n", encoding="utf-8")


def _add_cli_io_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--port", default=DEFAULT_PORT, help="serial port path")
    p.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="serial baudrate")
    p.add_argument("--dry-run", action="store_true", help="only print hex payload; do not send")
    p.add_argument("--save-hex", type=Path, help="optional path to save final payload as hex text")
    p.add_argument("--chunk-size", type=int, default=64, help="serial write chunk size in bytes")
    p.add_argument("--chunk-delay-ms", type=float, default=12.0, help="delay between chunks in ms")
    p.add_argument("--write-timeout", type=float, default=30.0, help="serial write timeout in seconds")
    p.add_argument(
        "--write-retry",
        type=int,
        default=1,
        help="retry count when serial write timeout occurs",
    )
    p.add_argument("--flush-each-chunk", action="store_true", help="flush serial after each chunk")
    p.add_argument("--flush-after-write", action="store_true", help="flush after full payload write")
    p.add_argument("--no-read-reply", action="store_true", help="disable reading serial reply bytes")
    p.add_argument("--reply-wait", type=float, default=0.8, help="max seconds to read reply bytes")
    p.add_argument(
        "--reply-quiet",
        type=float,
        default=0.12,
        help="stop reply read when no new byte for this duration(s)",
    )
    p.add_argument("--show-reply-hex", action="store_true", help="print reply bytes in hex")
    p.add_argument(
        "--no-status-check",
        action="store_true",
        help="disable DLE EOT realtime status query (10 04 01~04)",
    )
    p.add_argument("--status-delay", type=float, default=0.2, help="delay before status query")
    p.add_argument("--status-timeout", type=float, default=0.5, help="timeout per status query")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="638 printer glue-layer serial tool")
    parser.add_argument(
        "--hex",
        required=True,
        help="raw payload hex string; spaces/newlines are allowed",
    )
    parser.add_argument(
        "--wrap-pos",
        action="store_true",
        help="wrap payload with ESC @ + optional feed/cut",
    )
    parser.add_argument("--feed-lines", type=int, default=0, help="extra LF lines when --wrap-pos")
    parser.add_argument(
        "--cut",
        choices=["none", "half", "full"],
        default="none",
        help="cut type when --wrap-pos",
    )
    _add_cli_io_args(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = parse_hex_payload(args.hex)
    if args.wrap_pos:
        cut = None if args.cut == "none" else args.cut
        payload = build_pos_job(
            body=payload,
            add_init=True,
            feed_lines=args.feed_lines,
            cut=cut,
        )

    save_hex_if_needed(args.save_hex, payload)

    if args.dry_run:
        print(f"payload_bytes={len(payload)}")
        print(hex_dump(payload))
        return 0

    send_result = send_serial(
        port=args.port,
        baudrate=args.baudrate,
        payload=payload,
        chunk_size=args.chunk_size,
        chunk_delay_s=max(0.0, args.chunk_delay_ms / 1000.0),
        write_timeout_s=args.write_timeout,
        write_retry=args.write_retry,
        flush_each_chunk=args.flush_each_chunk,
        flush_after_write=args.flush_after_write,
        read_reply=not args.no_read_reply,
        reply_wait_s=args.reply_wait,
        reply_quiet_s=args.reply_quiet,
        query_status=not args.no_status_check,
        status_delay_s=args.status_delay,
        status_timeout_s=args.status_timeout,
    )

    print(f"sent {send_result['sent_bytes']} bytes to {args.port} @ {args.baudrate}")
    reply_bytes: bytes = send_result["reply_bytes"]
    if not args.no_read_reply:
        print(f"reply_bytes={len(reply_bytes)}")
        if args.show_reply_hex and reply_bytes:
            print(hex_dump(reply_bytes))

    if not args.no_status_check:
        raw = send_result["status_raw"]
        decoded = send_result["status_decoded"]
        for n in (1, 2, 3, 4):
            val = raw.get(n)
            if val is None:
                print(f"status n={n}: no_response")
                continue
            print(f"status n={n}: 0x{val:02X} ({val}) {decoded.get(n)}")
        healthy = send_result["healthy"]
        issues = send_result["issues"]
        if healthy is True:
            print("printer_health=ok")
        elif healthy is False:
            print(f"printer_health=not_ok issues={issues}")
        else:
            print("printer_health=unknown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
