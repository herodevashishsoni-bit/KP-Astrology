"""Compare scoring options on the validation cases (hits@3, median rank)."""
from __future__ import annotations
import statistics
from datetime import datetime, timezone
from kp import dasa as D
from kp.chart import cast_local
from kp.matters import catalogue
from kp.significators import Engine
from kp import windows as W
from .cases import CASES

def ranks(use_aspects=True, **opts):
    out=[]
    for c in CASES:
        ch=cast_local(c["birth"],c["tz"],c["lat"],c["lon"])
        eng=Engine(ch,use_aspects=use_aspects)
        ps=D.periods(ch.utc,ch.planets["Moon"].lon,3,100)
        mats={m.key:m for m in catalogue(ch)}
        for key,evs in c["events"].items():
            m=mats[key]
            for ds,_ in evs:
                ev=datetime.fromisoformat(ds).replace(tzinfo=timezone.utc)
                best=999
                for v in m.variants:
                    sc=sorted(W.score_periods(eng,m,v,ps,**opts),key=lambda s:-s.score)
                    seen=[]
                    for s in sc:
                        k=s.period.lords[:2]
                        if k not in seen: seen.append(k)
                        if s.period.start<=ev<s.period.end:
                            best=min(best,seen.index(k)+1); break
                out.append(best)
    return out

if __name__=="__main__":
    import sys
    for name,kw in [("sum, asp on",dict(use_aspects=True,method="sum")),("strong, asp on",dict(use_aspects=True,method="strong")),("strong, asp off",dict(use_aspects=False,method="strong"))]:
        r=ranks(**kw)
        print(f"{name:14} hits@3 {sum(x<=3 for x in r)}/{len(r)}  hits@10 {sum(x<=10 for x in r)}  median {statistics.median(r)}  {r}")
