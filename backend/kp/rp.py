"""Ruling planets (kp-rules §2.5).

Day lord (sunrise to sunrise), Moon's star lord, Moon's sign lord, lagna sign
lord, lagna star lord; also the lagna sub lord where the texts use it.
A node is added when it is in the sign of, conjoined with, or aspected by an RP
(KSK editor's note, MC_057). Horary use: an RP in the star of a retrograde
planet is rejected (R6).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .chart import Chart, cast, sunrise_utc
from .constants import SIGN_LORDS

WEEKDAY_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]  # Monday=0


def day_lord(utc: datetime, lat: float, lon: float) -> str:
    rise = sunrise_utc(utc, lat, lon)
    # weekday of the local date on which that sunrise happened
    local_rise = rise + timedelta(hours=lon / 15.0)
    return WEEKDAY_LORDS[local_rise.weekday()]


def ruling_planets(chart: Chart, horary: bool = False) -> dict:
    moon = chart.planets["Moon"].lords
    asc = chart.cusp_lords[0]
    items = [
        ("lagna star lord", asc.star),
        ("lagna sign lord", asc.sign),
        ("Moon star lord", moon.star),
        ("Moon sign lord", moon.sign),
        ("day lord", day_lord(chart.utc, chart.lat, chart.lon)),
    ]
    base = []
    for _, p in items:
        if p not in base:
            base.append(p)
    nodes = []
    for node in ("Rahu", "Ketu"):
        if node in base:
            continue
        sign_lord = SIGN_LORDS[chart.planets[node].sign_index]
        same_sign = [p for p in base if p not in ("Rahu", "Ketu") and chart.planets[p].sign_index == chart.planets[node].sign_index]
        if sign_lord in base or same_sign:
            nodes.append(node)
    rejected = []
    if horary:
        for p in base + nodes:
            star_lord = chart.planets[p].lords.star
            if chart.planets[star_lord].retro:
                rejected.append(p)
    final = [p for p in base + nodes if p not in rejected]
    return {"items": [{"role": r, "planet": p} for r, p in items],
            "lagna_sub_lord": asc.sub, "nodes_added": nodes, "rejected_retro_star": rejected,
            "ruling_planets": final}


def rp_now(when_utc: datetime, lat: float, lon: float, ayanamsa_name: str = "KSK", horary: bool = False) -> dict:
    ch = cast(when_utc, lat, lon, ayanamsa_name)
    out = ruling_planets(ch, horary)
    out["chart"] = ch
    return out
