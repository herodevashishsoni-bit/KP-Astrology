"""Diagnostics: for verified events, test candidate KP criteria for (a) hit rate on the
event period and (b) selectivity (share of all life periods that also pass)."""
from __future__ import annotations
from datetime import datetime, timezone
from kp import dasa as D
from kp.chart import cast_local
from kp.matters import catalogue
from kp.significators import Engine, strong_significators
from .cases import CASES

def verified():
    for c in CASES:
        ch=cast_local(c["birth"],c["tz"],c["lat"],c["lon"])
        for key,evs in c["events"].items():
            for ds,printed in evs:
                ev=datetime.fromisoformat(ds).replace(tzinfo=timezone.utc)
                p=D.at(ch.utc,ch.planets["Moon"].lon,ev,3)
                ours=p.label().replace("–","-")
                n=len(printed.split("-")) if printed else 0
                ok=(not printed) or "-".join(ours.split("-")[:min(n,2)])=="-".join(printed.split("-")[:min(n,2)])
                if ok: yield c,ch,key,ev,p

def run(crit_fns):
    rows=[]
    for c,ch,key,ev,p in verified():
        e=Engine(ch); m={x.key:x for x in catalogue(ch)}[key]
        ps=D.periods(ch.utc,ch.planets["Moon"].lon,3,90)
        for name,fn in crit_fns.items():
            hit=any(fn(e,v,p) for v in m.variants)
            sel=sum(1 for q in ps if any(fn(e,v,q) for v in m.variants))/len(ps)
            rows.append((name,c["id"],key,hit,sel))
    import collections
    agg=collections.defaultdict(lambda:[0,0,0.0])
    for name,_,_,hit,sel in rows:
        a=agg[name]; a[0]+=hit; a[1]+=1; a[2]+=sel
    for name,(h,n,s) in agg.items():
        print(f"{name:40} hit {h}/{n}  avg selectivity {s/n:.2f}  lift {(h/n)/(s/n):.2f}")
    return rows

def sig(e,l,hs,lvl=4): return bool(e.signified(l,lvl)&set(hs))
def subsig(e,l,hs):
    sub=e.chart.planets[l].lords.sub; return bool(e.sub_lord_houses(sub)&set(hs))
def strong(e,v): return {s.planet for s in strong_significators(e,v.houses)}

C={
 "D,B,A all signify (≤4)": lambda e,v,p: all(sig(e,l,v.houses) for l in p.lords[:3]),
 "D,B,A all signify (≤2 occ/star-occ)": lambda e,v,p: all(sig(e,l,v.houses,2) for l in p.lords[:3]),
 "B,A in strong set; D signifies": lambda e,v,p: sig(e,p.lords[0],v.houses) and p.lords[1] in strong(e,v) and p.lords[2] in strong(e,v),
 "B in strong set": lambda e,v,p: p.lords[1] in strong(e,v),
 "D,B,A signify + B,A sub fruitful": lambda e,v,p: all(sig(e,l,v.houses) for l in p.lords[:3]) and subsig(e,p.lords[1],v.houses) and subsig(e,p.lords[2],v.houses),
 "B star-lord signifies (≤4 of star lord)": lambda e,v,p: sig(e,e.chart.planets[p.lords[1]].lords.star,v.houses),
 "B & A star lords signify": lambda e,v,p: all(sig(e,e.chart.planets[l].lords.star,v.houses) for l in p.lords[1:3]),
 "B&A star lords sig + B&A sub lords sig": lambda e,v,p: all(sig(e,e.chart.planets[l].lords.star,v.houses) and sig(e,e.chart.planets[l].lords.sub,v.houses) for l in p.lords[1:3]),
 "D,B,A star lords and sub lords signify": lambda e,v,p: all(sig(e,e.chart.planets[l].lords.star,v.houses) and sig(e,e.chart.planets[l].lords.sub,v.houses) for l in p.lords[:3]),
 "cusp-sub-lord or its star lord among D,B,A": lambda e,v,p: v.promise is not None and bool({e.chart.cusp_lords[v.promise[0]-1].sub, e.chart.planets[e.chart.cusp_lords[v.promise[0]-1].sub].lords.star} & set(p.lords[:3])),
}
if __name__=="__main__":
    run(C)
