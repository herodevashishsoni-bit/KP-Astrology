"""Sign / star / sub / sub-sub lords of any zodiac degree, and the 249 table.

Each star (13°20') is divided into 9 subs in Vimshottari proportion, starting
with the star lord (R3 ch.1). Subs cut by a sign boundary give 249 divisions
(R6), which are also the horary numbers 1–249.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .constants import (DASA_YEARS, SIGN_LORDS, SIGNS, STAR_SPAN, STARS, TOTAL_YEARS,
                        sequence_from, star_lord_of_index)


@dataclass(frozen=True)
class Lords:
    sign: str
    star: str
    sub: str
    subsub: str
    sign_name: str
    star_name: str
    star_index: int

    def as_dict(self) -> dict:
        return {"sign": self.sign, "star": self.star, "sub": self.sub, "subsub": self.subsub,
                "sign_name": self.sign_name, "star_name": self.star_name}


def _divide(start: float, span: float, first_lord: str) -> list[tuple[float, float, str]]:
    out = []
    pos = start
    for lord in sequence_from(first_lord):
        w = span * DASA_YEARS[lord] / TOTAL_YEARS
        out.append((pos, pos + w, lord))
        pos += w
    return out


def lords_of(lon: float) -> Lords:
    lon = lon % 360.0
    sign_i = int(lon // 30)
    star_i = int(lon // STAR_SPAN)
    star_lord = star_lord_of_index(star_i)
    sub_lord = subsub = star_lord
    for a, b, lord in _divide(star_i * STAR_SPAN, STAR_SPAN, star_lord):
        if a <= lon < b or (lord == sequence_from(star_lord)[-1] and lon >= a):
            sub_lord = lord
            for a2, b2, l2 in _divide(a, b - a, lord):
                if a2 <= lon < b2:
                    subsub = l2
                    break
            else:
                subsub = sequence_from(lord)[-1]
            break
    return Lords(SIGN_LORDS[sign_i], star_lord, sub_lord, subsub, SIGNS[sign_i], STARS[star_i], star_i)


@lru_cache(maxsize=1)
def table_249() -> list[dict]:
    """The 249 divisions (number → start, end, sign/star/sub lords)."""
    rows = []
    for star_i in range(27):
        lord = star_lord_of_index(star_i)
        for a, b, sub in _divide(star_i * STAR_SPAN, STAR_SPAN, lord):
            cut = (int(a // 30) + 1) * 30.0
            pieces = [(a, b)] if not (a < cut < b - 1e-9) else [(a, cut), (cut, b)]
            for x, y in pieces:
                rows.append({"start": round(x, 6), "end": round(y, 6),
                             "sign": SIGN_LORDS[int((x + 1e-9) // 30) % 12], "star": lord, "sub": sub})
    for n, r in enumerate(rows, 1):
        r["number"] = n
    return rows


def horary_point(number: int, scheme: int = 249) -> tuple[float, float]:
    """Return the (start, end) longitude for a horary number."""
    if scheme == 249:
        if not 1 <= number <= 249:
            raise ValueError("number must be 1–249")
        r = table_249()[number - 1]
        return r["start"], r["end"]
    if scheme == 108:
        if not 1 <= number <= 108:
            raise ValueError("number must be 1–108")
        span = 360.0 / 108
        return (number - 1) * span, number * span
    raise ValueError("scheme must be 249 or 108")


def fmt_dms(lon: float, in_sign: bool = True) -> str:
    lon = lon % 360.0
    v = lon % 30 if in_sign else lon
    d = int(v)
    m_f = (v - d) * 60
    m = int(m_f)
    s = int(round((m_f - m) * 60))
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    sign = f" {SIGNS[int(lon // 30)][:3]}" if in_sign else ""
    return f"{d}°{m:02d}′{s:02d}″{sign}"
