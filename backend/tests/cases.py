"""Confirmed cases from the Readers and magazines (docs/kp-test-cases.md, docs/magazine-notes.md).

Each case: birth (local time, tz offset hours, lat, lon), events {matter_key: [(date, printed periods)]}.
printed periods = the D–B–A(–S) lords the source states for the event ('' if not printed).
"""
from datetime import datetime

CASES = [
    dict(id="R5-J", src="R5 p.328", birth=datetime(1931, 10, 10, 13, 11), tz=5.5, lat=13.07, lon=80.25,
         events={"marriage": [("1950-09-01", "Rahu-Rahu-Rahu")]}),
    dict(id="R3-B", src="R3 p.145–149", birth=datetime(1928, 1, 29, 19, 6), tz=5.5, lat=13.07, lon=80.25,
         events={"death_mother": [("1947-04-11", "Venus-Mercury-Saturn")],
                 "marriage": [("1947-07-06", "Venus-Ketu-Venus")],
                 "death_father": [("1952-07-15", "Sun-Mercury-Venus")],
                 "job": [("1952-01-15", "Sun-Saturn-Moon")]}),
    dict(id="R3-H", src="R3 p.189–195 (LMT)", birth=datetime(1920, 8, 7, 7, 10), tz=73.27 / 15, lat=22.0, lon=73.27,
         events={"job": [("1941-12-28", "Sun-Venus-Jupiter")],
                 "death_father": [("1964-06-27", "")]}),
    dict(id="R5-L", src="R5 p.189", birth=datetime(1893, 9, 9, 8, 53), tz=5.5, lat=13.07, lon=80.25,
         events={"death_father": [("1917-01-15", "")]}),
    dict(id="M-07 Nehru", src="MC (Nehru)", birth=datetime(1889, 11, 14, 23, 30), tz=5.5, lat=25.43, lon=81.87,
         events={"death": [("1964-05-27", "Rahu-Mercury-Rahu")]}),
    dict(id="Indira", src="MC_132 KSK", birth=datetime(1917, 11, 19, 23, 39, 16), tz=5.5, lat=25.47, lon=81.9,
         events={"death_mother": [("1936-02-28", "Mars-Sun-Venus")],
                 "marriage": [("1942-03-26", "Rahu-Saturn-Saturn")],
                 "child": [("1944-08-20", "Rahu-Saturn-Jupiter"), ("1946-12-14", "Rahu-Mercury-Saturn")],
                 "death_spouse": [("1960-09-08", "Jupiter-Mercury-Rahu")],
                 "death_father": [("1964-05-27", "Jupiter-Venus-Saturn")],
                 "seniority": [("1959-02-08", "Jupiter-Saturn-Jupiter")]}),
    # M-05 removed: printed balance (Rahu 0y11m14d) does not fit 23-7-1938 — birth year OCR-damaged ("193$").
    dict(id="Kennedy", src="MC_060 Mani", birth=datetime(1917, 5, 29, 15, 0), tz=-5.0, lat=42.33, lon=-71.12,
         events={"death": [("1963-11-22", "Jupiter-Jupiter-Rahu")]}),
    dict(id="Sharma-job", src="MC_08x P.R. Sharma", birth=datetime(1935, 5, 14, 4, 43), tz=5.5, lat=30.92, lon=75.9,
         events={"job": [("1958-08-11", "Rahu-Saturn-Saturn")]}),
    dict(id="Chandak-business", src="MC_08x Chandak", birth=datetime(1942, 7, 17, 7, 27, 17), tz=5.5, lat=27.72, lon=68.88,
         events={"business": [("1962-03-21", "Venus-Ketu-Mercury")]}),
    dict(id="Child-verif", src="MC_08x", birth=datetime(1947, 7, 11, 17, 20), tz=5.5, lat=28.12, lon=74.65,
         events={"child": [("1963-01-24", "Venus-Venus-Ketu")]}),
    dict(id="Bikaner", src="MC_08x Chandak", birth=datetime(1939, 7, 12, 7, 17, 44), tz=5.5, lat=28.02, lon=73.37,
         events={"marriage": [("1962-03-09", "Mars-Mars-Saturn")]}),
    dict(id="Kurnool", src="MC_090 V. Krishnamurty", birth=datetime(1934, 1, 20, 22, 45), tz=5.5, lat=15.93, lon=78.83,
         events={"marriage": [("1961-06-24", "Venus-Venus-Saturn")]}),
    dict(id="Bhattacharya", src="MC_119", birth=datetime(1925, 4, 6, 4, 0), tz=5.5, lat=23.98, lon=85.37,
         events={"job": [("1952-05-24", "Moon-Rahu-Saturn")]}),
    dict(id="Gaya-widow", src="MC_08x S.N. Mishra", birth=datetime(1946, 12, 16, 9, 18, 56), tz=5.5, lat=24.8, lon=85.02,
         events={"death_spouse": [("1966-03-29", "Rahu-Rahu-Venus")]}),
    dict(id="Infant", src="MC_10x Rangaswamy", birth=datetime(1968, 7, 29, 0, 26), tz=5.5, lat=11.0, lon=77.0,
         events={"death": [("1968-07-29", "")]}),
]
