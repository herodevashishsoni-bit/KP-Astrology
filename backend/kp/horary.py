"""Horary module (user decision #25; R6; magazines).

The question chart:
  - planets: the moment and place of the question;
  - Ascendant: the start of the division named by the number (1–249, R6; or 1–108, KSK
    magazines), or the actual rising degree when no number is given;
  - other cusps: Placidus cusps for the moment that degree rises at the place.
Judgment: Moon shows the question; the promise from the relevant cusp sub lord with the
horary retrograde rules (R6); timing from the significators, the dasa as if a child were
born now (MC_059), RPs at the question, and transits.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import dasa as D
from .chart import Chart, ayanamsa, cast, julday
from .matters import catalogue
from .rp import ruling_planets
from .significators import Engine
from .subs import fmt_dms, horary_point, lords_of
from .windows import pinpoint, promise, score_periods


def _time_when_rising(target_sid: float, around: datetime, lat: float, lon: float, aya_name: str) -> datetime:
    """Find a moment within ±12 h of `around` when the sidereal Ascendant equals target_sid."""
    best, best_d = around, 999.0
    t = around - timedelta(hours=12)
    while t < around + timedelta(hours=12):
        ch = cast(t, lat, lon, aya_name)
        d = (ch.cusps[0] - target_sid + 180) % 360 - 180
        if abs(d) < abs(best_d):
            best, best_d = t, d
        t += timedelta(minutes=4)
    # refine by bisection-like stepping
    step = timedelta(minutes=2)
    for _ in range(14):
        for cand in (best - step, best + step):
            ch = cast(cand, lat, lon, aya_name)
            d = (ch.cusps[0] - target_sid + 180) % 360 - 180
            if abs(d) < abs(best_d):
                best, best_d = cand, d
        step = step / 2
    return best


def horary_chart(question_utc: datetime, lat: float, lon: float, number: int | None = None,
                 scheme: int = 249, ayanamsa_name: str = "KSK") -> tuple[Chart, dict]:
    real = cast(question_utc, lat, lon, ayanamsa_name)
    if number is None:
        return real, {"method": "time of question", "asc": fmt_dms(real.cusps[0])}
    a, b = horary_point(number, scheme)
    when = _time_when_rising(a + 1e-6, question_utc, lat, lon, ayanamsa_name)
    houses = cast(when, lat, lon, ayanamsa_name)
    real.cusps = houses.cusps
    real.cusp_lords = [lords_of(c) for c in houses.cusps]
    for body in real.planets.values():
        body.house = real.house_of(body.lon)
    info = {"method": f"number {number} of {scheme}", "division": f"{fmt_dms(a)} – {fmt_dms(b)}",
            "division_lords": lords_of(a + 1e-6).as_dict(), "asc": fmt_dms(real.cusps[0])}
    return real, info


def judge(question_utc: datetime, lat: float, lon: float, matter_key: str, number: int | None = None,
          scheme: int = 249, ayanamsa_name: str = "KSK", years_ahead: float = 5.0) -> dict:
    ch, info = horary_chart(question_utc, lat, lon, number, scheme, ayanamsa_name)
    eng = Engine(ch)
    mats = {m.key: m for m in catalogue(ch)}
    m = mats[matter_key]
    rp = ruling_planets(ch, horary=True)
    moon = ch.planets["Moon"]
    moon_note = {"moon_house": moon.house, "star_lord": moon.lords.star, "sub_lord": moon.lords.sub,
                 "star_lord_signifies": sorted(eng.signified(moon.lords.star, 4)),
                 "sub_lord_signifies": sorted(eng.signified(moon.lords.sub, 4)),
                 "rule": "The Moon (mathi) shows the question in the querist's mind (magazines; R6)."}
    # dasa "as if a child were born now" (MC_059)
    periods = [p for p in D.periods(question_utc, moon.lon, 3, years_ahead + 1) if p.start < question_utc + timedelta(days=365.25 * years_ahead)]
    out_variants = []
    for v in m.variants:
        pr = promise(eng, *v.promise) if v.promise else None
        sc = sorted(score_periods(eng, m, v, periods, rps=rp["ruling_planets"]), key=lambda s: -s.score)
        wins = []
        seen = set()
        for s in sc:
            k = s.period.lords[:2]
            if k in seen:
                continue
            seen.add(k)
            wins.append({"lords": list(s.period.lords[:3]), "start": s.period.start.date().isoformat(),
                         "end": s.period.end.date().isoformat(), "score": s.score, "reasons": s.reasons,
                         "rp_lords": sorted(set(s.period.lords[:3]) & set(rp["ruling_planets"])),
                         "pinpoint": pinpoint(s.period.lords[:3], s.period.start, s.period.end, ayanamsa_name,
                                              agents={n: [a for a, _ in eng.node_agents(n)] for n in ("Rahu", "Ketu")})})
            if len(wins) >= 3:
                break
        out_variants.append({"houses": v.houses, "source": v.source, "promise": pr, "windows": wins})
    return {"question_utc": question_utc.isoformat(), "matter": m.title, "chart_info": info,
            "chart": ch.as_dict(), "ruling_planets": {k: v for k, v in rp.items() if k != "chart"},
            "moon": moon_note, "variants": out_variants,
            "retrograde_rules": "Horary: cusp sub lord in the star of a retrograde planet → denial; retrograde sub lord → "
                                "delay until direct; retrograde in the star of a retrograde planet → never; nodes exempt (R6)."}
