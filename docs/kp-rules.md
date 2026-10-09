# KP rules for the app — for user review

This document is the rulebook the app will implement. Every rule comes from KP Readers 1–6 (R1–R6) or the *Astrology & Athrishta* magazines 1963–1971 (MC_xxx = chunk in `mc/`). The detailed sources and line references are in `docs/kp-rules-notes.md` (Readers) and `docs/magazine-notes.md` (magazines).

Markers used:
- **[KSK]**: stated by K. S. Krishnamurti himself. **[contrib]**: stated by a magazine contributor (weaker authority).
- **DECIDE**: a contradiction or open choice. I give my recommended default; you confirm or change it.
- **GAP**: the texts give no rule; the app will say "no rule in the sources" rather than invent one.
- **APP CHOICE**: an implementation detail the texts do not fix (e.g. how to rank windows). It is labelled so it is never mistaken for a KP rule.

---

## 1. Chart casting

### 1.1 Ephemeris
- KSK: "Drik ganitha … Forget Vakya. Take Raphael's Ephemeris and Krishnamurti's ayanamsa alone." (R1 l.436–441; magazines.)
- **Decision:** Swiss Ephemeris (modern drik positions; Raphael's figures were the best of their day and agree with it to within the rounding the books use). Tropical positions computed first, then the ayanamsa subtracted, exactly as KSK did with Raphael.
- Validation: every worked chart in `docs/kp-test-cases.md` and the CONFIRMED magazine cases must reproduce the printed cusps and planets to within a few minutes of arc before the app is released.

### 1.2 Ayanamsa
- KSK: use Krishnamurti's ayanamsa only; others are "useless if you want to follow K.P." (R1 preface). The zero point is opposite Spica; the rate is Newcomb's 50.2486″/year [MC Kannan article; KSK].
- KSK also says Lahiri is "almost correct" and "use Newcomb's or Lahiri's" — the difference is about 5–6′, KSK being smaller (MC notes l.306).
- Printed check values (KSK ayanamsa): 1913 22°33′; 1919 22°38′; 1922 22°40′; 1929 22°46′; 1939 22°55′; 1963 23°15′; 1966 23°16′; 1968 23°19′; 1970 23°23′.
- **Default:** Swiss Ephemeris "Krishnamurti" ayanamsa, checked against the values above. **Option:** Lahiri, shown as an alternative in settings.

### 1.3 Houses
- Placidus cusps (Raphael's Tables of Houses), tropical cusps minus ayanamsa (R1; M1968 worked example, Agra 15-5-1963).
- A house (bhava) runs from its cusp to the next cusp. Occupation is by bhava, not by sign ("Moon is in the 6th as per K.P. but tradition says 7", R3).
- The lord of a house is the lord of the sign its cusp is in. An intercepted sign gives no lordship; one planet may own two houses (R3 l.~14690).
- Traditional bhava-chalit tables are "misleading" (R3).

### 1.4 Lagna only
- "In the research after 1967 it was found that we have to take always the Lagna alone. Never judge whether Moon sign or Lagna is stronger" (R3 l.~10725; reconfirmed R3 l.~18680: "since end 1965").
- Earlier magazine cases (1964–Jan 1968) read from the Moon sign when the lagna was "afflicted". **Decision:** lagna/cusps only. The Moon-sign method is not implemented (listed under excluded methods).

### 1.5 Birth time and place
- The birth moment is when the child is severed from the mother (separate breathing) [KSK].
- Clock time → UT via the IANA time-zone database, including war time (India +1 h in 1942–45). Where the database and the user disagree, the user can override the offset; rectification (§6) resolves the doubtful hour as KSK did in the war-time example (R3 l.~21700).
- Local sidereal time: the Swiss Ephemeris computes it directly. (KSK's manual method — 10 s/hour correction, ephemeris at 5:30 PM IST — is not needed but is the check for the printed examples.)

### 1.6 Nodes
- Mean node (KSK's ephemeris used the mean node; the printed node positions match the mean node). Ketu = Rahu + 180°.
- Nodes have no stations; they are never treated as retrograde for the retrograde-denial rules (MC_113; MC_124 prints "ever retrograde", judged an OCR/wording slip — both texts say they "never retrace their pathway").

### 1.7 Planets used
- Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu.
- Uranus and Neptune: "In K.P. we do not include Neptune"; they own no stars and are not significators (R3 l.~15760, l.~7340). They may be shown for information only. Some mode-of-death descriptions in R2/R3 mention them → shown as descriptive text only.
- Pars Fortuna: R3 uses it once (gives results of its star lord). **Default:** descriptive only, not used for scoring.

### 1.8 Dasa
- Vimshottari only ("Udu dasa"), from the Moon's exact position (R1 l.409–410). Year = 365.25 days (**APP CHOICE**; KSK's tables use the solar year — the printed dasa balances in the test cases decide whether 365.25 or 360 is closer; default 365.25 and verify).
- Levels: dasa, bhukti, antara, sookshma (the books use down to sookshma; prana is not used).

### 1.9 Sign–star–sub table
- Star = 13°20′; each star split into 9 subs in Vimshottari proportion, starting from the star lord (Ke Ve Su Mo Ma Ra Ju Sa Me order). Sub sizes: Sun 40′, Moon 1°06′40″, Mars/Ketu 46′40″, Rahu 2°, Jupiter 1°46′40″, Saturn 2°06′40″, Mercury 1°53′20″, Venus 2°13′20″ (R3 ch.1).
- Subs cut by sign boundaries give 249 divisions; the horary numbers 1–249 follow that table (R6). Sub-sub = the same division applied inside the sub.

---

## 2. The significator engine (applies to every matter)

### 2.1 What each layer means
- **Sign** = source/quality; **star lord** = the nature of the result (the houses the star lord occupies and owns); **sub lord** = whether it is favourable or not — "the star lord proposes; the sub lord seconds or opposes" (R3 l.~950, l.~3420; magazines repeatedly).
- A planet gives the results of its star lord's houses most strongly, then of the house it occupies, then of the houses it owns ("star lord > occupation > ownership", R2 l.~11900; R3 p.39–61; MC_139).
- For the star lord itself: the house it *occupies* is stronger than the houses it *owns* (R3 p.114–115).
- If no planet sits in a planet's stars, that planet gives its own houses' results strongly (R3 l.~6700).

### 2.2 Significators of a house (canonical order, strongest first) — R3 l.~14660, l.~7270, l.~17500
1. Planets in the star of the **occupants** of the house.
2. The **occupants**.
3. Planets in the star of the **lord** of the house.
4. The **lord** (owner of the cusp's sign).
5. Planets **conjoined** with the above.
6. Planets **aspected** by the above.

- Strength statement (R3 p.318–319, l.~13730): occupant of a star > lord of the star; star > sign; occupant of a sign > lord of the sign.
- **DECIDE (aspects for level 5–6):** R3 uses Western degree aspects (conjunction, opposition, trine, square, sextile, 108°, semi-square) in the dasa principle, and Hindu full aspects (Jupiter 5/9, Saturn 3/10, Mars 4/8) for nodes. **Default:** conjunction only for levels 5–6 within the same bhava and a small orb (APP CHOICE: 3°20′, one pada), plus Hindu full aspects for nodes as R3 does. Western aspects are listed as excluded from scoring (§7) — you may switch them on.

### 2.3 Cusp sub lords decide the promise
- "The sub lord of each cusp gives the correct solution of that house (promise); significators show the time" (R3 l.~18680).
- The cusp's star lord: planets in that star lord's star are significators. The cusp's sub lord: planets in the sub lord's star are "very strong" significators; the cusp sub lord itself often turns out to be the timing planet (R3 l.~13600).
- The benefic/malefic test for a house: a significator in the star **and** sub of significators of the 6th, 8th or 12th counted *from that house* harms that house (R3 l.~6180). "12th to any house is its negation" (R2).

### 2.4 Fruitful significators
- Among the significators, the useful ones are those whose **sub lord** is itself a significator of the matter's houses (R4 p.118; R3 finance section).
- Reject a planet that signifies the matter's houses **and** their 12ths (e.g. 2/7/11 and 1/6/10 for marriage) — "it cannot give" (R4 p.118, p.150).
- Then select among the fruitful ones with the **ruling planets** (RPs) at the moment of judgment (R3 l.~13400; R6).

### 2.5 Ruling planets
- At a given moment: (1) day lord, (2) Moon's star lord, (3) Moon's sign lord, (4) lagna sign lord, (5) lagna star lord; plus a node that is in the sign of, conjoined with, or aspected by one of them (R3 l.~21250; R6).
- The day runs sunrise to sunrise for the day lord [KSK]. The Moon's star and sign change at their real ingress (a contributor's "change only after sunrise" is rejected, MC notes l.6590).
- Horary/RP use only: reject an RP that is in the star of a retrograde planet (R6).
- **DECIDE (RP strength order):** variants found — lagna star lord > lagna sign lord > Moon star lord > Moon sign lord > day lord (R6 usual list); "star lord > sign lord > day lord" (R3 l.~12370); contributors give lagna lord first (MC_131). **Default:** the R6 order; the app uses RPs mainly as a filter (yes/no), so the order only breaks ties.

### 2.6 Nodes (Rahu, Ketu)
- A node gives the results of: the planets it is conjoined with, the planets aspecting it, its star lord, and its sign lord. It is **stronger** than the planets it represents ("Rahu or Ketu will ever be stronger than the lord of the house in which they are posited and also the planets with which they are conjoined", R3 l.~8890).
- A planet in a node's sub gives the node's results [contrib, consistent with R3].
- **DECIDE (order of node agency):**
  - (a) conjoined → aspecting → star lord → sign lord — KSK, "this order is to be followed as this alone is correct" (MC Jan 1965; MC_120; MC_139).
  - (b) star lord first, unless the node is in its own star (MC_123).
  - (c) other orders in R6.
  - **Default:** (a), and the node also carries every house its agents signify (so the order only matters for ranking).

### 2.7 Dasa principle (R3 l.19248+, "to be strictly and universally applied")
- The dasa lord's nature = how the result comes; houses it owns = source; its star lord's houses = what it predominantly gives; its sub lord benefic → realised, malefic → denial/anxiety.
- **Dasa lord supremacy:** a bhukti can give a matter only if the dasa lord also signifies it (magazines, many cases). A bhukti gives the houses common to dasa and bhukti lords.
- "A dasa, B bhukti, A antara give the result to the full extent" (R3 l.~9560).
- Do not split a dasa into halves; a planet owning good and bad houses gives the good in bhuktis whose lords are in benefic subs and the bad in the others (R3 l.~10400).
- Western aspects between dasa and bhukti lords (R3 (e)–(h)): see §2.2 DECIDE; default not scored.

### 2.8 Retrogression
- **Natal:** retrogression makes no difference to the promise [KSK, MC_139 and earlier] — contributors who reject retrograde natal planets are overruled. One R3 case (10th cusp sub lord Saturn retrograde → no ministership, R3 l.~17125) is treated as horary-type evidence; **DECIDE**, default: natal ignores retrogression.
- **Horary / RP selection:** a cusp sub lord in the star of a retrograde planet → denial; a retrograde sub lord → delay until it turns direct and passes its station point; retrograde in the star of a retrograde planet → never. Nodes are exempt (R6; MC_113).
- Timing: a retrograde planet gives results before it turns retrograde or after it is direct (R3 l.~13500).

### 2.9 Combustion
- **DECIDE:** "within 8°30′ of the Sun" (R3 p.529) vs other figures in R1; R6 p.151 has a rule for planets in the star of an eclipsed planet as cusp sub lords, which the Institute's own check says gives both good and bad. **Default:** not used in scoring; shown as information.
