# Engine validation log

The harness lives in `backend/tests/validate.py`, `experiment.py` and `experiment2.py`. The cases are in `backend/tests/cases.py`: confirmed events with birth data, from the Readers and magazines.

## Run 1 (first engine build)

**Casting.**
- Alibag 23-12-1924, 9 PM (R5-A): cusps within 8′ of the printed values; planets within 1–6′.
- Jullundur 31-10-1919, 3:53:48 AM: Asc 6°52′ Virgo (printed 6°53′).

**Ayanamsa.** KSK matches every printed value within about 1′ for 1913–1968. In 1970 we get 23°21′ against the printed 23°23′.

**Dasa.**
- Balances: R5-J 1y10m15d (printed 1y10m12d); Indira 1y9m24d (printed 1y10m12d); Bhattacharya 19y2m22d (printed 19y1m15d).
- The event periods agree with the printed D–B–A for 18 of 26 events. Every mismatch is either a period boundary or a doubtful birth record:
  - Kennedy: printed balance Venus 3y5m3d; ours 3y1m5d.
  - M-05: the printed balance doesn't fit the birth date, so the case was removed.

**Window ranking.** The question: where does the actual event's window rank among all the windows of a 100-year life? The best source variant is taken for each event, over 25 events.

| Method | Hits in top 3 | Hits in top 10 | Median rank |
|---|---|---|---|
| Sum of significator levels + fruitful sub + negation (KSK ayanamsa) | 4 | 8 | 22 |
| Same, Lahiri | 3 | 7 | 22 |
| KSK "strong significators only" (stop at 3–4 planets) | 3 | 6 | 33 |

There are about 75 distinct dasa–bhukti pairs in 100 years, so a random choice would give a median rank of about 37.

**Finding.** Most planets signify at least one of a matter's 3–4 houses. So ranking a whole life on house signification alone separates poorly. In the published cases KSK predicted near the time of the question and chose between the candidates with the **ruling planets at that moment**. The bio has no such moment.

What helps within the source rules:
- the age bands the sources do give (first job at ages 16–30, R3; the longevity span for death);
- the user entering known events, which checks the birth time and fixes the one-time events;
- the RPs at the moment the user asks about a specific matter, KSK's own method.

Status: the sum method is the default. Ranking quality is reported honestly in the app.

## Run 2: timing investigation (42 events, 34 with verified data)

**Data check.** An event counts as "verified" when our dasa–bhukti at the event equals the printed one, or when nothing is printed. 8 events failed this check: the printed birth data is probably damaged (e.g. Madras-1929, where the source says Rahu–Ketu and we compute Mercury–Venus). Those were left out of tuning.

**Diagnostic** (`backend/tests/diag.py`). For each source-based criterion: how often does the actual event period pass it, and what share of all life periods pass it? Lift = hit rate ÷ share of periods passing; 1.0 means no better than chance.

| Criterion | Event periods passing | Share of life passing | Lift |
|---|---|---|---|
| D, B, A all signify the houses (levels 1–4) | 25/34 | 0.68 | 1.08 |
| D, B, A all signify at levels 1–2 | 10/34 | 0.27 | 1.08 |
| B and A among the strongest significators (KSK selection) | 12/34 | 0.35 | 1.02 |
| D, B, A signify, with fruitful sub lords | 21/34 | 0.58 | 1.06 |
| Star and sub lords of D, B, A signify | 23/34 | 0.56 | 1.21 |
| Cusp sub lord or its star lord among D, B, A | 11/34 | 0.33 | 0.98 |
| Negation filters (12th houses) | — | — | 0.0–1.15 |

**Finding.** Applied over a whole life, the significator rules hardly separate the event period from other periods. Each planet signifies 4–6 of the 12 houses, so most periods qualify for most matters. In the books KSK never ranked a whole life. He judged at the moment someone asked, and the ruling planets of that moment picked the period.

**Question-time test (horary module, 3-year horizon).** The actual date was in the top 3 windows for 3 of 4 confirmed cases:
- brokerage: rank 1;
- Kulu transfer: rank 3;
- Gaya transfer: rank 1–3, depending on the source version;
- Chopra promotion: missed (the order came within 3 weeks; finer sub-periods are needed).

**Change made.** Timing is now KSK's method, "When? Ask now" for one matter (`kp.windows.ask_now`):
- every one of the dasa, bhukti and antara lords must signify the matter;
- the ruling planets of the moment must be among the bhukti or antara lords;
- the earliest strong period comes first.

The whole-life lists remain only as "periods when the matter is active", not predictions.

**Limit.** The ruling planets are the same for every question asked at the same moment. So the method distinguishes matters only when they are asked one at a time, as KSK's clients did.

## Run 3: user chart (Devashish Soni, 16-12-1999 8:07 PM IST, Ajmer)

- **Ask now, first earning (job, houses 2/6/10):** asked 10-10-2026 4:33 PM IST, Jaipur. Ruling planets: Jupiter, Saturn, Moon, Mercury, Rahu.
  - #1: Mercury–Jupiter–Moon, 17-10-2026 to 25-12-2026; Sun-transit dates 16 and 20 Dec 2026.
  - #2: Mercury–Saturn–Mercury, 18-11-2027 to 5-4-2028.
  - The promise is "promised" (10th cusp sub lord Jupiter).
  - Prediction, to be checked.
- **Known events:**
  - Class 10 (2015, Mer–Mer–Sat) and Class 12 (2017, Mer–Ven–Moon) both fit education houses 4/9/11.
  - The younger siblings' births (24-11-2001, 23-6-2005) fit only weakly or partly: rule 3 (or 5 for the 2nd younger) with 2 and 11.
- **Birth time:** RP rectification at the judgment moment gives 8:05:30–8:06:30 PM IST (Cancer 3°21′–3°34′, Moon / Saturn / Saturn / Saturn). The recorded 8:07 PM is in the same sub. The event scan also favours 8:06–8:09 PM.
- **User's actual jobs:** Oct 2024 (~2 months), Sep 2025 (~1.5 months), ~Feb–Apr 2026. Antara rule (R4 p.118, fruitful significator): the antara lord signifies 2, 6 or 10 AND its sub lord does too.
  - 9 of 10 antaras from Apr 2024 to Oct 2026 match. The job antaras are Rahu–Moon, Jupiter–Saturn and Jupiter–Ketu.
  - Jupiter–Mercury qualifies, but the job began only in its last month.
  - The ends of the jobs fall at antara boundaries.
  - Next qualifying antara: Mercury–Jupiter–Moon, from 17-10-2026, the same as ask-now #1.
  - This antara rule did not stand out over whole lives in the book cases (lift 1.06), so a dated-event test on more charts is needed before it becomes the default.
