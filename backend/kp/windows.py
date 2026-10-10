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
    """Span of life from the Ascendant sub lord — two source rules, both shown.

    R3: the Asc sub lord benefic (lord of 1, 5, 9, 10) → long; malefic (lord of 6, 8, 12) → short;
        both → middle (R3 p.157–169; bands R3 l.~7200).
    R6: the Asc sub lord in the star of a significator of badhaka/maraka → short life.
    """
    ch = engine.chart
    sl = ch.cusp_lords[0].sub
    ranges = {"short (0–33)": (0, 33), "middle (33–66)": (33, 66), "long (66–100)": (66, 100)}
    owns = set(ch.owner_houses(sl))
    good, bad = owns & {1, 5, 9, 10}, owns & {6, 8, 12}
    if good and not bad:
        r3 = ("long (66–100)", f"{sl} owns {sorted(good)} (benefic lordship)")
    elif bad and not good:
        r3 = ("short (0–33)", f"{sl} owns {sorted(bad)} (malefic lordship)")
    elif good and bad:
        r3 = ("middle (33–66)", f"{sl} owns both {sorted(good)} and {sorted(bad)}")
    else:
        hs = engine.sub_lord_houses(sl)
        g2, b2 = hs & {1, 5, 9, 10}, hs & {6, 8, 12}
        r3 = (("long (66–100)" if g2 and not b2 else "short (0–33)" if b2 and not g2 else "middle (33–66)"),
              f"{sl} owns no deciding house; it signifies {sorted(hs)}")
    dh = {badhaka_from(ch, 1), 2, 7}
    star = ch.planets[sl].lords.star
    star_sig = engine.signified(star, 2)          # occupant-level significance (strict reading)
    if star_sig & dh:
        r6 = ("short (0–33)", f"{sl} is in the star of {star}, which occupies/is in the star of an occupant of {sorted(star_sig & dh)}")
    else:
        r6 = (None, f"{sl}'s star lord {star} is not a strong significator of badhaka/maraka houses — R6 rule does not shorten life")
    agree = r6[0] is None or r6[0] == r3[0]
    band = r3[0]
    return {"sub_lord": sl, "band": band, "years": ranges[band],
            "rules": [{"source": "R3 p.157–169 (lordship of the Asc sub lord)", "band": r3[0], "reason": r3[1]},
                      {"source": "R6 (Asc sub lord in the star of a badhaka/maraka significator)",
                       "band": r6[0] or "no shortening", "reason": r6[1]}],
            "agree": agree,
            "reason": f"R3: {r3[0]} — {r3[1]}; R6: {r6[0] or 'no shortening'}",
            "source": "R3 p.157–169; R6"}


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
                  rps: list[str] | None = None, method: str = "sum") -> list[Scored]:
    if method == "strong":
        return score_strong(engine, matter, v, periods, rps)
    return score_sum(engine, matter, v, periods, rps)


def score_strong(engine: Engine, matter: Matter, v: Variant, periods: list[D.Period],
                 rps: list[str] | None = None) -> list[Scored]:
    """KSK method: the event comes in the conjoined period of the strong significators;
    the dasa lord must be connected with the houses (any level)."""
    from .significators import strong_significators
    strong = strong_significators(engine, v.houses)
    rank = {s.planet: i for i, s in enumerate(strong)}
    why = {s.planet: s.reason for s in strong}
    fruitful = {p: bool(engine.sub_lord_houses(engine.chart.planets[p].lords.sub) & set(v.houses)) for p in rank}
    out = []
    ch = engine.chart
    for p in periods:
        d, b, a = p.lords[:3]
        sd, _ = engine.strength(d, v.houses, weights=v.weights)
        if sd <= 0:
            continue
        if b not in rank and a not in rank:
            continue
        score = 0.0
        reasons = [f"Dasa {d} is connected with houses {v.houses}"]
        for role, l, wt in (("Bhukti", b, 3.0), ("Antara", a, 2.0), ("Dasa", d, 1.5)):
            if l in rank:
                score += wt * (len(strong) + 1 - rank[l]) / len(strong)
                if fruitful[l]:
                    score += wt * 0.5
                reasons.append(f"{role} {l}: strong significator — {why[l]}"
                               + (" (sub lord also signifies the houses: fruitful)" if fruitful[l] else ""))
        if v.negate:
            for l in (b, a):
                neg = engine.signified(l, 2) & set(v.negate)
                if neg and l not in rank:
                    score -= 1
        if a == d and d != b:
            score += 0.5
            reasons.append("A–B–A pattern: result to the full extent (R3)")
        if d != b and engine.use_aspects:
            asp = western_between(d, ch.planets[d].lon, b, ch.planets[b].lon)
            if asp and asp.name != "conjunction":
                score += 0.25 if asp.quality == "good" else -0.25
                reasons.append(f"{d}–{b} {asp.name} ({asp.quality}) (R3 dasa principle)")
        if rps:
            score += 0.1 * len({d, b, a} & set(rps))
        out.append(Scored(p, round(score, 2), reasons))
    return out


