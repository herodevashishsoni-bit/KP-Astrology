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
