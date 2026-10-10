"""Run the engine on the confirmed cases and report.

  python -m tests.validate            # summary table
Checks: (1) our D–B–A at the event equals the printed periods;
        (2) rank of the event's window among all windows (best variant).
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

from kp import dasa as D
from kp.chart import cast_local
from kp.matters import catalogue
from kp.significators import Engine
from kp.windows import score_periods

from .cases import CASES


def run(ayanamsa_name: str = "KSK", verbose: bool = False):
    rows = []
    for c in CASES:
        ch = cast_local(c["birth"], c["tz"], c["lat"], c["lon"], ayanamsa_name)
        eng = Engine(ch)
        periods = D.periods(ch.utc, ch.planets["Moon"].lon, depth=3, until_years=100)
        mats = {m.key: m for m in catalogue(ch)}
        for key, evs in c["events"].items():
            m = mats[key]
            for date_s, printed in evs:
                ev = datetime.fromisoformat(date_s).replace(tzinfo=timezone.utc)
                ours = D.at(ch.utc, ch.planets["Moon"].lon, ev, depth=3)
                ours_s = ours.label().replace("–", "-") if ours else "?"
                dasa_ok = (not printed) or ours_s.startswith(printed) or printed.startswith(ours_s[:len(printed)])
                best = None
                for v in m.variants:
                    sc = sorted(score_periods(eng, m, v, periods), key=lambda s: -s.score)
                    # rank by distinct (D,B) as in the bio
                    seen, rank = [], None
                    for s in sc:
                        k = s.period.lords[:2]
                        if k in seen:
                            if s.period.start <= ev < s.period.end:
                                rank = seen.index(k) + 1
                                break
                            continue
                        seen.append(k)
                        if s.period.start <= ev < s.period.end:
                            rank = len(seen)
                            break
                    if rank and (best is None or rank < best[0]):
                        best = (rank, v.source)
                rows.append((c["id"], key, date_s, printed, ours_s, dasa_ok, best))
    hits = sum(1 for r in rows if r[6] and r[6][0] <= 3)
    for r in rows:
        print(f"{r[0]:18} {r[1]:13} {r[2]}  printed {r[3]:22} ours {r[4]:22} dasa {'OK ' if r[5] else 'DIFF'}  "
              f"rank {r[6][0] if r[6] else '-':>3}  {r[6][1][:40] if (r[6] and verbose) else ''}")
    print(f"\n{ayanamsa_name}: event window in top 3 for {hits}/{len(rows)} events; "
          f"dasa matches printed for {sum(r[5] for r in rows)}/{len(rows)}")
    return rows


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "KSK", verbose=True)
