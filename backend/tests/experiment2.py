"""Chronological test: among windows whose score is in the top X% for the matter,
ordered by time from a start age, where does the actual event fall?"""
from __future__ import annotations
import statistics
from datetime import datetime, timezone
from kp import dasa as D
from kp.chart import cast_local
from kp.matters import catalogue
from kp.significators import Engine
from kp import windows as W
from .cases import CASES
START = {"marriage": 18, "child": 18, "job": 16, "business": 18, "seniority": 18}

def run(pct=0.25, method="sum", use_aspects=True, start_override=None):
    res=[]
    for c in CASES:
        ch=cast_local(c["birth"],c["tz"],c["lat"],c["lon"])
        eng=Engine(ch,use_aspects=use_aspects)
        ps=D.periods(ch.utc,ch.planets["Moon"].lon,3,100)
        mats={m.key:m for m in catalogue(ch)}
        for key,evs in c["events"].items():
            m=mats[key]
            age0=(start_override if start_override is not None else START.get(key,0))
            t0=ch.utc.replace(year=ch.utc.year+age0) if age0 else ch.utc
            for ds,_ in evs:
                ev=datetime.fromisoformat(ds).replace(tzinfo=timezone.utc)
                best=999
                for v in m.variants:
                    sc=W.score_periods(eng,m,v,ps,method=method)
                    if not sc: continue
                    vals=sorted([s.score for s in sc],reverse=True)
                    thr=vals[max(0,int(len(vals)*pct)-1)]
                    strong=[s for s in sc if s.score>=thr and s.period.end>t0]
                    strong.sort(key=lambda s:s.period.start)
                    # merge by (D,B)
                    order=[]
                    for s in strong:
                        k=s.period.lords[:2]
                        if k not in order: order.append(k)
                        if s.period.start<=ev<s.period.end:
                            best=min(best,order.index(k)+1); break
                res.append((c["id"],key,best))
    r=[x[2] for x in res]
    return sum(x<=1 for x in r), sum(x<=3 for x in r), statistics.median(r), res

if __name__=="__main__":
    for pct in (0.1,0.2,0.3):
        for method in ("sum","strong"):
            h1,h3,med,res=run(pct,method)
            print(f"top{int(pct*100)}% {method:6}: first {h1}/25  within first 3 {h3}/25  median {med}  {[x[2] for x in res]}")
