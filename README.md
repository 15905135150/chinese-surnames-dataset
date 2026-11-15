# Chinese Surnames Open Dataset

109 Chinese surnames as structured data — Mandarin pinyin with tone marks, the era each surname took shape, the founding ancestor recorded in the histories, place of origin, commanderies (郡望) and hall names (堂号), the 2020 national population rank, notable historical bearers, and a prose note on how the surname came to exist.

**Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)** — commercial use, modification and redistribution are all permitted; attribution plus a licence link is the only condition.

| | |
|---|---|
| JSON | <https://naming-cn.pages.dev/data/surnames.json> (87 KB) |
| CSV  | <https://naming-cn.pages.dev/data/surnames.csv> (19 KB, UTF-8 with BOM) |
| Docs (English) | <https://naming-cn.pages.dev/en/chinese-surnames-dataset> |
| Docs (中文) | <https://naming-cn.pages.dev/opendata> |
| Version | 2.1 (2026-11-15) |

Both files are served with `Access-Control-Allow-Origin: *`, so a plain browser `fetch` works — no key, no signup, no proxy.

---

## Quick start

Shell:

```bash
curl -s https://naming-cn.pages.dev/data/surnames.json \
  | jq -r 'sort_by(.rank_num // 999) | .[] | select(.rank_num) | "\(.rank_num)\t\(.surname)\t\(.pinyin)"'
```

Python:

```python
import pandas as pd

df = pd.read_csv("https://naming-cn.pages.dev/data/surnames.csv")
ranked = df.dropna(subset=["rank_num"]).sort_values("rank_num")   # 30 rows
populated = df.dropna(subset=["population_est"])                  # 42 rows
official = df[df["population_source"] == "mps2020"]               # 12 rows, verbatim from the report
```

Two columns describe population and they are **not** from the same survey. Sort on `rank_num`; treat `population_est` as a magnitude, and filter on `population_source` before quoting a number as official.

JavaScript:

```js
const rows = await fetch("https://naming-cn.pages.dev/data/surnames.json")
  .then(r => r.json());

const byRank = rows.filter(r => r.rank_num)
  .sort((a, b) => a.rank_num - b.rank_num);
const li = rows.find(r => r.surname === "李");
const liPrefix = rows.filter(r => /^li/.test(r.slug)); // li3, liang2, liao4, lin2, liu2 …
```

## What a record looks like

```json
{
  "surname": "李",
  "slug": "li3",
  "pinyin": "lǐ",
  "era": "商末",
  "ancestor": "李利贞（血缘始祖皋陶）",
  "origin": "河南鹿邑",
  "junwang": ["陇西", "赵郡"],
  "tanghao": [
    { "name": "陇西堂", "note": "以郡望立堂，出自陇西一系" },
    { "name": "青莲堂", "note": "李白自号青莲居士，后世一支取为堂号" }
  ],
  "rank": "全国第 2 位",
  "rank_num": 2,
  "population": "约 1.01 亿人",
  "population_est": 101000000,
  "population_source": "estimate",
  "notables": ["李耳（老子）", "李广", "李世民", "李白", "李时珍"],
  "origin_note": "嬴姓。舜时皋陶任大理（掌刑狱），子孙以官为氏称「理」。……遂改「理」为「李」。",
  "url": "https://naming-cn.pages.dev/xing/li3"
}
```

## Schema

16 fields. Field names are English; free-text values (ancestor names, place names, the origin narrative) are Chinese, because the source literature is Chinese.

