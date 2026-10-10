"""Aspects (user decision #2: Western degree aspects AND Hindu full aspects).

Western: the R1/R2 table with its orbs (planet–planet and planet–cusp).
Hindu: full sign aspects (all planets 7th; Mars 4/8; Jupiter 5/9; Saturn 3/10;
nodes 5/9 as quoted in R3 for node agency).
"""
from __future__ import annotations

from dataclasses import dataclass

from .chart import Chart
from .constants import (CUSP_CONJUNCTION_ORB, DEFAULT_ORB, HINDU_ASPECTS, PLANET_ORB,
                        WESTERN_ASPECTS)


@dataclass(frozen=True)
class Aspect:
    a: str            # aspecting planet
    b: str            # aspected planet, or "cusp N"
    kind: str         # "western" | "hindu"
    name: str
    quality: str      # good / adverse / by nature
    orb: float = 0.0  # actual deviation from exact (western)

    def as_dict(self) -> dict:
        return {"from": self.a, "to": self.b, "system": self.kind, "aspect": self.name,
                "quality": self.quality, "orb": round(self.orb, 2)}


def _sep(x: float, y: float) -> float:
    d = abs(x - y) % 360
    return 360 - d if d > 180 else d


def western_between(p1: str, l1: float, p2: str, l2: float, cusp: bool = False) -> Aspect | None:
    d = _sep(l1, l2)
    for name, angle, quality, _rank, orb in WESTERN_ASPECTS:
        if orb is None:  # conjunction
            orb = CUSP_CONJUNCTION_ORB if cusp else (PLANET_ORB.get(p1, DEFAULT_ORB) + PLANET_ORB.get(p2, DEFAULT_ORB)) / 2
        if abs(d - angle) <= orb:
            return Aspect(p1, p2, "western", name, quality, abs(d - angle))
    return None


def hindu_aspects_of(chart: Chart, planet: str) -> list[int]:
    """Sign indices aspected by planet (Hindu full aspects, counted sign to sign)."""
    s = chart.planets[planet].sign_index
    return [(s + n - 1) % 12 for n in HINDU_ASPECTS[planet]]


def all_aspects(chart: Chart, western: bool = True, hindu: bool = True) -> list[Aspect]:
    out: list[Aspect] = []
    names = list(chart.planets)
    if western:
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if {a, b} == {"Rahu", "Ketu"}:
                    continue
                asp = western_between(a, chart.planets[a].lon, b, chart.planets[b].lon)
                if asp:
                    out.append(asp)
                    out.append(Aspect(b, a, asp.kind, asp.name, asp.quality, asp.orb))
            for h, c in enumerate(chart.cusps, 1):
                asp = western_between(a, chart.planets[a].lon, f"cusp {h}", c, cusp=True)
                if asp:
                    out.append(asp)
    if hindu:
        for a in names:
            for si in hindu_aspects_of(chart, a):
                for b in names:
                    if b != a and chart.planets[b].sign_index == si and {a, b} != {"Rahu", "Ketu"}:
                        out.append(Aspect(a, b, "hindu", "full", "by nature"))
    return out


def aspecting(chart: Chart, target: str, aspects: list[Aspect]) -> list[Aspect]:
    return [x for x in aspects if x.b == target and x.name != "conjunction"]


def conjoined(chart: Chart, target: str, aspects: list[Aspect]) -> list[str]:
    """Planets conjoined with target: western conjunction within orb, or same sign for nodes (R3)."""
    out = {x.a for x in aspects if x.b == target and x.name == "conjunction"}
    if target in ("Rahu", "Ketu"):
        s = chart.planets[target].sign_index
        out |= {p for p, b in chart.planets.items() if p != target and b.sign_index == s and p not in ("Rahu", "Ketu")}
    return sorted(out)
