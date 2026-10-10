"""Vimshottari dasa from the Moon's exact longitude (kp-rules §1.8).

Levels: dasa, bhukti, antara, sookshma. Year length is configurable
(365.25 days by default; KSK's printed balances are used to check it).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .constants import DASA_YEARS, STAR_SPAN, TOTAL_YEARS, sequence_from, star_lord_of_index

YEAR_DAYS = 365.25
LEVEL_NAMES = ["dasa", "bhukti", "antara", "sookshma"]


@dataclass
class Period:
    lords: tuple[str, ...]          # (dasa,) or (dasa, bhukti) ...
    start: datetime
    end: datetime

    @property
    def lord(self) -> str:
        return self.lords[-1]

    def label(self) -> str:
        return "–".join(self.lords)

    def as_dict(self) -> dict:
        return {"lords": list(self.lords), "start": self.start.isoformat(), "end": self.end.isoformat()}


def balance(moon_lon: float) -> tuple[str, float, float]:
    """(first dasa lord, fraction of the star already passed, balance in years)."""
    star_i = int((moon_lon % 360) // STAR_SPAN)
    lord = star_lord_of_index(star_i)
    passed = ((moon_lon % 360) - star_i * STAR_SPAN) / STAR_SPAN
    return lord, passed, DASA_YEARS[lord] * (1 - passed)


def ymd(years: float) -> tuple[int, int, int]:
    """Balance as years/months/days the way the books print it (12×30-day months)."""
    y = int(years)
    rem = (years - y) * 12
    m = int(rem)
    d = int(round((rem - m) * 30))
    if d == 30:
        d, m = 0, m + 1
    if m == 12:
        m, y = 0, y + 1
    return y, m, d


def _subdivide(parent: Period, years_len: float) -> list[Period]:
    out = []
    t = parent.start
    total = (parent.end - parent.start)
    for lord in sequence_from(parent.lord):
        dur = total * (DASA_YEARS[lord] / TOTAL_YEARS)
        out.append(Period(parent.lords + (lord,), t, t + dur))
        t = t + dur
    out[-1].end = parent.end
    return out


def mahadasas(birth_utc: datetime, moon_lon: float, until_years: float = 120,
              year_days: float = YEAR_DAYS) -> list[Period]:
    lord, passed, _ = balance(moon_lon)
    # virtual start of the first dasa
    start = birth_utc - timedelta(days=passed * DASA_YEARS[lord] * year_days)
    out = []
    t = start
    seq = sequence_from(lord)
    i = 0
    while (t - birth_utc).days < until_years * year_days:
        l = seq[i % 9]
        end = t + timedelta(days=DASA_YEARS[l] * year_days)
        out.append(Period((l,), t, end))
        t = end
        i += 1
    return out


def periods(birth_utc: datetime, moon_lon: float, depth: int = 3, until_years: float = 120,
            year_days: float = YEAR_DAYS) -> list[Period]:
    """Flat list of periods at the given depth (1=dasa … 4=sookshma), starting from birth."""
    level = mahadasas(birth_utc, moon_lon, until_years, year_days)
    for _ in range(depth - 1):
        nxt = []
        for p in level:
            nxt.extend(_subdivide(p, year_days))
        level = nxt
    return [p for p in level if p.end > birth_utc]


def at(birth_utc: datetime, moon_lon: float, when: datetime, depth: int = 4,
       year_days: float = YEAR_DAYS) -> Period | None:
    level = mahadasas(birth_utc, moon_lon, 121, year_days)
    found = None
    for _ in range(depth):
        found = next((p for p in level if p.start <= when < p.end), None)
        if found is None:
            return None
        level = _subdivide(found, year_days)
    return found
