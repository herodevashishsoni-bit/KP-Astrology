"""The significator engine (kp-rules §2).

Levels, strongest first (R3):
  1 planets in the star of the occupants
  2 occupants
  3 planets in the star of the lord
  4 the lord (owner of the cusp's sign)
  5 planets conjoined with the above
  6 planets aspected by the above (Western + Hindu, user decision #2)
Nodes: a node signifies whatever its agents signify — conjoined planets,
aspecting planets, its star lord, its sign lord (KSK order) — and is stronger
than them (R3). Substitution: a node in a sign owned by a significator takes its
place (MC_058).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .aspects import Aspect, all_aspects, aspecting, conjoined
from .chart import Chart
from .constants import PLANETS, SIGN_LORDS

LEVEL_NAMES = {
    1: "in the star of an occupant",
    2: "occupant",
    3: "in the star of the lord",
    4: "lord",
    5: "conjoined with a significator",
    6: "aspected by a significator",
}
NODES = ("Rahu", "Ketu")


@dataclass
class Sig:
    planet: str
    house: int
    level: float          # lower = stronger; nodes get agent level − 0.5
    reason: str

    def as_dict(self) -> dict:
        return {"planet": self.planet, "house": self.house, "level": self.level, "reason": self.reason}


@dataclass
class Engine:
    chart: Chart
    use_aspects: bool = True
    node_order: str = "KSK"       # "KSK": conjoined→aspect→star→sign ; "star-first" (MC_123)
    aspects: list[Aspect] = field(default_factory=list)
    _matrix: dict[str, dict[int, Sig]] = field(default_factory=dict)

    def __post_init__(self):
        self.aspects = all_aspects(self.chart, western=self.use_aspects, hindu=self.use_aspects)
        self._build()

    # ---- base levels -------------------------------------------------
    def _base(self, house: int) -> list[Sig]:
        ch = self.chart
        out: list[Sig] = []
        occ = [p for p in ch.occupants(house)]
        lord = ch.house_lord(house)
        for p, b in ch.planets.items():
            if b.lords.star in occ:
                out.append(Sig(p, house, 1, f"{p} is in the star of {b.lords.star}, occupant of house {house}"))
        for p in occ:
            out.append(Sig(p, house, 2, f"{p} occupies house {house}"))
        for p, b in ch.planets.items():
            if b.lords.star == lord:
                out.append(Sig(p, house, 3, f"{p} is in the star of {lord}, lord of house {house}"))
        out.append(Sig(lord, house, 4, f"{lord} owns house {house} (cusp sign)"))
        return out

    def _build(self):
        ch = self.chart
        m: dict[str, dict[int, Sig]] = {p: {} for p in PLANETS}

        def put(s: Sig):
            cur = m[s.planet].get(s.house)
            if cur is None or s.level < cur.level:
                m[s.planet][s.house] = s

        base_by_house = {h: self._base(h) for h in range(1, 13)}
        for h, sigs in base_by_house.items():
            for s in sigs:
                put(s)
        # nodes as agents (their own entries already exist if they occupy/own-star)
        for node in NODES:
            for h in range(1, 13):
                best = None
                for agent, why in self.node_agents(node):
                    a = m[agent].get(h)
                    if a and a.level <= 4 and (best is None or a.level < best[0]):
                        best = (a.level, agent, why)
                if best:
                    put(Sig(node, h, best[0] - 0.5,
                            f"{node} acts for {best[1]} ({best[2]}), which signifies house {h}"))
        # levels 5 and 6: conjunction / aspect with a level 1–4 significator
        if self.use_aspects:
            for h in range(1, 13):
                strong = [p for p in PLANETS if m[p].get(h) and m[p][h].level <= 4]
                for p in PLANETS:
                    if m[p].get(h):
                        continue
                    conj = [q for q in strong if q in conjoined(ch, p, self.aspects)]
                    if conj:
                        put(Sig(p, h, 5, f"{p} is conjoined with {conj[0]}, a significator of house {h}"))
                        continue
                    asp = [x for x in aspecting(ch, p, self.aspects) if x.a in strong]
                    if asp:
                        x = asp[0]
                        put(Sig(p, h, 6, f"{p} receives a {x.kind} {x.name} from {x.a}, a significator of house {h}"))
        self._matrix = m

    # ---- nodes -------------------------------------------------------
    def node_agents(self, node: str) -> list[tuple[str, str]]:
        # R3/R6: a node represents its sign lord only if it is not conjoined or aspected;
        # it always gives the results of its star lord. Aspects on nodes: Hindu full aspects
        # (R3 uses them for nodes) and the major Western aspects.
        ch = self.chart
        b = ch.planets[node]
        # "In that order" is read as an order of preference: conjoined planets if any,
        # otherwise aspecting planets (Hindu full aspects, as R3 uses for nodes).
        conj = [(p, "conjoined") for p in conjoined(ch, node, self.aspects) if p not in NODES]
        asp = [] if conj else [(x.a, f"Hindu aspect") for x in aspecting(ch, node, self.aspects)
                               if x.a not in NODES and x.kind == "hindu"]
        star = [(b.lords.star, "its star lord")] if b.lords.star not in NODES else []
        sign = [] if (conj or asp) else [(SIGN_LORDS[b.sign_index], "its sign lord")]
        order = conj + asp + star + sign if self.node_order == "KSK" else star + conj + asp + sign
        seen, out = set(), []
        for p, why in order:
            if p not in seen:
                seen.add(p)
                out.append((p, why))
        return out

    # ---- queries -----------------------------------------------------
    def of_house(self, house: int) -> list[Sig]:
        sigs = [self._matrix[p][house] for p in PLANETS if house in self._matrix[p]]
        return sorted(sigs, key=lambda s: (s.level, PLANETS.index(s.planet)))

    def houses_of(self, planet: str, max_level: float = 6) -> dict[int, Sig]:
        return {h: s for h, s in self._matrix[planet].items() if s.level <= max_level}

    def strength(self, planet: str, houses: list[int], max_level: float = 6,
                 weights: dict[int, float] | None = None) -> tuple[float, list[Sig]]:
        """Score how strongly planet signifies the houses: level 1 → 6 pts … level 6 → 1 pt."""
        tot, used = 0.0, []
        for h in houses:
            s = self._matrix[planet].get(h)
            if s and s.level <= max_level:
                tot += (7 - s.level) * (weights or {}).get(h, 1.0)
                used.append(s)
        return tot, used

    def signified(self, planet: str, max_level: float = 4) -> set[int]:
        return {h for h, s in self._matrix[planet].items() if s.level <= max_level}

    def sub_lord_houses(self, planet: str, mode: str = "standard") -> set[int]:
        """Houses signified by the sub lord of a planet/cusp sub lord.

        standard (R3/R4): the sub lord signifies houses through its star lord, occupation, ownership.
        own (magazine "do not scrutinize further"): only the houses the sub lord occupies and owns.
        """
        ch = self.chart
        if mode == "own":
            return {ch.planets[planet].house} | set(ch.owner_houses(planet))
        b = ch.planets[planet]
        return ({ch.planets[b.lords.star].house} | set(ch.owner_houses(b.lords.star))
                | {b.house} | set(ch.owner_houses(planet)) | self.signified(planet, 4))

    def table(self) -> list[dict]:
        """Planet → star lord → sub lord with houses (the display table, MC_061)."""
        ch = self.chart
        rows = []
        for p in PLANETS:
            b = ch.planets[p]
            rows.append({
                "planet": p, "occupies": b.house, "owns": ch.owner_houses(p),
                "star_lord": b.lords.star, "star_lord_occupies": ch.planets[b.lords.star].house,
                "star_lord_owns": ch.owner_houses(b.lords.star),
                "sub_lord": b.lords.sub, "sub_lord_occupies": ch.planets[b.lords.sub].house,
                "sub_lord_owns": ch.owner_houses(b.lords.sub),
                "signifies": sorted(self.signified(p, 4)),
                "node_agents": [a for a, _ in self.node_agents(p)] if p in NODES else [],
            })
        return rows

    def house_table(self) -> list[dict]:
        return [{"house": h, "significators": [s.as_dict() for s in self.of_house(h)]} for h in range(1, 13)]


def strong_significators(engine: "Engine", houses: list[int], want: int = 4) -> list[Sig]:
    """KSK selection: walk the levels (1 → 6) over all the matter's houses and stop once
    at least `want` distinct planets are found ("if enough significators are found in
    items 1 and 2 one need not go to 3, 4, 5", MC_056; "if four significators come up,
    stop", MC_058). Nodes rank with their agent's level − 0.5."""
    allsigs = sorted([s for h in houses for s in engine.of_house(h)], key=lambda s: s.level)
    chosen: dict[str, Sig] = {}
    cutoff = None
    for s in allsigs:
        if cutoff is not None and s.level > cutoff:
            break
        if s.planet not in chosen:
            chosen[s.planet] = s
        if len(chosen) >= want and cutoff is None:
            cutoff = int(s.level + 0.5) if s.level % 1 else s.level   # finish the current level
    return list(chosen.values())
