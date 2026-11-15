# Changelog

All notable changes to the Chinese Surnames Open Dataset. Version numbers are also
published in `schema.json` consumers' interest — the two canonical URLs always serve
the latest release, so pin a local copy if you need reproducibility.

## 2.1 — 2026-11-15

A documentation correction that needed a field to make it honest. **No rank and no
headcount changed**; what changed is the claim about where the headcounts came from.

While preparing a write-up of the "only 30 of 109 have population data" angle, five
adjacent pairs in the ranked subset turned out to be out of order — 林 (#18) carrying
a larger figure than 何 (#17), 高 #20 > 罗 #19, 宋 #24 > 谢 #23, 韩 #27 > 许 #26,
冯 #29 > 邓 #28. Chasing that led back to the primary document: the Ministry of Public
Security's 2020 national name report publishes a top-100 table of **ranks with no
headcounts**, and prints figures only in a separate section on common compound
surnames (欧阳 111.2万, 令狐 5.5万, 诸葛 4.8万 …). The v2.0 docs had attributed all 42
population figures to that report. They were not all from it.

- **`population_source`** (`string`) — new field, one of `mps2020`, `estimate`,
  `qualitative`, `""`. `mps2020` marks the 12 compound surnames whose figure is
  verbatim from the report; `estimate` marks the 30 ranked single-character surnames
  whose figure comes from other statistics of varying vintage; `qualitative` marks the
  18 recorded only as `"人数稀少"`; empty marks the 49 with no data.
- **Coverage paragraph rewritten** around that split, and an explicit warning added
  about the five inversions: sort on `rank_num`, use `population_est` for magnitude
  only. A short pandas snippet in the README lets a reader reproduce the five rows.
- `scripts/sync.py` validates the new field (enum membership, plus consistency:
  `mps2020` must carry a figure and no rank, `qualitative` must carry no number,
  `estimate` must carry a figure) and prints the inversion pairs on every run so a
  sixth one cannot appear quietly.
- `schema.json` gained the property and added it to `required`.

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