def score_sum(engine: Engine, matter: Matter, v: Variant, periods: list[D.Period],
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
             max_dates: int = 4, agents: dict[str, list[str]] | None = None) -> list[dict]:
    """Days in the window when the Sun transits a point whose sign, star and sub lords are all
    period lords (R3 ch.2; R5 p.161–187). Nodes count for the planets they act for, and vice
    versa. If no such day exists, days with the star and sub ruled by period lords are given."""
    from .chart import ayanamsa
    want = set(lords)
    for l in list(lords):
        want |= set((agents or {}).get(l, []))
    for n, ag in (agents or {}).items():
        if set(ag) & set(lords):
            want.add(n)
    full, partial = [], []
    t = start
    prev_f = prev_p = False
    while t < end:
        jd = julday(t)
        xx, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH)
        lon = (xx[0] - ayanamsa(jd, ayanamsa_name)) % 360
        L = lords_of(lon)
        f = {L.sign, L.star, L.sub} <= want
        pp = {L.star, L.sub} <= want
        if f and not prev_f:
            full.append({"date": t.date().isoformat(), "sun": f"{L.sign_name} / {L.star_name} / {L.sub} sub",
                         "rule": "Sun in a sign, star and sub all ruled by the period lords"})
        elif pp and not prev_p and not f:
            partial.append({"date": t.date().isoformat(), "sun": f"{L.sign_name} / {L.star_name} / {L.sub} sub",
                            "rule": "Sun in a star and sub ruled by the period lords"})
        prev_f, prev_p = f, pp
        t += timedelta(days=1)
    return (full or partial)[:max_dates]


def matter_report(chart: Chart, engine: Engine, matter: Matter, now: datetime,
                  periods: list[D.Period], rps: list[str] | None = None,
                  known_event: datetime | None = None, top_n: int = 3) -> dict:
    variants_out = []
    agents = {n: [a for a, _ in engine.node_agents(n)] for n in ("Rahu", "Ketu")}
    span = longevity_span(engine) if matter.key == "death" else None
    for v in matter.variants:
        scored = score_periods(engine, matter, v, periods, rps)
        if span:
            # R2/R3: if long life is promised an evil period in youth gives illness, not death.
            # Applied only when the span rules agree; otherwise both are shown and nothing is penalised.
            lo, hi = span["years"]
            if span["agree"]:
                for s in scored:
                    age = (s.period.start - chart.utc).days / 365.25
                    if not (lo - 3 <= age <= hi + 5):
                        s.score -= 2
                        s.reasons.append(f"outside the promised span {span['band']} (R2/R3)")
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
                                         chart.ayanamsa_name, agents=agents) if rank else []}

        # KSK's practice (R3 l.~13400; magazines): judge the coming periods, and select with the
        # ruling planets at the moment of judgment. Upcoming = periods starting within 15 years.
        horizon = now + timedelta(days=365.25 * 15)
        up = [s for s in scored if s.period.end > now and s.period.start < horizon]
        if up:
            top = max(s.score for s in up)
            up = [s for s in up if s.score >= 0.7 * top]   # only strong windows compete
        rp_set = set(rps or [])
        up.sort(key=lambda s: (-s.score, -len(set(s.period.lords[:3]) & rp_set)))   # RPs break ties only
        up_pick, seen_u = [], set()
        for s in up:
            k = s.period.lords[:2]
            if k in seen_u or s.score <= 0:
                continue
            seen_u.add(k)
            up_pick.append(s)
            if len(up_pick) >= 3:
                break
        pr = promise(engine, *v.promise) if v.promise else None
        entry = {"upcoming": [dict(win(s, i + 1), rp_lords=sorted(set(s.period.lords[:3]) & rp_set))
                              for i, s in enumerate(sorted(up_pick, key=lambda s: s.period.start))],"houses": v.houses, "source": v.source, "note": v.note, "promise": pr,
                 "windows": [win(s, i + 1) for i, s in enumerate(picked)],
                 "other_strong_windows": [win(s, None) for s in strong]}
        if known_event:
            rank, seen_k = None, []
            for s in scored:
                k = s.period.lords[:2]
                if k not in seen_k:
                    seen_k.append(k)
                if s.period.start <= known_event < s.period.end:
                    rank = seen_k.index(k) + 1
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


