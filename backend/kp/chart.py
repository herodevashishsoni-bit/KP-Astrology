"""Chart casting the KP way (kp-rules §1).

Tropical positions and Placidus cusps from the Swiss Ephemeris, then the
ayanamsa subtracted, exactly as KSK did with Raphael's ephemeris and tables.
Mean node; Ketu = Rahu + 180°.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from .constants import (DEBILITATION, EXALTATION, PLANETS, SIGN_LORDS, SIGNS)
from .subs import Lords, fmt_dms, lords_of

AYANAMSAS = {"KSK": swe.SIDM_KRISHNAMURTI, "Lahiri": swe.SIDM_LAHIRI}
_SWE_IDS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE}
_FLAGS = swe.FLG_SPEED | swe.FLG_MOSEPH  # no ephemeris files needed (Moshier, arc-second level)


def to_utc(local: datetime, tz: str | float | None) -> datetime:
    """Local clock time → UTC. tz is an IANA name (handles war time) or a fixed offset in hours."""
    if local.tzinfo is not None:
        return local.astimezone(timezone.utc)
    if isinstance(tz, (int, float)):
        return (local - timedelta(hours=float(tz))).replace(tzinfo=timezone.utc)
    return local.replace(tzinfo=ZoneInfo(tz or "Asia/Kolkata")).astimezone(timezone.utc)


def julday(utc: datetime) -> float:
    h = utc.hour + utc.minute / 60 + (utc.second + utc.microsecond / 1e6) / 3600
    return swe.julday(utc.year, utc.month, utc.day, h)


def jd_to_utc(jd: float) -> datetime:
    y, m, d, h = swe.revjul(jd)
    return datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)


def ayanamsa(jd: float, name: str = "KSK") -> float:
    swe.set_sid_mode(AYANAMSAS[name])
    return swe.get_ayanamsa_ut(jd)


@dataclass
class Body:
    name: str
    lon: float
    speed: float
    lords: Lords
    house: int = 0  # bhava (cusp to cusp)

    @property
    def retro(self) -> bool:
        return self.name not in ("Rahu", "Ketu") and self.speed < 0

    @property
    def sign_index(self) -> int:
        return int(self.lon // 30)

    def dignity(self) -> str | None:
        if self.name in EXALTATION:
            if self.sign_index == EXALTATION[self.name]:
                return "exalted"
            if self.sign_index == DEBILITATION[self.name]:
                return "debilitated"
            if SIGN_LORDS[self.sign_index] == self.name:
                return "own sign"
        return None

    def as_dict(self) -> dict:
        return {"name": self.name, "lon": round(self.lon, 6), "dms": fmt_dms(self.lon),
                "sign": SIGNS[self.sign_index], "speed": round(self.speed, 6),
                "retro": self.retro, "house": self.house, "dignity": self.dignity(),
                **{f"{k}_lord": v for k, v in self.lords.as_dict().items() if k in ("sign", "star", "sub", "subsub")},
                "star_name": self.lords.star_name}


@dataclass
class Chart:
    jd: float
    utc: datetime
    lat: float
    lon: float
    ayanamsa_name: str
    ayanamsa: float
    cusps: list[float]                 # index 0..11 → houses 1..12
    planets: dict[str, Body]
    cusp_lords: list[Lords] = field(default_factory=list)
    sidereal_time: float = 0.0
    tropical_asc: float = 0.0

    def house_of(self, lon: float) -> int:
        lon %= 360
        for i in range(12):
            a, b = self.cusps[i], self.cusps[(i + 1) % 12]
            if (b - a) % 360 > (lon - a) % 360:
                return i + 1
        return 12

    def owner_houses(self, planet: str) -> list[int]:
        """Houses whose cusp falls in a sign owned by planet (R3: lordship by cusp sign)."""
        return [i + 1 for i, c in enumerate(self.cusps) if SIGN_LORDS[int(c // 30)] == planet]

    def occupants(self, house: int) -> list[str]:
        return [p for p, b in self.planets.items() if b.house == house]

    def house_lord(self, house: int) -> str:
        return SIGN_LORDS[int(self.cusps[house - 1] // 30)]

    def as_dict(self) -> dict:
        return {
            "utc": self.utc.isoformat(), "jd": self.jd, "lat": self.lat, "lon": self.lon,
            "ayanamsa_name": self.ayanamsa_name, "ayanamsa": self.ayanamsa,
            "ayanamsa_dms": fmt_dms(self.ayanamsa, in_sign=False),
            "sidereal_time_hours": round(self.sidereal_time, 6),
            "cusps": [{"house": i + 1, "lon": round(c, 6), "dms": fmt_dms(c), "sign": SIGNS[int(c // 30)],
                       **{f"{k}_lord": v for k, v in self.cusp_lords[i].as_dict().items() if k in ("sign", "star", "sub", "subsub")},
                       "star_name": self.cusp_lords[i].star_name}
                      for i, c in enumerate(self.cusps)],
            "planets": [b.as_dict() for b in self.planets.values()],
        }


def cast(utc: datetime, lat: float, lon: float, ayanamsa_name: str = "KSK") -> Chart:
    jd = julday(utc)
    aya = ayanamsa(jd, ayanamsa_name)
    bodies: dict[str, Body] = {}
    for name in PLANETS:
        if name == "Ketu":
            r = bodies["Rahu"]
            kl = (r.lon + 180) % 360
            bodies["Ketu"] = Body("Ketu", kl, r.speed, lords_of(kl))
            continue
        xx, _ = swe.calc_ut(jd, _SWE_IDS[name], _FLAGS)
        sl = (xx[0] - aya) % 360
        bodies[name] = Body(name, sl, xx[3], lords_of(sl))
    cusps_t, ascmc = swe.houses(jd, lat, lon, b"P")
    cusps = [(c - aya) % 360 for c in cusps_t[:12]]
    ch = Chart(jd, utc, lat, lon, ayanamsa_name, aya, cusps, bodies,
               [lords_of(c) for c in cusps], sidereal_time=swe.sidtime(jd) + lon / 15.0,
               tropical_asc=ascmc[0])
    ch.sidereal_time %= 24
    for b in bodies.values():
        b.house = ch.house_of(b.lon)
    return ch


def cast_local(local: datetime, tz, lat: float, lon: float, ayanamsa_name: str = "KSK") -> Chart:
    return cast(to_utc(local, tz), lat, lon, ayanamsa_name)


def sunrise_utc(day_utc: datetime, lat: float, lon: float, before: bool = True) -> datetime:
    """Sunrise that starts the astrological day containing day_utc (KSK: day runs sunrise to sunrise)."""
    jd = julday(day_utc)
    geo = (lon, lat, 0.0)
    flags = swe.CALC_RISE | swe.BIT_DISC_CENTER
    _, t = swe.rise_trans(jd - 1.0, swe.SUN, flags, geo, 0, 0, swe.FLG_MOSEPH)
    rise = t[0]
    # move forward to the last sunrise <= jd
    while True:
        _, t2 = swe.rise_trans(rise + 0.01, swe.SUN, flags, geo, 0, 0, swe.FLG_MOSEPH)
        if t2[0] > jd:
            break
        rise = t2[0]
    return jd_to_utc(rise)
