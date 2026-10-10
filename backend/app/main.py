"""FastAPI app: single-user login, saved charts, chart/bio/rectification/horary endpoints."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from kp import dasa as D
from kp.chart import cast_local, to_utc
from kp.constants import SIGNS
from kp.horary import judge as horary_judge
from kp.matters import catalogue
from kp.rectify import candidates as rect_candidates, check_events, vighati_check
from kp.remedies import gems
from kp.rp import rp_now
from kp.significators import Engine
from kp.windows import bio as make_bio

from .auth import check_pw, current_user, hash_pw, token_for
from .db import ChartRec, EventRec, SessionLocal, User, init

app = FastAPI(title="KP Life Bio", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init()


# ------------------------------------------------------------------ helpers
def parse_tz(tz: str):
    t = tz.strip()
    if t and t[0] in "+-" and ":" in t:
        sign = -1 if t[0] == "-" else 1
        h, m = t[1:].split(":")
        return sign * (int(h) + int(m) / 60)
    try:
        return float(t)
    except ValueError:
        return t


def chart_of(rec: ChartRec, ayanamsa: str):
    return cast_local(datetime.fromisoformat(rec.birth_local), parse_tz(rec.tz), rec.lat, rec.lon, ayanamsa)


def get_chart(chart_id: int, user: User, s) -> ChartRec:
    rec = s.get(ChartRec, chart_id)
    if not rec or rec.user_id != user.id:
        raise HTTPException(404, "Chart not found")
    return rec


# ------------------------------------------------------------------ auth
class Creds(BaseModel):
    username: str
    password: str = Field(min_length=6)


@app.get("/api/auth/status")
def auth_status():
    with SessionLocal() as s:
        return {"has_user": s.query(User).count() > 0}


@app.post("/api/auth/setup")
def setup(c: Creds):
    with SessionLocal() as s:
        if s.query(User).count() > 0:
            raise HTTPException(400, "The single user account already exists")
        u = User(username=c.username, password_hash=hash_pw(c.password))
        s.add(u)
        s.commit()
        return {"token": token_for(u), "username": u.username}


@app.post("/api/auth/login")
def login(c: Creds):
    with SessionLocal() as s:
        u = s.query(User).filter_by(username=c.username).first()
        if not u or not check_pw(c.password, u.password_hash):
            raise HTTPException(401, "Wrong username or password")
        return {"token": token_for(u), "username": u.username}


# ------------------------------------------------------------------ charts
class ChartIn(BaseModel):
    name: str
    birth_local: str            # "1975-03-21T14:35:00"
    tz: str = "Asia/Kolkata"
    lat: float
    lon: float
    place: str = ""
    notes: str = ""


class EventIn(BaseModel):
    matter_key: str
    date: str
    note: str = ""


def chart_json(r: ChartRec) -> dict:
    return {"id": r.id, "name": r.name, "birth_local": r.birth_local, "tz": r.tz, "lat": r.lat, "lon": r.lon,
            "place": r.place, "notes": r.notes,
            "events": [{"id": e.id, "matter_key": e.matter_key, "date": e.date, "note": e.note} for e in r.events]}


@app.get("/api/charts")
def list_charts(user: User = Depends(current_user)):
    with SessionLocal() as s:
        return [chart_json(r) for r in s.query(ChartRec).filter_by(user_id=user.id).order_by(ChartRec.name)]


@app.post("/api/charts")
def create_chart(c: ChartIn, user: User = Depends(current_user)):
    datetime.fromisoformat(c.birth_local)
    with SessionLocal() as s:
        r = ChartRec(user_id=user.id, **c.model_dump())
        s.add(r)
        s.commit()
        s.refresh(r)
        return chart_json(r)


@app.put("/api/charts/{chart_id}")
def update_chart(chart_id: int, c: ChartIn, user: User = Depends(current_user)):
    with SessionLocal() as s:
        r = get_chart(chart_id, user, s)
        for k, v in c.model_dump().items():
            setattr(r, k, v)
        s.commit()
        return chart_json(r)


@app.delete("/api/charts/{chart_id}")
def delete_chart(chart_id: int, user: User = Depends(current_user)):
    with SessionLocal() as s:
        s.delete(get_chart(chart_id, user, s))
        s.commit()
        return {"ok": True}


@app.post("/api/charts/{chart_id}/events")
def add_event(chart_id: int, e: EventIn, user: User = Depends(current_user)):
    datetime.fromisoformat(e.date)
    with SessionLocal() as s:
        r = get_chart(chart_id, user, s)
        r.events.append(EventRec(**e.model_dump()))
        s.commit()
        return chart_json(r)


@app.delete("/api/charts/{chart_id}/events/{event_id}")
def delete_event(chart_id: int, event_id: int, user: User = Depends(current_user)):
    with SessionLocal() as s:
        r = get_chart(chart_id, user, s)
        r.events = [e for e in r.events if e.id != event_id]
        s.commit()
        return chart_json(r)


# ------------------------------------------------------------------ calculations
@app.get("/api/matters")
def matters():
    ch = cast_local(datetime(2000, 1, 1, 12), 5.5, 13.0, 80.0)
    return [{"key": m.key, "title": m.title, "group": m.group, "one_time": m.one_time} for m in catalogue(ch)]


@app.get("/api/charts/{chart_id}/chart")
def chart_view(chart_id: int, ayanamsa: str = "KSK", user: User = Depends(current_user)):
    with SessionLocal() as s:
        rec = get_chart(chart_id, user, s)
        ch = chart_of(rec, ayanamsa)
    eng = Engine(ch)
    lord, passed, bal = D.balance(ch.planets["Moon"].lon)
    y, m, d = D.ymd(bal)
    dasas = [p.as_dict() for p in D.mahadasas(ch.utc, ch.planets["Moon"].lon, 120)]
    now = datetime.now(timezone.utc)
    cur = D.at(ch.utc, ch.planets["Moon"].lon, now, 4)
    return {"chart": ch.as_dict(), "significators": eng.table(), "houses": eng.house_table(),
            "aspects": [a.as_dict() for a in eng.aspects],
            "dasa_balance": {"lord": lord, "years": y, "months": m, "days": d}, "dasas": dasas,
            "current_period": cur.as_dict() if cur else None, "gems": gems(eng),
            "vighati": vighati_check(ch.utc, ch.lat, ch.lon, ch.planets["Moon"].lords.star)}


@app.get("/api/charts/{chart_id}/dasa")
def dasa_view(chart_id: int, ayanamsa: str = "KSK", depth: int = 2, user: User = Depends(current_user)):
    with SessionLocal() as s:
        ch = chart_of(get_chart(chart_id, user, s), ayanamsa)
    return [p.as_dict() for p in D.periods(ch.utc, ch.planets["Moon"].lon, min(depth, 4), 120)]


@app.get("/api/charts/{chart_id}/bio")
def bio_view(chart_id: int, ayanamsa: str = "KSK", aspects: bool = True, matter: str | None = None,
             here_lat: float | None = None, here_lon: float | None = None,
             user: User = Depends(current_user)):
    with SessionLocal() as s:
        rec = get_chart(chart_id, user, s)
        ch = chart_of(rec, ayanamsa)
        known = {}
        for e in rec.events:
            known.setdefault(e.matter_key, datetime.fromisoformat(e.date).replace(tzinfo=timezone.utc))
    now = datetime.now(timezone.utc)
    # RPs at generation time (decision #19: tie-break only), at the user's current place if given
    rp = rp_now(now, here_lat if here_lat is not None else ch.lat, here_lon if here_lon is not None else ch.lon, ayanamsa)
    out = make_bio(ch, now=now, use_aspects=aspects, rps=rp["ruling_planets"], known_events=known,
                   only=[matter] if matter else None)
    out["ruling_planets_now"] = {k: v for k, v in rp.items() if k != "chart"}
    return out


class RectIn(BaseModel):
    date: str                  # birth date "1975-03-21"
    time_from: str = "00:00"
    time_to: str = "23:59"
    tz: str = "Asia/Kolkata"
    lat: float
    lon: float
    judge_lat: float | None = None
    judge_lon: float | None = None
    judge_utc: str | None = None
    ayanamsa: str = "KSK"
    reject_retro: bool = True
    events: dict[str, str] = {}


@app.post("/api/rectify")
def rectify(r: RectIn, user: User = Depends(current_user)):
    tz = parse_tz(r.tz)
    start = datetime.fromisoformat(f"{r.date}T{r.time_from}")
    end = datetime.fromisoformat(f"{r.date}T{r.time_to}")
    if (end - start).total_seconds() > 6 * 3600:
        raise HTTPException(400, "Please give a range of at most 6 hours")
    ju = datetime.fromisoformat(r.judge_utc).replace(tzinfo=timezone.utc) if r.judge_utc else datetime.now(timezone.utc)
    res = rect_candidates(start, end, tz, r.lat, r.lon, ju, r.judge_lat or r.lat, r.judge_lon or r.lon,
                          r.ayanamsa, reject_retro=r.reject_retro)
    ev = {k: datetime.fromisoformat(v).replace(tzinfo=timezone.utc) for k, v in r.events.items()}
    if ev:
        for c in res["candidates"][:20]:
            fit = check_events(datetime.fromisoformat(c["mid_utc"]), r.lat, r.lon, ev, r.ayanamsa)
            c["event_fit"] = fit
        res["candidates"].sort(key=lambda c: (-(c.get("event_fit", {}).get("fit", 0)), -c["rp_score"]))
    return res


class HoraryIn(BaseModel):
    matter_key: str
    number: int | None = None
    scheme: int = 249
    lat: float
    lon: float
    when_utc: str | None = None
    ayanamsa: str = "KSK"
    years_ahead: float = 5


@app.post("/api/horary")
def horary(h: HoraryIn, user: User = Depends(current_user)):
    when = datetime.fromisoformat(h.when_utc).replace(tzinfo=timezone.utc) if h.when_utc else datetime.now(timezone.utc)
    try:
        return horary_judge(when, h.lat, h.lon, h.matter_key, h.number, h.scheme, h.ayanamsa, h.years_ahead)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/rp")
def rp(lat: float, lon: float, ayanamsa: str = "KSK", user: User = Depends(current_user)):
    r = rp_now(datetime.now(timezone.utc), lat, lon, ayanamsa)
    ch = r.pop("chart")
    r["asc"] = ch.cusp_lords[0].as_dict()
    r["moon"] = ch.planets["Moon"].lords.as_dict()
    return r


# ------------------------------------------------------------------ frontend (built files)
_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(_dist, "assets")), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        return FileResponse(os.path.join(_dist, "index.html"))
