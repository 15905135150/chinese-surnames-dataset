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
    "population_source",
    "notables",
    "origin_note",
    "url",
]

SOURCES = {"mps2020", "estimate", "qualitative", ""}

COMPOUND_MIN = 2  # at least one two-character surname must exist, else the extractor broke


def fetch(url: str, binary: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": "chinese-surnames-dataset-sync/2.1"})
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

        # v2.1: every population figure must say where it came from, and the
        # source must agree with the shape of the data it describes.
        src = rec["population_source"]
        if src not in SOURCES:
            fail(f"{where}: population_source must be one of {sorted(SOURCES)}, got {src!r}")
        if src == "mps2020":
            if rec["population_est"] is None:
                fail(f"{where}: mps2020 must carry a population_est")
            if rec["rank_num"] is not None:
                fail(
                    f"{where}: a ranked surname cannot be mps2020 — the 2020 report's "
                    "top-100 table lists ranks only, no headcounts"
                )
        elif src == "estimate":
            if rec["population_est"] is None:
                fail(f"{where}: estimate must carry a population_est")
        elif src == "qualitative":
            if rec["population_est"] is not None:
                fail(f"{where}: qualitative must not carry a number")
            if rec["population"] != "人数稀少":
                fail(f"{where}: qualitative implies population == '人数稀少', got {rec['population']!r}")
        elif src == "":
            if rec["population_est"] is not None or rec["population"]:
                fail(f"{where}: empty source but a population value is present")

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
    by_src = {s: sum(1 for r in rows if r["population_source"] == s) for s in ("mps2020", "estimate", "qualitative", "")}
    print(
        f"OK {len(rows)} records · {ranked} with a 2020 rank · {with_pop} with a population figure · {rare} marked rare"
    )
    print(
        "   provenance: "
        f"{by_src['mps2020']} mps2020 · {by_src['estimate']} estimate · "
        f"{by_src['qualitative']} qualitative · {by_src['']} none"
    )

    # The two population columns are not from the same survey, so ordering by
    # population_est disagrees with the official rank in a few adjacent pairs.
    # Surface them rather than letting a reader discover it by accident.
    ordered = sorted((r for r in rows if r["rank_num"] is not None and r["population_est"]), key=lambda r: r["rank_num"])
    inversions = [
        (a, b)
        for a, b in zip(ordered, ordered[1:])
        if b["population_est"] > a["population_est"]
    ]
    if inversions:
        pairs = ", ".join(f"{b['surname']}#{b['rank_num']} > {a['surname']}#{a['rank_num']}" for a, b in inversions)
        print(f"   note: {len(inversions)} adjacent inversion(s) when sorting by population_est — {pairs}")
        print("   sort on rank_num; use population_est for magnitude only")

    print(f"wrote {DATA / 'surnames.json'} and {DATA / 'surnames.csv'}")


if __name__ == "__main__":
    main()