| Field | Type | Notes |
|---|---|---|
| `surname` | string | One character, or two for a compound surname (欧阳, 司马, 万俟) |
| `slug` | string | Tone-numbered pinyin, doubles as the URL key: `li3`, `ouyang2`, `moqi2` |
| `pinyin` | string | Mandarin reading with tone marks |
| `era` | string | Period in which the surname mainly took shape, e.g. `商末`, `西周` |
| `ancestor` | string | Founding ancestor; when the sources disagree both readings are kept |
| `origin` | string | Place of origin as a modern administrative location |
| `junwang` | string[] | Commanderies — regions where a clan branch rose to prominence |
| `tanghao` | object[] | Hall names, each `{ name, note }` with the derivation |
| `rank` | string | Population rank as a display string, e.g. `"全国第 2 位"`; empty when none |
| `rank_num` | integer \| null | The same rank as a number. **Sort on this one** |
| `population` | string | Estimate as published, e.g. `"约 1.01 亿人"`; `"人数稀少"` = recorded as rare |
| `population_est` | integer \| null | Estimate in persons, e.g. `101000000`. Never filled with 0 |
| `population_source` | string | Where the population figure came from — `mps2020`, `estimate`, `qualitative`, or empty. Read this before quoting a number |
| `notables` | string[] | Historical bearers |
| `origin_note` | string | Prose account of the surname's origins (Chinese) |
| `url` | string | Full detail page for that surname |

A machine-readable [`schema.json`](schema.json) (JSON Schema draft-07) is included.

## Coverage and known gaps

Read these before you trust a join.

