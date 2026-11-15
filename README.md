# Chinese Surnames Open Dataset

109 Chinese surnames as structured data — Mandarin pinyin with tone marks, the era each surname took shape, the founding ancestor recorded in the histories, place of origin, commanderies (郡望) and hall names (堂号), the 2020 national population rank, notable historical bearers, and a prose note on how the surname came to exist.

**Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)** — commercial use, modification and redistribution are all permitted; attribution plus a licence link is the only condition.

| | |
|---|---|
| JSON | <https://naming-cn.pages.dev/data/surnames.json> (84 KB) |
| CSV  | <https://naming-cn.pages.dev/data/surnames.csv> (19 KB, UTF-8 with BOM) |
| Docs (English) | <https://naming-cn.pages.dev/en/chinese-surnames-dataset> |
| Docs (中文) | <https://naming-cn.pages.dev/opendata> |
| Version | 2.0 (2026-11-15) |

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
```

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
  "notables": ["李耳（老子）", "李广", "李世民", "李白", "李时珍"],
  "origin_note": "嬴姓。舜时皋陶任大理（掌刑狱），子孙以官为氏称「理」。……遂改「理」为「李」。",
  "url": "https://naming-cn.pages.dev/xing/li3"
}
```

## Schema

15 fields. Field names are English; free-text values (ancestor names, place names, the origin narrative) are Chinese, because the source literature is Chinese.

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
| `notables` | string[] | Historical bearers |
| `origin_note` | string | Prose account of the surname's origins (Chinese) |
| `url` | string | Full detail page for that surname |

A machine-readable [`schema.json`](schema.json) (JSON Schema draft-07) is included.

## Coverage and known gaps

Read these before you trust a join.

- **Official population ranks cover only 30 of 109.** The Ministry of Public Security's 2020 national name report publishes ranks and sizes for the top 100 surnames; nothing official exists below that. A further **12** records — all compound surnames — carry a population estimate but no rank, because they fall outside that top 100; those figures come from looser sources than the MPS report. **18** are marked `"人数稀少"` (recorded as rare, no figure) and **49** are empty.
- **Null means unknown, not zero.** `rank_num` and `population_est` are `null` in all of those cases. An empty string means the same for `rank` and `population`. Please do not coerce to 0 — it silently breaks sums, averages and sorts.
- **Compound surnames must not be split.** 欧阳 is not "a surname 欧 followed by 阳", and 万俟 is read *mò qí*, not *wàn sì*. `surname` holds one or two characters; `slug` is the join key.
- **Multiple origins are the norm.** A large surname usually descends from several unrelated lines at once. `origin_note` states the branches in parallel rather than forcing a single root; where `ancestor` names two people, that is a documented disagreement, not a typo.
- **Commanderies and hall names are literary, not census data.** Commanderies follow surname books such as the *Genealogical Tables of the Chancellors* in the New Book of Tang and the *Yuanhe Surname Compilation*; hall names come from clan genealogies and ancestral halls. Different branches of one surname use different halls, so the field lists the most frequently cited ones, not all.
- **This is not the 109 most common surnames.** The set is the surnames that already have a full detail page on the site, which is why rare compounds sit next to 王 and 李.

## Versioning

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
Chinese Naming (2026). Chinese Surnames Open Dataset, v2.0.
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

## 中文摘要

本站把 109 个姓氏详情页里的结构化信息抽成机器可读的数据集：拼音、得姓时代、得姓始祖、发源地、郡望、堂号、2020 年全国人口排名与人口估算、史籍所见名人、得姓源流说明，以及站内详情页地址。

- 数据文件：<https://naming-cn.pages.dev/data/surnames.json> 与 `surnames.csv`（UTF-8 带 BOM，Excel 直开不乱码）
- 说明页：<https://naming-cn.pages.dev/opendata>
- 授权：**CC BY 4.0**，可商用、可修改、可再分发，署名并附许可链接即可
- **空值表示「未知」，不是 0**：只有 30 个姓有官方全国排名（公安部 2020 年报告只公布前 100），另 12 个复姓有人口估算但无排名，18 个标为「人数稀少」，49 个空缺
- 姓氏源流多源并存，数据并列保留异说、不做裁决，用于学术研究请回原始文献核对
