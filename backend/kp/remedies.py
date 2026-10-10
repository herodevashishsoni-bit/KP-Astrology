"""Gem suggestions (user decision #17: ON, labelled as remedies).

Sources:
  R3 l.~17940 / p.414–418 and R4 p.279: use the gem of the Ascendant sub lord and the 11th
  cusp sub lord if they are not connected with 6/8/12; reject a sub lord signifying 6/8/12.
  Later Reader note (kp-rules-notes l.1338): use the star lord of the 11th sub lord if it
  signifies 1/2/11; never a gem of a 6/8/12 significator.
KSK's view, shown with the result: remedies do not change fate (R4 p.119; magazines).
"""
from __future__ import annotations

from .significators import Engine

GEMS = {"Sun": "ruby", "Moon": "pearl", "Mars": "coral", "Mercury": "emerald", "Jupiter": "topaz",
        "Venus": "diamond", "Saturn": "sapphire", "Rahu": "agate", "Ketu": "turquoise"}
EVIL = {6, 8, 12}


def gems(engine: Engine) -> dict:
    ch = engine.chart
    out = []
    for label, cusp in (("Ascendant sub lord", 1), ("11th cusp sub lord", 11)):
        sl = ch.cusp_lords[cusp - 1].sub
        sig = engine.signified(sl, 4)
        bad = sorted(sig & EVIL)
        out.append({"rule": f"{label} (R3 p.414–418; R4 p.279)", "planet": sl, "gem": GEMS[sl],
                    "signifies": sorted(sig), "usable": not bad,
                    "reason": (f"{sl} signifies {bad} (6/8/12) → not to be used" if bad
                               else f"{sl} is not connected with 6/8/12")})
    sl11 = ch.cusp_lords[10].sub
    star = ch.planets[sl11].lords.star
    ssig = engine.signified(star, 4)
    ok = bool(ssig & {1, 2, 11}) and not (ssig & EVIL)
    out.append({"rule": "Star lord of the 11th sub lord (later Reader note)", "planet": star, "gem": GEMS[star],
                "signifies": sorted(ssig), "usable": ok,
                "reason": (f"{star} signifies {sorted(ssig & {1, 2, 11})}" if ok
                           else f"{star} signifies {sorted(ssig)} — needs 1/2/11 and no 6/8/12")})
    return {"suggestions": out,
            "note": "Remedy, shown because you enabled it. KSK: remedies do not change destiny "
                    "(R4 p.119: 'Karma comes first. God comes next.')."}
