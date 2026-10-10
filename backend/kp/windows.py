"""Promise (cusp sub lord) and time windows for every matter (kp-rules §3–4).

Scoring is an APP CHOICE (§4.2), built only from source rules:
  - dasa supremacy: the dasa lord must signify the matter (R3; magazines)
  - each lord scored by significator level (level 1 = 6 pts … level 6 = 1 pt)
  - fruitful bonus when a lord's sub lord also signifies the houses (R4 p.118)
  - penalty when the lord signifies the negating houses (R4 p.118, p.150)
  - A–B–A "full extent" pattern bonus (R3 l.~9560)
  - Western aspect between dasa and bhukti lords (R3 (e)–(h); decision #2)
  - small tie-break for ruling planets at generation time (decision #19)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import swisseph as swe

from . import dasa as D
from .aspects import western_between
from .chart import Chart, julday
from .constants import EXALTATION, DEBILITATION, SIGN_QUALITY
from .matters import Matter, Variant, badhaka_from, catalogue
from .significators import Engine
from .subs import lords_of


# ---------------------------------------------------------------- promise
def promise(engine: Engine, cusp: int, good: list[int], bad: list[int]) -> dict:
    ch = engine.chart
    cl = ch.cusp_lords[cusp - 1]
    sl = cl.sub
    out = {"cusp": cusp, "cusp_sign_lord": cl.sign, "cusp_star_lord": cl.star, "sub_lord": sl,
           "sub_lord_star": ch.planets[sl].lords.star, "variants": []}
    for mode, src in (("standard", "R3/R4: sub lord judged through its star lord, occupation and ownership"),
                      ("own", "Magazines: sub lord judged by the houses it occupies and owns only")):
        hs = engine.sub_lord_houses(sl, mode)
        g, b = sorted(hs & set(good)), sorted(hs & set(bad))
        if g and not b:
            verdict = "promised"
        elif b and not g:
            verdict = "denied"
        elif g and b:
            verdict = "promised with obstacles"
        else:
            verdict = "not indicated"
        out["variants"].append({"mode": mode, "source": src, "houses": sorted(hs), "good": g, "bad": b,
                                "verdict": verdict})
    # natal retrogression variant (decision #5: show both)
    b = ch.planets[sl]
    retro_note = None
    if sl not in ("Rahu", "Ketu"):
        if b.retro and ch.planets[b.lords.star].retro:
            retro_note = "Sub lord retrograde and in the star of a retrograde planet → never (R6 horary rule applied to natal)"
        elif ch.planets[b.lords.star].retro:
            retro_note = "Sub lord in the star of a retrograde planet → denial (R6 horary rule applied to natal)"
        elif b.retro:
            retro_note = "Sub lord retrograde → delay until it turns direct (R6 horary rule applied to natal)"
    out["retrograde_variant"] = retro_note or "No retrogression involved."
    out["retrograde_ignored_note"] = "KSK MC_139: natal retrogression makes no difference."
    return out


def longevity_span(engine: Engine) -> dict:
    """Span from the Ascendant sub lord (R3)."""
    ch = engine.chart
    sl = ch.cusp_lords[0].sub
    dh = set([badhaka_from(ch, 1), 2, 7])
    star = ch.planets[sl].lords.star
    star_sig = engine.signified(star, 4)
    if star_sig & dh:
        band, why = "short (0–33)", f"Ascendant sub lord {sl} is in the star of {star}, a significator of badhaka/maraka houses {sorted(star_sig & dh)}"
    else:
        hs = engine.sub_lord_houses(sl)
        good, bad = hs & {1, 5, 9, 10}, hs & {6, 8, 12}
        if good and not bad:
            band, why = "long (66–100)", f"Ascendant sub lord {sl} signifies {sorted(good)}"
        elif bad and not good:
            band, why = "short (0–33)", f"Ascendant sub lord {sl} signifies {sorted(bad)}"
        else:
            band, why = "middle (33–66)", f"Ascendant sub lord {sl} signifies both {sorted(good)} and {sorted(bad)}"
    ranges = {"short (0–33)": (0, 33), "middle (33–66)": (33, 66), "long (66–100)": (66, 100)}
    return {"sub_lord": sl, "band": band, "reason": why, "years": ranges[band],
            "source": "R3 p.157–169 (bands R3 l.~7200)"}


# ---------------------------------------------------------------- windows
@dataclass
class Scored:
    period: D.Period
    score: float
    reasons: list[str]


def _lord_score(engine: Engine, lord: str, v: Variant, matter: Matter) -> tuple[float, list[str]]:
    s, used = engine.strength(lord, v.houses, weights=v.weights)
    reasons = [x.reason for x in used[:2]]
    if s <= 0:
        return 0.0, reasons
    sub = engine.chart.planets[lord].lords.sub
    sub_hs = engine.sub_lord_houses(sub)
    if sub_hs & set(v.houses):
        s += 2
        reasons.append(f"{lord}'s sub lord {sub} also signifies {sorted(sub_hs & set(v.houses))} (fruitful)")
    if v.negate:
        neg = engine.signified(lord, 4) & set(v.negate)
        if neg and not (sub_hs & set(v.houses)):
            s -= 3
            reasons.append(f"{lord} also signifies negating houses {sorted(neg)}")
    if matter.karaka and lord == matter.karaka:
        s += 0.5
    return s, reasons


def score_periods(engine: Engine, matter: Matter, v: Variant, periods: list[D.Period],
                  rps: list[str] | None = None) -> list[Scored]:
    cache: dict[str, tuple[float, list[str]]] = {}

    def ls(l):
        if l not in cache:
            cache[l] = _lord_score(engine, l, v, matter)
        return cache[l]

    out = []
    ch = engine.chart
    for p in periods:
        d, b, a = p.lords[:3]
        sd, rd = ls(d)
        if sd <= 0:
            continue                      # dasa supremacy
        sb, rb = ls(b)
        sa, ra = ls(a)
        if sb <= 0 and sa <= 0:
            continue
        score = sd + 1.5 * sb + sa
        reasons = [f"Dasa {d}: " + "; ".join(rd)]
        if sb > 0:
            reasons.append(f"Bhukti {b}: " + "; ".join(rb))
        if sa > 0:
            reasons.append(f"Antara {a}: " + "; ".join(ra))
        if a == d and d != b:
            score += 2
            reasons.append("A–B–A pattern: result to the full extent (R3)")
        if d != b and engine.use_aspects:
            asp = western_between(d, ch.planets[d].lon, b, ch.planets[b].lon)
            if asp and asp.name != "conjunction":
                score += 1 if asp.quality == "good" else -1
                reasons.append(f"{d}–{b} {asp.name} ({asp.quality}) (R3 dasa principle)")
        if rps:
            k = len({d, b, a} & set(rps))
            score += 0.25 * k
        out.append(Scored(p, round(score, 2), reasons))
    return out


def magnitude_note(engine: Engine, lords: tuple[str, ...]) -> str | None:
    """R6 p.145–146: the star lord's strength scales magnitude (container/contents)."""
    notes = []
    for l in lords:
        star = engine.chart.planets[l].lords.star
        dig = engine.chart.planets[star].dignity() if star in EXALTATION else None
        if dig == "exalted":
            notes.append(f"{l}'s star lord {star} is exalted → larger result")
        elif dig == "debilitated":
            notes.append(f"{l}'s star lord {star} is debilitated → smaller result")
    return "; ".join(notes) + " (R6 p.145)" if notes else None


