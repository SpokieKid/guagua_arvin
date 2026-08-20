#!/usr/bin/env python3
"""MiniMax 文本转语音并输出 mp3/ogg。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib import error, request


API_URL = "https://api.minimaxi.com/v1/t2a_v2"
DEFAULT_MODEL = "speech-2.8-hd"
DEFAULT_VOICE_ID = "jiliguagua_xiaoqingwa001_0224"
DEFAULT_TIMEOUT = 120
SCRIPT_DIR = Path(__file__).resolve().parent
HAPPY_BOOST_LEVELS = {"off", "light", "medium", "strong"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="调用 MiniMax TTS，把文本转成 mp3 和目标规格的 ogg。"
    )
    parser.add_argument("--text", help="直接传入要合成的文本")
    parser.add_argument("--text-file", help="从文本文件读取要合成的内容")
    parser.add_argument("--api-key", help="MiniMax API Key，默认读取 MINIMAX_API_KEY")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MiniMax 模型名")
    parser.add_argument("--voice-id", default=DEFAULT_VOICE_ID, help="声音 ID")
    parser.add_argument("--emotion", default="happy", help="情绪参数")
    parser.add_argument("--speed", type=float, default=1.0, help="语速")
    parser.add_argument("--vol", type=float, default=1.0, help="音量")
    parser.add_argument("--pitch", type=int, default=0, help="音调")
    parser.add_argument(
        "--happy-boost",
        default="off",
        choices=sorted(HAPPY_BOOST_LEVELS),
        help="开心增强强度",
    )
    parser.add_argument("--group-id", help="MiniMax group_id，可选")
    parser.add_argument("--out-dir", default=".", help="输出目录")
    parser.add_argument("--out-name", help="输出文件名，不带扩展名")
    parser.add_argument("--mp3-out", help="指定 mp3 输出路径")
    parser.add_argument("--ogg-out", help="指定 ogg 输出路径")
    parser.add_argument(
        "--keep-mp3",
        action="store_true",
        help="转码完成后保留 mp3，默认只保留 ogg",
    )
    parser.add_argument(
        "--subtitle-enable",
        action="store_true",
        help="是否开启字幕信息",
    )
    parser.add_argument(
        "--bitrate",
        type=int,
        default=128000,
        help="请求 mp3 的码率",
    )
    return parser.parse_args()


def read_text(args: argparse.Namespace) -> str:
    if args.text and args.text_file:
        raise ValueError("--text 和 --text-file 只能选一个")
    if not args.text and not args.text_file:
        raise ValueError("必须提供 --text 或 --text-file")
    if args.text:
        text = args.text.strip()
    else:
        text = Path(args.text_file).read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("输入文本不能为空")
    return text


def resolve_output_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mp3_out:
        mp3_path = Path(args.mp3_out).expanduser().resolve()
    else:
        base_name = args.out_name or datetime.now().strftime("guagua_%Y%m%d_%H%M%S")
        mp3_path = out_dir / f"{base_name}.mp3"

    if args.ogg_out:
        ogg_path = Path(args.ogg_out).expanduser().resolve()
    else:
        ogg_path = mp3_path.with_suffix(".ogg")

    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    ogg_path.parent.mkdir(parents=True, exist_ok=True)
    return mp3_path, ogg_path


def build_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def parse_env_value(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file(env_path: Path) -> dict[str, str]:
    env_map: dict[str, str] = {}
    if not env_path.is_file():
        return env_map

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        env_map[key] = parse_env_value(value)
    return env_map


def resolve_api_key(args: argparse.Namespace) -> str:
    if args.api_key:
        return args.api_key.strip()

    env_key = (os.getenv("MINIMAX_API_KEY") or "").strip()
    if env_key:
        return env_key

    env_candidates = [
        SCRIPT_DIR / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in env_candidates:
        file_key = load_env_file(env_path).get("MINIMAX_API_KEY", "").strip()
        if file_key:
            return file_key
    return ""


def should_inject_emotion_tags(model: str) -> bool:
    return model in {"speech-2.8-hd", "speech-2.8-turbo"}


def enhance_text_for_happy_mood(text: str, boost: str, model: str) -> str:
    if boost == "off":
        return text
    if not should_inject_emotion_tags(model):
        return text

    normalized = text.strip()
    if not normalized:
        return normalized

    if boost == "light":
        prefix = "(chuckle) "
        suffix = ""
    elif boost == "medium":
        prefix = "(laughs) "
        suffix = " (chuckle)" if normalized[-1] in {"！", "!"} else ""
    else:
        prefix = "(laughs) "
        suffix = " (laughs)"

    has_tag = any(tag in normalized for tag in ("(laughs)", "(chuckle)"))
    if has_tag:
        return normalized

    if normalized[-1] in {"。", ".", "！", "!", "？", "?"}:
        body = normalized[:-1]
        punctuation = normalized[-1]
        return f"{prefix}{body}{suffix}{punctuation}".strip()
    return f"{prefix}{normalized}{suffix}".strip()


def build_payload(text: str, args: argparse.Namespace) -> dict:
    payload = {
        "model": args.model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": args.voice_id,
            "speed": args.speed,
            "vol": args.vol,
            "pitch": args.pitch,
            "emotion": args.emotion,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": args.bitrate,
            "format": "mp3",
            "channel": 1,
        },
        "output_format": "hex",
        "subtitle_enable": args.subtitle_enable,
    }
    if args.group_id:
        payload["group_id"] = args.group_id
    return payload


def request_tts(text: str, args: argparse.Namespace, api_key: str) -> dict:
    req = request.Request(
        API_URL,
        data=json.dumps(build_payload(text, args)).encode("utf-8"),
        headers=build_headers(api_key),
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MiniMax 请求失败: HTTP {exc.code} {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"MiniMax 请求失败: {exc.reason}") from exc

    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("MiniMax 返回的不是合法 JSON") from exc

    base_resp = payload.get("base_resp") or {}
    if base_resp.get("status_code") not in (0, "0", None):
        status_msg = base_resp.get("status_msg") or "未知错误"
        raise RuntimeError(f"MiniMax 业务返回失败: {status_msg}")

    audio_hex = ((payload.get("data") or {}).get("audio") or "").strip()
    if not audio_hex:
        raise RuntimeError("MiniMax 返回里没有 data.audio")
    return payload


def save_mp3_from_hex(audio_hex: str, mp3_path: Path) -> None:
    try:
        audio_bytes = bytes.fromhex(audio_hex)
    except ValueError as exc:
        raise RuntimeError("返回的 audio 不是合法 hex 数据") from exc
    mp3_path.write_bytes(audio_bytes)


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("未找到 ffmpeg，请先安装 ffmpeg")
    if shutil.which("ffprobe") is None:
        raise RuntimeError("未找到 ffprobe，请先安装 ffmpeg 工具集")


def convert_mp3_to_ogg(mp3_path: Path, ogg_path: Path) -> None:
    ensure_ffmpeg()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(mp3_path),
        "-acodec",
        "libopus",
        "-sample_fmt",
        "s16",
        "-ac",
        "1",
        "-ar",
        "48000",
        str(ogg_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 转码失败:\n{result.stderr.strip()}")


def probe_audio(file_path: Path) -> str:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_name,sample_rate,channels,sample_fmt",
        "-of",
        "json",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe 校验失败:\n{result.stderr.strip()}")
    data = json.loads(result.stdout)
    stream = (data.get("streams") or [{}])[0]
    codec = stream.get("codec_name", "unknown")
    sample_rate = stream.get("sample_rate", "unknown")
    channels = stream.get("channels", "unknown")
    sample_fmt = stream.get("sample_fmt", "unknown")
    return f"codec={codec}, sample_rate={sample_rate}, channels={channels}, sample_fmt={sample_fmt}"


def main() -> int:
    args = parse_args()
    try:
        original_text = read_text(args)
        api_key = resolve_api_key(args)
        if not api_key:
            raise RuntimeError("缺少 API Key，请传 --api-key 或设置 MINIMAX_API_KEY")
        text = enhance_text_for_happy_mood(original_text, args.happy_boost, args.model)

        mp3_path, ogg_path = resolve_output_paths(args)
        payload = request_tts(text, args, api_key)
        audio_hex = payload["data"]["audio"]
        save_mp3_from_hex(audio_hex, mp3_path)
        convert_mp3_to_ogg(mp3_path, ogg_path)
        ogg_info = probe_audio(ogg_path)
        mp3_kept = args.keep_mp3
        if not args.keep_mp3 and mp3_path.exists():
            mp3_path.unlink()
            mp3_kept = False

        print(f"ogg 已生成: {ogg_path}")
        if mp3_kept:
            print(f"mp3 已保留: {mp3_path}")
        else:
            print("mp3 已删除")
        print(f"情绪参数: emotion={args.emotion}, speed={args.speed}, pitch={args.pitch}, happy_boost={args.happy_boost}")
        print(f"实际送审文本: {text}")
        print("目标转码参数: codec=opus, sample_rate=48000, channels=1, sample_fmt=s16")
        print(f"文件实测规格: {ogg_info}")
        return 0
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
