# Changelog

All notable changes to the Chinese Surnames Open Dataset. Version numbers are also
published in `schema.json` consumers' interest — the two canonical URLs always serve
the latest release, so pin a local copy if you need reproducibility.

## 2.0 — 2026-11-15

Added two numeric fields, which is the change the v1 docs promised. Purely additive:
every v1 field name, order and value is unchanged, so existing consumers keep working.

- **`rank_num`** (`integer | null`) — `rank` was a display string (`"全国第 2 位"`),
  which forced anyone who wanted to sort to parse Chinese numerals with a regex. This
  is the same ranking as a number. `null` when there is no rank.
- **`population_est`** (`integer | null`) — population in persons (`101000000`),
  derived from `population` (`"约 1.01 亿人"`). `null` for `"人数稀少"` and for unknown
  values; never filled with 0.
- **Coverage figures corrected.** The docs previously said only 30 of 109 surnames
  have population data. The accurate breakdown is: 30 with an official 2020 national
  rank, 12 compound surnames with a population estimate but no rank, 18 recorded as
  `"人数稀少"`, 49 with no figure at all. The 12 estimates come from looser sources
  than the MPS report and should be cited with that caveat.
- `schema.json` added, plus `scripts/sync.py` (downloads and validates the canonical
  files) and a weekly GitHub Actions job that mirrors them into `data/`.

## 1.0 — 2026-11-13

First release: 109 records, 13 fields, JSON and CSV, CC BY 4.0.