def pinpoint(lords: tuple[str, ...], start: datetime, end: datetime, ayanamsa_name: str,
             max_dates: int = 4) -> list[dict]:
    """Days in the window when the Sun transits a sign/star/sub all ruled by the D/B/A lords (R3 ch.2; R5)."""
    from .chart import ayanamsa
    want = set(lords)
    out = []
    t = max(start, start)
    step = timedelta(days=1)
    prev = False
    while t < end and len(out) < max_dates:
        jd = julday(t)
        xx, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH)
        lon = (xx[0] - ayanamsa(jd, ayanamsa_name)) % 360
        L = lords_of(lon)
        hit = {L.sign, L.star, L.sub} <= want
        if hit and not prev:
            out.append({"date": t.date().isoformat(), "sun": f"{L.sign_name} / {L.star_name} / {L.sub} sub",
                        "rule": "Sun in sign, star and sub of the period lords"})
        prev = hit
        t += step
    return out


def matter_report(chart: Chart, engine: Engine, matter: Matter, now: datetime,
                  periods: list[D.Period], rps: list[str] | None = None,
                  known_event: datetime | None = None, top_n: int = 3) -> dict:
    variants_out = []
    span = longevity_span(engine) if matter.key == "death" else None
    for v in matter.variants:
        scored = score_periods(engine, matter, v, periods, rps)
        if span:
            lo, hi = span["years"]
            for s in scored:
                age = (s.period.start - chart.utc).days / 365.25
                if not (lo <= age <= hi + 5):
                    s.score -= 4
                    s.reasons.append(f"outside the promised span {span['band']}")
        scored.sort(key=lambda s: -s.score)
        picked, seen = [], set()
        for s in scored:
            key = s.period.lords[:2]
            if key in seen:
                continue
            seen.add(key)
            picked.append(s)
            if len(picked) >= top_n:
                break
        best = scored[0].score if scored else 0
        strong = sorted([s for s in scored if s.score >= 0.75 * best and s not in picked],
                        key=lambda s: s.period.start)[:10] if not matter.one_time else []

        def win(s: Scored, rank: int | None):
            st = "PAST" if s.period.end < now else ("CURRENT" if s.period.start <= now else "FUTURE")
            age = (s.period.start - chart.utc).days / 365.25
            return {"rank": rank, "lords": list(s.period.lords[:3]), "start": s.period.start.date().isoformat(),
                    "end": s.period.end.date().isoformat(), "age_at_start": round(age, 1), "status": st,
                    "score": s.score, "reasons": s.reasons,
                    "magnitude": magnitude_note(engine, s.period.lords[:3]),
                    "pinpoint": pinpoint(s.period.lords[:3], s.period.start, s.period.end,
                                         chart.ayanamsa_name) if rank else []}

        pr = promise(engine, *v.promise) if v.promise else None
        entry = {"houses": v.houses, "source": v.source, "note": v.note, "promise": pr,
                 "windows": [win(s, i + 1) for i, s in enumerate(picked)],
                 "other_strong_windows": [win(s, None) for s in strong]}
        if known_event:
            rank = None
            for i, s in enumerate(scored):
                if s.period.start <= known_event < s.period.end:
                    rank = i + 1
                    break
            entry["known_event_check"] = {"date": known_event.date().isoformat(),
                                          "rank_of_its_window": rank,
                                          "in_top_3": bool(rank and rank <= 3)}
        variants_out.append(entry)
    return {"key": matter.key, "title": matter.title, "group": matter.group, "one_time": matter.one_time,
            "karaka": matter.karaka, "span": span, "variants": variants_out}


def bio(chart: Chart, now: datetime | None = None, use_aspects: bool = True,
        rps: list[str] | None = None, known_events: dict[str, datetime] | None = None,
        only: list[str] | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    engine = Engine(chart, use_aspects=use_aspects)
    periods = D.periods(chart.utc, chart.planets["Moon"].lon, depth=3, until_years=100)
    reports = []
    for m in catalogue(chart):
        if only and m.key not in only:
            continue
        ke = (known_events or {}).get(m.key)
        reports.append(matter_report(chart, engine, m, now, periods, rps, ke))
    return {"generated": now.isoformat(), "ayanamsa": chart.ayanamsa_name, "matters": reports,
            "significators": engine.table(), "houses": engine.house_table(),
            "aspects": [a.as_dict() for a in engine.aspects]}
