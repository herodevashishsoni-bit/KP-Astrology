"""Birth-time rectification (kp-rules §6).

KP method (R3 l.~21250–21720; R6 p.140–143; MC_058 "When am I born?"):
 1. RPs at the moment of judgment (horary rules: drop an RP in the star of a retrograde planet).
 2. The birth Ascendant's sign, star and sub lords (and ideally the sub-sub) must be RPs;
    a node stands for the planets it represents.
 3. Scan the user's time range; every stretch where the Ascendant is ruled by RPs is a candidate.
 4. Known events decide between candidates (KSK: "multiple judgments are allowed").
Traditional vighati check (×4 ÷ 9) is shown for information only (R3 used it; R6 rejects it).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import dasa as D
from .chart import Chart, cast, sunrise_utc
from .matters import catalogue
from .rp import ruling_planets
from .significators import Engine
from .subs import fmt_dms, lords_of
from .windows import score_periods


def _expand(rps: list[str], judge: Chart) -> set[str]:
    """Nodes stand for the planets they represent and vice versa."""
    eng = Engine(judge, use_aspects=True)
    out = set(rps)
    for n in ("Rahu", "Ketu"):
        agents = [a for a, _ in eng.node_agents(n)]
        if n in rps:
            out |= set(agents)
        if set(agents) & set(rps):
            out.add(n)
    return out


def candidates(start_local: datetime, end_local: datetime, tz, lat: float, lon: float,
               judge_utc: datetime, judge_lat: float, judge_lon: float, ayanamsa_name: str = "KSK",
               step_seconds: int = 20, reject_retro: bool = True,
               rps_override: list[str] | None = None) -> dict:
    from .chart import to_utc
    judge = cast(judge_utc, judge_lat, judge_lon, ayanamsa_name)
    rp = ruling_planets(judge, horary=reject_retro)
    rps = rps_override or rp["ruling_planets"]
    allowed = _expand(rps, judge)
    t = to_utc(start_local, tz)
    t_end = to_utc(end_local, tz)
    segs: list[dict] = []
    cur = None
    while t <= t_end:
        ch = cast(t, lat, lon, ayanamsa_name)
        L = ch.cusp_lords[0]
        ok = L.sign in allowed and L.star in allowed and L.sub in allowed
        key = (L.sign, L.star, L.sub, L.subsub)
        if ok:
            if cur and cur["key"] == key:
                cur["end"] = t
            else:
                cur = {"key": key, "start": t, "end": t, "asc_start": ch.cusps[0]}
                segs.append(cur)
            cur["asc_end"] = ch.cusps[0]
        else:
            cur = None
        t += timedelta(seconds=step_seconds)
    out = []
    lagna_lord_now = judge.cusp_lords[0].sign
    for s in segs:
        mid = s["start"] + (s["end"] - s["start"]) / 2
        sign, star, sub, subsub = s["key"]
        score = 3 + (1 if subsub in allowed else 0) + (1 if subsub == lagna_lord_now else 0)
        out.append({"start_utc": s["start"].isoformat(), "end_utc": s["end"].isoformat(),
                    "mid_utc": mid.isoformat(), "asc": f"{fmt_dms(s['asc_start'])} – {fmt_dms(s['asc_end'])}",
                    "sign_lord": sign, "star_lord": star, "sub_lord": sub, "subsub_lord": subsub,
                    "rp_score": score,
                    "notes": ([f"sub-sub lord {subsub} is an RP"] if subsub in allowed else [])
                             + ([f"sub-sub lord equals the lagna lord at judgment ({lagna_lord_now}) (R3)"]
                                if subsub == lagna_lord_now else [])})
    out.sort(key=lambda c: -c["rp_score"])
    return {"judgment_utc": judge_utc.isoformat(), "ruling_planets": rps, "reject_retro": reject_retro, "allowed_with_nodes": sorted(allowed),
            "rp_detail": {k: v for k, v in rp.items() if k != "chart"}, "candidates": out,
            "source": "R3 l.~21250–21720; R6 p.140–143; MC_058"}


def check_events(candidate_utc: datetime, lat: float, lon: float, events: dict[str, datetime],
                 ayanamsa_name: str = "KSK") -> dict:
    """How well a candidate birth time explains known events (rank of each event's window)."""
    ch = cast(candidate_utc, lat, lon, ayanamsa_name)
    eng = Engine(ch)
    periods = D.periods(ch.utc, ch.planets["Moon"].lon, 3, 100)
    mats = {m.key: m for m in catalogue(ch)}
    res, total = [], 0.0
    for key, when in events.items():
        m = mats.get(key)
        if not m:
            continue
        best = None
        for v in m.variants:
            sc = sorted(score_periods(eng, m, v, periods), key=lambda s: -s.score)
            seen = []
            for s in sc:
                k = s.period.lords[:2]
                if k not in seen:
                    seen.append(k)
                if s.period.start <= when < s.period.end:
                    r = seen.index(k) + 1
                    if best is None or r < best[0]:
                        best = (r, v.source)
                    break
        p = D.at(ch.utc, ch.planets["Moon"].lon, when, 3)
        res.append({"matter": key, "date": when.date().isoformat(), "period": p.label() if p else None,
                    "rank": best[0] if best else None, "variant": best[1] if best else None})
        total += 1.0 / best[0] if best else 0
    return {"birth_utc": candidate_utc.isoformat(), "events": res, "fit": round(total, 3)}


def vighati_check(birth_utc: datetime, lat: float, lon: float, moon_star_lord: str) -> dict:
    """Traditional check (information only): vighatis since sunrise ×4 ÷ 9; the remainder
    gives the birth-star group counted from Aswini (R3 used it; R6 p.141 rejects it)."""
    from .constants import DASA_ORDER
    rise = sunrise_utc(birth_utc, lat, lon)
    vig = int((birth_utc - rise).total_seconds() / 24)  # 1 vighati = 24 s
    rem = (vig * 4) % 9
    lord = DASA_ORDER[(rem - 1) % 9]
    return {"vighatis_since_sunrise": vig, "remainder": rem, "star_group_lord": lord,
            "moon_star_lord": moon_star_lord, "agrees": lord == moon_star_lord,
            "status": "information only (R3 used it; R6 p.141 rejects it)"}
