#!/usr/bin/env python3
"""Mirror the canonical Chinese Surnames dataset into data/ and validate it.

Canonical source: https://naming-cn.pages.dev/data/
Licence: CC BY 4.0 — attribution plus a licence link is the only condition.

Run locally:   python scripts/sync.py
Run in CI:     .github/workflows/sync-data.yml (weekly, or on demand)

Exit codes: 0 ok, 1 validation failed, 2 download failed.
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.request

BASE = "https://naming-cn.pages.dev"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FIELDS = [
    "surname",
    "slug",
    "pinyin",
    "era",
    "ancestor",
    "origin",
    "junwang",
    "tanghao",
    "rank",
    "rank_num",
    "population",
    "population_est",
    "notables",
    "origin_note",
    "url",
]

COMPOUND_MIN = 2  # at least one two-character surname must exist, else the extractor broke


def fetch(url: str, binary: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": "chinese-surnames-dataset-sync/2.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    return raw if binary else raw.decode("utf-8")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def validate(rows) -> None:
    if not isinstance(rows, list) or not rows:
        fail("surnames.json is not a non-empty array")

    for i, rec in enumerate(rows):
        where = f"row {i} ({rec.get('surname', '?')})"
        missing = [f for f in FIELDS if f not in rec]
        extra = [k for k in rec if k not in FIELDS]
        if missing or extra:
            fail(f"{where}: missing={missing} extra={extra}")

        if not isinstance(rec["surname"], str) or not 1 <= len(rec["surname"]) <= 2:
            fail(f"{where}: surname must be 1–2 characters")
        if not isinstance(rec["junwang"], list) or not isinstance(rec["notables"], list):
            fail(f"{where}: junwang/notables must be arrays")
        if not isinstance(rec["tanghao"], list):
            fail(f"{where}: tanghao must be an array")
        for hall in rec["tanghao"]:
            if set(hall) != {"name", "note"}:
                fail(f"{where}: each tanghao entry needs exactly name+note")

        # The whole point of v2: numbers are numbers, and unknown is null — never 0.
        if rec["rank_num"] is not None and not isinstance(rec["rank_num"], int):
            fail(f"{where}: rank_num must be int or null")
        if rec["population_est"] is not None and not isinstance(rec["population_est"], int):
            fail(f"{where}: population_est must be int or null")
        if rec["rank_num"] == 0 or rec["population_est"] == 0:
            fail(f"{where}: zero is not a valid unknown value — use null")
        if rec["rank_num"] is None and rec["rank"]:
            fail(f"{where}: rank says {rec['rank']!r} but rank_num is null")
        if rec["rank_num"] is not None and not rec["rank"]:
            fail(f"{where}: rank_num is set but rank is empty")

    ranks = [r["rank_num"] for r in rows if r["rank_num"] is not None]
    if len(ranks) != len(set(ranks)):
        fail("duplicate rank_num values — the ranking is meant to be a permutation")

    if not any(len(r["surname"]) >= COMPOUND_MIN for r in rows):
        fail("no compound surnames found — the upstream extractor likely broke")


def main() -> None:
    try:
        rows = json.loads(fetch(f"{BASE}/data/surnames.json"))
        csv_bytes = fetch(f"{BASE}/data/surnames.csv", binary=True)
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: download error: {e}", file=sys.stderr)
        sys.exit(2)

    validate(rows)

    if not csv_bytes.startswith(b"\xef\xbb\xbf"):
        fail("CSV lost its UTF-8 BOM — Excel on Chinese Windows would show mojibake")

    DATA.mkdir(exist_ok=True)
    (DATA / "surnames.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (DATA / "surnames.csv").write_bytes(csv_bytes)

    ranked = sum(1 for r in rows if r["rank_num"] is not None)
    with_pop = sum(1 for r in rows if r["population_est"] is not None)
    rare = sum(1 for r in rows if r["population"] == "人数稀少")
    print(f"OK {len(rows)} records · {ranked} with a 2020 rank · {with_pop} with a population figure · {rare} marked rare")
    print(f"wrote {DATA / 'surnames.json'} and {DATA / 'surnames.csv'}")


if __name__ == "__main__":
    main()
