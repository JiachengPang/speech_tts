"""
Notes:
- By default, `prompt` comes from each item's "question". Pass --prompt to override with a constant string.
- `output` defaults to each item's "answer_gt" (override with --output-field).
- If --compute-duration is set, the script will try to read .wav durations. If files are missing/unreadable, it falls back to null.
- Input can be a JSON array or JSONL (one JSON object per line).
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Optional
import wave
import re

def load_items(path: str) -> List[Dict[str, Any]]:
    """Load input as JSON array; if that fails, try JSONL."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        raise ValueError("Top-level JSON is not a list.")
    except json.JSONDecodeError:
        # Try JSONL
        items = []
        for ln, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {ln}: {e}") from e
            items.append(obj)
        return items

def get_wav_duration_seconds(path: str) -> Optional[float]:
    """Get duration for a WAV file using the stdlib wave module."""
    try:
        with wave.open(path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate and frames:
                return round(frames / float(rate), 6)
    except Exception:
        return None
    return None

def resolve_audio_path(audio_path: str, audio_root: Optional[str]) -> str:
    """If audio_root is provided, join it with audio_path; else use audio_path as-is."""
    if audio_root:
        return os.path.join(audio_root, audio_path)
    return audio_path

def build_prompt_with_choices(item: Dict[str, Any]) -> str:
    """If override provided, use it; else build: 'question (A): choice_a. (B): choice_b. ...'"""
    q = (item.get("question") or "").strip()
    pieces = []

    # Include choices in A..Z order if present: choice_a, choice_b, ...
    letters = "abcd"
    for i, letter in enumerate(letters):
        key = f"choice_{letter}"
        if key in item:
            label = chr(ord('A') + i)  # A, B, C, ...
            val = str(item[key]).strip()
            # Ensure a trailing period for each choice piece
            if val and val[-1] not in ".!?":
                val = val + "."
            pieces.append(f"({label}): {val}")

    # Build final prompt
    if pieces:
        # Ensure the question ends with punctuation
        if q and q[-1] not in "?!:.":
            q = q + "?"
        return (q + " " + " ".join(pieces)).strip()
    else:
        return q  # fallback to just the question

def _iter_choices(item: Dict[str, Any]):
    """Yield tuples of (label_char, key, value) for choice_a..choice_z that exist."""
    letters = "abcd"
    for i, letter in enumerate(letters):
        key = f"choice_{letter}"
        if key in item and item[key] not in (None, ""):
            label = chr(ord('A') + i)  # A, B, C, ...
            yield (label, key, str(item[key]).strip())

def _normalize(s: str) -> str:
    """Lowercase, collapse whitespace, strip trailing punctuation for robust matching."""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".!?")
    return s.lower()


def build_output_with_letter(item: Dict[str, Any], output_field: str) -> str:
    """
    Return output text prefixed with its letter, e.g. "(B): Young adult."
    Tries to match:
      1) answer value equals a choice's text (case/space/punct-insensitive)
      2) answer value equals 'B'/'b' or 'choice_b'
    Falls back to raw field if no match.
    """
    raw = str(item.get(output_field, "")).strip()
    if raw == "":
        return raw

    raw_norm = _normalize(raw)
    choices = list(_iter_choices(item))

    # 1) Value-text match
    for label, _, val in choices:
        if _normalize(val) == raw_norm:
            out = val
            if out and out[-1] not in ".!?":
                out += "."
            return f"({label}): {out}"

    # 2) Letter or key match
    for label, key, val in choices:
        if raw_norm in {label.lower(), key.lower()}:
            out = val
            if out and out[-1] not in ".!?":
                out += "."
            return f"({label}): {out}"

    # 3) Fallback: keep raw but still add a period and no letter (unknown)
    if raw and raw[-1] not in ".!?":
        raw += "."
    return raw

def convert(
    items: List[Dict[str, Any]],
    split: str,
    split_path: str,
    flamingo_task: str,
    output_field: str,
    compute_duration: bool,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "split": split,
        "split_path": split_path,
        "flamingo_task": flamingo_task,
        "data": {}
    }

    for idx, item in enumerate(items):
        name = item.get("audio_path") or item.get("name")
        if not name:
            # If there's no audio_path, skip or raise; here we raise to avoid silent errors.
            raise KeyError(f"Item {idx} missing 'audio_path' (or 'name'). Full item: {item}")

        prompt = build_prompt_with_choices(item)
        output_value = build_output_with_letter(item, output_field)

        duration = None
        if compute_duration and name.lower().endswith(".wav"):
            actual_path = resolve_audio_path(name, split_path)
            if os.path.isfile(actual_path):
                duration = get_wav_duration_seconds(actual_path)
            else:
                print(f'no file found: {actual_path}')
                duration = None  # file missing; leave null

        out["data"][str(idx)] = {
            "name": name,
            "prompt": prompt,
            "output": output_value,
            "duration": duration
        }

    return out

def main():
    parser = argparse.ArgumentParser(description="Convert MCQ-style JSON to Flamingo-style JSON.")
    parser.add_argument("-i", "--input", default='vox_paradox_mcq.json', help="Path to input JSON (array) or JSONL file.")
    parser.add_argument("-o", "--output", default='test.json', help="Path to write output JSON.")
    parser.add_argument("--split", default="test", help="Value for 'split' in output JSON. Default: test")
    parser.add_argument("--split-path", default="/wekafs/ict/pangj/data/speech_benchmark_samples", help="Value for 'split_path' in output JSON.")
    parser.add_argument("--flamingo-task", default="VoxParadox-AQA", help="Value for 'flamingo_task'")
    parser.add_argument("--output-field", default="answer_gt", help="Which input field becomes 'output'. Default: answer_gt")
    parser.add_argument("--compute-duration", type=bool, default=True, help="Compute .wav duration if accessible.")

    args = parser.parse_args()

    try:
        items = load_items(args.input)
    except Exception as e:
        print(f"[ERROR] Failed to load input: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        out = convert(
            items=items,
            split=args.split,
            split_path=args.split_path,
            flamingo_task=args.flamingo_task,
            output_field=args.output_field,
            compute_duration=args.compute_duration,
        )
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        sys.exit(2)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[OK] Wrote: {args.output}")

if __name__ == "__main__":
    main()