def ask_now(chart: Chart, matter_key: str, now: datetime, lat: float, lon: float,
            horizon_years: float = 5.0, use_aspects: bool = True) -> dict:
    """KSK's timing practice for a question asked now (R3 l.~13400; R6; MC_056–061):
    the significators of the matter's houses give the candidates; the ruling planets at the
    moment of the question select among them; the earliest strong conjoined period wins.
    Validation note: whole-life ranking has little lift (docs/validation.md); question-time
    selection reproduced 3 of 4 confirmed horary cases in the top 3."""
    from .rp import rp_now
    engine = Engine(chart, use_aspects=use_aspects)
    rp = rp_now(now, lat, lon, chart.ayanamsa_name)
    rps = rp["ruling_planets"]
    mats = {m.key: m for m in catalogue(chart)}
    m = mats[matter_key]
    end = now + timedelta(days=365.25 * horizon_years)
    periods = [p for p in D.periods(chart.utc, chart.planets["Moon"].lon, 3, 120)
               if p.end > now and p.start < end]
    agents = {n: [a for a, _ in engine.node_agents(n)] for n in ("Rahu", "Ketu")}
    rp_ext = set(rps)
    for n, ag in agents.items():
        if n in rps:
            rp_ext |= set(ag)
        if set(ag) & set(rps):
            rp_ext.add(n)
    out = []
    for v in m.variants:
        scored = score_periods(engine, m, v, periods)
        if not scored:
            out.append({"houses": v.houses, "source": v.source, "windows": [],
                        "promise": promise(engine, *v.promise) if v.promise else None})
            continue
        top = max(s.score for s in scored)
        cands = []
        for s in scored:
            lords = s.period.lords[:3]
            if not all(engine.strength(l, v.houses)[0] > 0 for l in lords):
                continue                                     # D, B, A must all signify the matter
            k = len(set(lords[1:]) & rp_ext)
            if k == 0:
                continue                                     # RPs must pick the bhukti or antara
            cands.append((s, k))
        cands.sort(key=lambda x: (-(x[1] + (x[0].score >= 0.7 * top)), x[0].period.start))
        picked, seen = [], set()
        for s, k in cands:
            key = s.period.lords[:2]
            if key in seen:
                continue
            seen.add(key)
            st = "CURRENT" if s.period.start <= now else "FUTURE"
            picked.append({"lords": list(s.period.lords[:3]), "start": s.period.start.date().isoformat(),
                           "end": s.period.end.date().isoformat(), "status": st, "score": s.score,
                           "rp_lords": sorted(set(s.period.lords[:3]) & rp_ext), "reasons": s.reasons[:4],
                           "pinpoint": pinpoint(s.period.lords[:3], max(s.period.start, now), s.period.end,
                                                chart.ayanamsa_name, agents=agents)})
            if len(picked) >= 3:
                break
        picked.sort(key=lambda w: w["start"])
        for i, w in enumerate(picked):
            w["rank"] = i + 1
        out.append({"houses": v.houses, "source": v.source, "windows": picked,
                    "promise": promise(engine, *v.promise) if v.promise else None})
    return {"matter": m.title, "key": m.key, "asked_at": now.isoformat(), "ruling_planets": rps,
            "ruling_planets_with_nodes": sorted(rp_ext), "horizon_years": horizon_years, "variants": out,
            "method": "KSK: significators of the matter's houses; ruling planets at the moment of asking select the "
                      "period; earliest strong conjoined period first (R3 l.~13400; magazines)."}