- **The two population columns do not come from the same source, and only one of them is official.** The Ministry of Public Security's 2020 national name report publishes a top-100 ranking table — **ranks, no headcounts**. The only figures it prints are in a separate section on common compound surnames (欧阳 1.112 million, 令狐 55,000, 诸葛 48,000 …). So the split is: **30** records with a national rank but a population figure from elsewhere (`population_source = estimate`, vintage varies), **12** compound surnames whose figure is verbatim from the report (`mps2020`) but which carry no rank because they fall outside the top 100, **18** marked `"人数稀少"` (recorded as rare, no figure), and **49** empty. Read `population_source` before you quote a number as official.
- **Sorting by `population_est` contradicts the official ranking in 5 adjacent pairs.** 林 (#18) carries a larger figure than 何 (#17); likewise 高 #20 > 罗 #19, 宋 #24 > 谢 #23, 韩 #27 > 许 #26, 冯 #29 > 邓 #28. Those are not typos and not a sort bug — the rank comes from the 2020 report and the headcounts come from other, differently-dated estimates. Sort on `rank_num`; use `population_est` for order of magnitude only. `scripts/sync.py` prints these pairs on every run so a new one cannot slip in unnoticed.
- **Null means unknown, not zero.** `rank_num` and `population_est` are `null` in all of those cases. An empty string means the same for `rank` and `population`. Please do not coerce to 0 — it silently breaks sums, averages and sorts.
- **Compound surnames must not be split.** 欧阳 is not "a surname 欧 followed by 阳", and 万俟 is read *mò qí*, not *wàn sì*. `surname` holds one or two characters; `slug` is the join key.
- **Multiple origins are the norm.** A large surname usually descends from several unrelated lines at once. `origin_note` states the branches in parallel rather than forcing a single root; where `ancestor` names two people, that is a documented disagreement, not a typo.
- **Commanderies and hall names are literary, not census data.** Commanderies follow surname books such as the *Genealogical Tables of the Chancellors* in the New Book of Tang and the *Yuanhe Surname Compilation*; hall names come from clan genealogies and ancestral halls. Different branches of one surname use different halls, so the field lists the most frequently cited ones, not all.
- **This is not the 109 most common surnames.** The set is the surnames that already have a full detail page on the site, which is why rare compounds sit next to 王 and 李.

### Checking the inversions yourself

```python
df = df.dropna(subset=["rank_num", "population_est"]).sort_values("rank_num")
prev = df.shift(1)
bad = df[df["population_est"] > prev["population_est"]]
print(bad[["surname", "rank_num", "population_est", "population_source"]])
```

Five rows: 林, 高, 宋, 韩, 冯. If a sixth appears, the rank column and the estimate column have drifted further apart than the dataset admits to.

## Versioning

`2.1` — added `population_source` (additive) and corrected the provenance documentation. No rank or headcount changed; what changed is the claim that the headcounts came from the 2020 MPS report. They did not — that report ranks the top 100 without printing sizes, and the only figures it prints are for compound surnames.
`2.0` — added `rank_num` and `population_est` (both additive; every v1 field is unchanged).
`1.0` — first release, 13 fields.

See [CHANGELOG.md](CHANGELOG.md). The two URLs above always serve the latest version; pin a copy locally if you need reproducibility.

## Files in this repo

```
README.md            this file
LICENSE              CC BY 4.0, with the attribution string
CHANGELOG.md         version history
schema.json          JSON Schema for one record of surnames.json
scripts/sync.py      downloads the canonical files into data/ and validates them
data/surnames.json   mirrored copy (see note below)
data/surnames.csv    mirrored copy (see note below)
.github/workflows/   weekly sync job
```

The **canonical** files live on the site. `data/` here is a convenience mirror refreshed by the sync workflow, so it can lag by up to a week. If you need the current release, fetch from `naming-cn.pages.dev`; if you want a stable copy to diff against, use this repo.

## Citation

```
Chinese Naming (2026). Chinese Surnames Open Dataset, v2.1.
https://naming-cn.pages.dev/en/chinese-surnames-dataset (CC BY 4.0)
```

BibTeX:

```bibtex
@misc{chinesenaming_surnames_2026,
  title  = {Chinese Surnames Open Dataset},
  author = {{Chinese Naming}},
  year   = {2026},
  note   = {109 records, CC BY 4.0},
  url    = {https://naming-cn.pages.dev/en/chinese-surnames-dataset}
}
```

## Corrections

Genuinely welcome, especially from anyone who knows the genealogy literature better than this dataset does. Open an issue here or use the site's [message board](https://naming-cn.pages.dev/board). Verified fixes ship as a new version number.

## Write-ups

- [I published 109 Chinese surnames as open data — here are the awkward parts](https://dev.to/liuxj0416/i-published-109-chinese-surnames-as-open-data-here-are-the-awkward-parts-2976) — why compound surnames stay whole, why empty means unknown, why the BOM is deliberate.
- [My open dataset credited the wrong source for 30 numbers](https://dev.to/liuxj0416/my-open-dataset-credited-the-wrong-source-for-30-numbers-a-sort-order-gave-it-away-3kn9) — the v2.1 provenance fix, found by a monotonicity check on `population_est`.

## 中文摘要

本站把 109 个姓氏详情页里的结构化信息抽成机器可读的数据集：拼音、得姓时代、得姓始祖、发源地、郡望、堂号、2020 年全国人口排名与人口估算、史籍所见名人、得姓源流说明，以及站内详情页地址。

- 数据文件：<https://naming-cn.pages.dev/data/surnames.json> 与 `surnames.csv`（UTF-8 带 BOM，Excel 直开不乱码）
- 说明页：<https://naming-cn.pages.dev/opendata>
- 授权：**CC BY 4.0**，可商用、可修改、可再分发，署名并附许可链接即可
- **空值表示「未知」，不是 0**：只有 30 个姓有官方全国排名；2020 年公安部报告的「百家姓」表只排前 100、表内不列人数，另在「常见复姓」一节给出 12 个复姓的具体人数。18 个标为「人数稀少」，49 个空缺
- **人口数字分两种口径，别混用**：`population_source` 标明来源——`mps2020`（报告原文数字，仅 12 个复姓）、`estimate`（其他统计或估算，年份不一，30 个有排名的单姓）、`qualitative`（只有「人数稀少」定性）、空（无数据）。按 `population_est` 排序会出现 5 处相邻倒挂（林#18>何#17、高#20>罗#19、宋#24>谢#23、韩#27>许#26、冯#29>邓#28），排序请用 `rank_num`
- 姓氏源流多源并存，数据并列保留异说、不做裁决，用于学术研究请回原始文献核对
