"""Fixed KP tables: signs, lords, stars, Vimshottari years, sub divisions.

Sources: R1/R3 ch.1 (sign-star-sub scheme); R6 (249 table).
"""
from __future__ import annotations

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SHORT = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju",
         "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"}

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
# movable / fixed / common (dual)
SIGN_QUALITY = ["movable", "fixed", "common"] * 4

STARS = ["Aswini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Ardra", "Punarvasu",
         "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
         "Chitra", "Swati", "Visakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
         "Uttara Ashadha", "Sravana", "Dhanishta", "Satabhisha", "Purva Bhadrapada",
         "Uttara Bhadrapada", "Revati"]

DASA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18,
              "Jupiter": 16, "Saturn": 19, "Mercury": 17}
TOTAL_YEARS = 120

STAR_SPAN = 360.0 / 27          # 13°20'
PADA_SPAN = STAR_SPAN / 4       # 3°20'


def star_lord_of_index(i: int) -> str:
    return DASA_ORDER[i % 9]


def sequence_from(lord: str) -> list[str]:
    i = DASA_ORDER.index(lord)
    return DASA_ORDER[i:] + DASA_ORDER[:i]


# Exaltation / debilitation signs (index) — used only where sources use them (kp-rules #18)
EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
DEBILITATION = {p: (s + 6) % 12 for p, s in EXALTATION.items()}

# Hindu full aspects (houses counted from the planet, inclusive: 7 = opposite)
HINDU_ASPECTS = {"Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
                 "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
                 "Rahu": [5, 7, 9], "Ketu": [5, 7, 9]}

# Western aspects as tabulated in R1/R2 (kp-rules-notes "Aspect quality" and "ORBS").
# (name, angle, quality, strength rank 1=strongest, orb)
WESTERN_ASPECTS = [
    ("conjunction", 0.0, "by nature", 1, None),     # orb = half sum of planet orbs
    ("opposition", 180.0, "adverse", 2, 8.0),
    ("trine", 120.0, "good", 2, 6.0),
    ("quincunx", 150.0, "adverse", 2, 2.5),
    ("biquintile", 144.0, "good", 2, 3.0),
    ("sesquiquadrate", 135.0, "adverse", 2, 3.0),
    ("square", 90.0, "adverse", 3, 6.0),
    ("sextile", 60.0, "good", 3, 6.0),
    ("quintile", 72.0, "good", 3, 2.0),
    ("tredecile", 108.0, "good", 4, 2.5),
    ("126°", 126.0, "good", 4, 2.0),
    ("162°", 162.0, "good", 4, 2.0),
    ("54°", 54.0, "good", 4, 2.0),
    ("semi-square", 45.0, "adverse", 4, 2.0),
    ("decile", 36.0, "good", 4, 2.0),
    ("semi-sextile", 30.0, "good", 4, 2.0),
    ("vigintile", 18.0, "good", 4, 2.0),
]
# Planet orbs for conjunction (R1/R2): Sun 12, Moon 8, others 6 (applying)
PLANET_ORB = {"Sun": 12.0, "Moon": 8.0}
DEFAULT_ORB = 6.0
CUSP_CONJUNCTION_ORB = 6.0

# Combustion variants (kp-rules #6): R3 p.529 8°30'; R2: within 5° eclipsed, 10° ordinary
COMBUSTION_VARIANTS = {"R3": 8.5, "R2-eclipsed": 5.0, "R2-ordinary": 10.0}
