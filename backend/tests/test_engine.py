"""Engine checks against values printed in the Readers and magazines."""
from datetime import datetime, timezone

import pytest

from kp import dasa as D
from kp.chart import ayanamsa, cast_local, julday
from kp.subs import horary_point, lords_of, table_249
from kp.windows import bio


def test_249_table():
    t = table_249()
    assert len(t) == 249
    assert (t[0]["sign"], t[0]["star"], t[0]["sub"]) == ("Mars", "Ketu", "Ketu")
    assert (t[-1]["sign"], t[-1]["star"], t[-1]["sub"]) == ("Jupiter", "Mercury", "Saturn")


def test_number_51_of_108():          # MC_056: Virgo 16°40'–20°, Hasta pada 3
    a, b = horary_point(51, 108)
    assert round(a, 4) == 166.6667 and round(b, 4) == 170.0
    L = lords_of(a + 0.01)
    assert (L.sign, L.star) == ("Mercury", "Moon")


@pytest.mark.parametrize("year,printed", [(1913, 22 + 33 / 60), (1919, 22 + 38 / 60), (1929, 22 + 46 / 60),
                                          (1939, 22 + 55 / 60), (1963, 23 + 15 / 60), (1968, 23 + 19 / 60)])
def test_ksk_ayanamsa(year, printed):
    a = ayanamsa(julday(datetime(year, 7, 1, tzinfo=timezone.utc)), "KSK")
    assert abs(a - printed) < 2 / 60


def test_alibag_cusps():               # R5-A: I 18°22' Cancer, IV 17°01' Libra
    c = cast_local(datetime(1924, 12, 23, 21, 0), 5.5, 18.65, 72.92)
    assert abs(c.cusps[0] - (90 + 18 + 22 / 60)) < 10 / 60
    assert abs(c.cusps[3] - (180 + 17 + 1 / 60)) < 10 / 60


def test_jullundur_asc():              # 31-10-1919 3:53:48 AM: Asc 6°53' Virgo
    c = cast_local(datetime(1919, 10, 31, 3, 53, 48), "Asia/Kolkata", 31 + 19 / 60, 75.3)
    assert abs(c.cusps[0] - (150 + 6 + 53 / 60)) < 3 / 60


@pytest.mark.parametrize("birth,tz,lat,lon,event,printed", [
    (datetime(1889, 11, 14, 23, 30), 5.5, 25.43, 81.87, datetime(1964, 5, 27), ("Rahu", "Mercury", "Rahu")),
    (datetime(1931, 10, 10, 13, 11), 5.5, 13.07, 80.25, datetime(1950, 9, 1), ("Rahu", "Rahu", "Rahu")),
    (datetime(1917, 11, 19, 23, 39, 16), 5.5, 25.47, 81.9, datetime(1942, 3, 26), ("Rahu", "Saturn", "Saturn")),
    (datetime(1917, 11, 19, 23, 39, 16), 5.5, 25.47, 81.9, datetime(1960, 9, 8), ("Jupiter", "Mercury", "Rahu")),
])
def test_printed_periods(birth, tz, lat, lon, event, printed):
    c = cast_local(birth, tz, lat, lon)
    p = D.at(c.utc, c.planets["Moon"].lon, event.replace(tzinfo=timezone.utc), 3)
    assert p.lords == printed


def test_bio_runs_and_marks_past():
    c = cast_local(datetime(1931, 10, 10, 13, 11), 5.5, 13.07, 80.25)
    b = bio(c, now=datetime(2026, 1, 1, tzinfo=timezone.utc),
            known_events={"marriage": datetime(1950, 9, 1, tzinfo=timezone.utc)}, only=["marriage"])
    v = b["matters"][0]["variants"][0]
    assert v["windows"] and all(w["status"] in ("PAST", "CURRENT", "FUTURE") for w in v["windows"])
    assert v["known_event_check"]["rank_of_its_window"] is not None
