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
- The early rule as KSK himself stated it (MC_057 "Smooth life", MC_059 "Defect from birth", MC_060 "Which is half-baked"):
  - Lagna afflicted and Moon sign not → take the Moon sign.
  - Lagna not afflicted, or both afflicted → take the lagna.
  - "Afflicted" means Saturn, Rahu, Ketu or Mars in the sign, whether before or after the degree ("a snake in the room").
  - When in doubt, use the RPs.

  KSK also used it in "Building—will I shift?" (MC_056). The later R3 statement supersedes it, so these cases are validated on the lagna only.

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
- **New evidence for this DECIDE (MC_061, Jan 1967, official statement of the method):**
  - The method statement says: "Follow western system of houses; aspects and progression, Hindu aspects."
  - So in 1967 KSK's own method included Western aspects and even progressions. Many 1966 cases use 108°, 144°, 135° and other aspects, and transit aspects to natal positions.
  - The later Readers drop progressions. R3 still uses degree aspects in the dasa principle.

  Because you asked for no Western methods, the default stays "off". This is the single biggest source-vs-preference conflict, so please confirm.
- Inverse aspect rule [KSK, MC_060]: a good aspect or conjunction of lord 12 with the lords of 2, 6 and 10 harms; an adverse aspect from lord 12 helps. This applies only if aspects are switched on.

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
- RPs are taken when the astrologer judges and answers ("when the urge is there"), not when the question was asked [KSK, MC_057 "Fortune—from when"].
- RPs are used to confirm and to select 3–4 significators when many come up. "It does not mean that the RPs promise success" [KSK, MC_058].
- RPs reveal correctly only with the KP ayanamsa [KSK, MC_117].
- **DECIDE (RP strength order):** variants found — lagna star lord > lagna sign lord > Moon star lord > Moon sign lord > day lord (R6 usual list); "star lord > sign lord > day lord" (R3 l.~12370); contributors give lagna lord first (MC_131). **Default:** the R6 order; the app uses RPs mainly as a filter (yes/no), so the order only breaks ties.

### 2.6 Nodes (Rahu, Ketu)
- A node gives the results of: the planets it is conjoined with, the planets aspecting it, its star lord, and its sign lord. It is **stronger** than the planets it represents ("Rahu or Ketu will ever be stronger than the lord of the house in which they are posited and also the planets with which they are conjoined", R3 l.~8890).
- A planet in a node's sub gives the node's results [contrib, consistent with R3].
- **DECIDE (order of node agency):**
  - (a) conjoined → aspecting → star lord → sign lord — KSK, "this order is to be followed as this alone is correct" (MC Jan 1965; MC_120; MC_139).
  - (b) star lord first, unless the node is in its own star (MC_123).
  - (c) other orders in R6.
  - **Default:** (a), and the node also carries every house its agents signify (so the order only matters for ranking).
- **Substitution** [KSK, MC_058 "Service or independent work"; MC_060]:
  - If a planet selected as significator owns the sign that a node occupies, substitute the node, which is stronger ("tenants are stronger than the owner; nodes are ever tenants").
  - A node in either sign of a planet represents both of that planet's signs and houses.
  - A node conjoined with, aspected by, or in the sign of an RP is a stronger RP (KSK editor's note, MC_057).
  - An unconjoined node in the sign of planet X gives the houses of both of X's signs (MC_057 example: Pisces lagna, node in Aries → houses 2 and 9).

### 2.7 Dasa principle (R3 l.19248+, "to be strictly and universally applied")
- The dasa lord's nature = how the result comes; houses it owns = source; its star lord's houses = what it predominantly gives; its sub lord benefic → realised, malefic → denial/anxiety.
- **Dasa lord supremacy:** a bhukti can give a matter only if the dasa lord also signifies it (magazines, many cases). A bhukti gives the houses common to dasa and bhukti lords.
- "A dasa, B bhukti, A antara give the result to the full extent" (R3 l.~9560).
- Do not split a dasa into halves; a planet owning good and bad houses gives the good in bhuktis whose lords are in benefic subs and the bad in the others (R3 l.~10400).
- Western aspects between dasa and bhukti lords (R3 (e)–(h)): see §2.2 DECIDE; default not scored.
- "If four significators come up, stop; but if the dasa lord is not one of them, check whether it is connected. If not connected, the matter will not happen in its dasa even if the bhukti lord is a significator" [KSK, MC_058]. "The dasa lord is ever stronger than the bhukti lord" (MC_060).
- **Sub classification** [KSK, MC_058]: take planets A, B and C in the star of D.
  - A in the sub of D itself → fulfils.
  - B in the sub of a lord owning the 6th, 8th or 12th from D's houses → incapable.
  - C in the sub of a lord unconnected with both groups → neutral, which means **delay** ("a few disappointments, then success"), not denial.
  - **APP:** windows whose sub lord is neutral are labelled "with delay/obstacles".
- **Plurality:** the bhukti lord in a dual sign → two engagements at once, e.g. service and practice, or two places [KSK, MC_058]. Changes within a dasa come from the bhukti lord; dasa and bhukti lords must "both vote".
- A in the star of B → A gives B's matters in A dasa, B bhukti (MC_059 "Return from overseas").
- Sub of lord 12 (or its node agent) → loss; sub of lord 6 (or a node in 6) → bank position improves [KSK, MC_057 "Rajayogathipathi"].

### 2.8 Retrogression
- **Natal:** retrogression makes no difference to the promise [KSK, MC_139 and earlier] — contributors who reject retrograde natal planets are overruled. One R3 case (10th cusp sub lord Saturn retrograde → no ministership, R3 l.~17125) is treated as horary-type evidence; **DECIDE**, default: natal ignores retrogression.
- **Horary / RP selection:** a cusp sub lord in the star of a retrograde planet → denial; a retrograde sub lord → delay until it turns direct and passes its station point; retrograde in the star of a retrograde planet → never. Nodes are exempt (R6; MC_113).
- Timing: a retrograde planet gives results before it turns retrograde or after it is direct (R3 l.~13500).

### 2.9 Combustion
- **DECIDE:** "within 8°30′ of the Sun" (R3 p.529) vs other figures in R1; R6 p.151 has a rule for planets in the star of an eclipsed planet as cusp sub lords, which the Institute's own check says gives both good and bad. **Default:** not used in scoring; shown as information.

---

## 3. Life matters (what the bio shows)

For every matter the app shows: **promise** (from the cusp sub lord — yes / no / conditional), **description** where the texts give one, and the **top 3 time windows** (dasa–bhukti–antara periods, see §4). Windows already in the past are marked PAST. Unless stated, significators are found with §2.2 and filtered with §2.4.

### 3.1 Longevity and death of the native — R2 ch.17; R3 p.157–169; R6 p.154–160
- Houses: longevity 1, 3, 8; their 12ths (12, 2, 7) = maraka/moksha. **Marakas for everyone: 2 and 7.**
- **Badhaka:** movable lagna → 11th; fixed → 9th; common → 7th. It applies only to health and longevity.
- **Span:** Asc sub lord in the star of a significator of badhaka/maraka → short life; otherwise judge the Asc sub lord benefic (lords of 1, 5, 9, 10) or malefic (lords of 6, 8, 12) (R3). Bands: short 0–33, middle 33–66, long 66–100 (R3 l.~7200).
- If long life is promised, an evil period in youth gives illness, not death (R2).
- **Asc sub lord in the star of a significator of:** 6 → disease, not death; 8 → accident; 12 → long bed rest/hospital (R6).
- **Timing:** death = the conjoined period of the significators of the badhaka and maraka houses (order: planets in the star of badhaka occupants > occupants > planets in the star of the badhaka lord > the lord; then the marakas 2 and 7 the same way), within the band the span allows; confirmed by RPs and Sun/Moon transits (R3 Ex.1, death 18-2-1970; R6 p.154–157).
- Saturn in the 8th is an exception as a killer: it gives long life (R3 p.157).
- The same period can give a child (2/5/11) and the mother's death, when its lords are also maraka/badhaka significators. Case: girl born 9 AM 30-1-1966, mother died at the birth (MC_059).
- Contributor rules (M.S. Mani, MC_060 Kennedy case), used only as tie-breakers, **DECIDE**:
  - "Planets in the sub of the lagna lord cannot cause death in their periods."
  - Use "subha kendradhipati" (lord of a benefic kendra) as a killer.
  - Default: off. KSK (MC_139) says kendra lordship is irrelevant and only maraka/badhaka significance counts.
- **Mode of death:** the 8th cusp sub lord, its star lord, sign lord (R3 l.~7480; R2). Jupiter peaceful; Mars sudden/accident/fire/surgery (fiery sign fire/violence, watery drowning, airy haemorrhage); Saturn chronic, lingering, falls; Moon conjoined with many planets in the 8th → sudden, unnatural (R5 p.241). Death cause by the star lord of a Moon in 8 signifying maraka/badhaka (R5 p.241).
- **Place of death:** the 8th cusp sub lord signifying 1, 4, 10 → home; 3 → during a short journey; 6, 8, 12 → hospital/jail/unknown place; 9 → far away (R3 p.168).
- **Self-caused / suicide:** lagna lord in 8, or a planet in 8 in the star of the lagna lord, or lord 8 conjoined lagna lord (R2); the 8th sub lord in the star of a significator of badhaka/maraka + 8, connected with Mars (R6 p.258). **DECIDE:** show this or not (default: shown only inside the mode-of-death text, worded as the texts word it).
- **Accident:** the 8th sub lord in the star of a significator of 8 → accident; + 6 fever after; + 12 hospital; + badhaka/maraka → death unless longevity is promised (R6 p.159). Journey accident: significator of 3 or 9 also of 6 and 8 (R3).
- Birth and death happen once; other events repeat (R3 l.~16200). The app gives the **single best** death window (plus two runners-up only as "danger to life" windows).
- **Directness:** the user asked for direct statements; KSK predicts death in many published cases. R3 quotes a Western caution not to predict death — noted, not followed.

### 3.2 Death of family members — "take the relative's house as their lagna; their marakas are the 2nd and 7th from it, and their badhaka is counted from it" (R6 p.83–86; R3 p.145–149)
| Relative | Their house | Death houses (native's chart) | Source |
|---|---|---|---|
| Father | 9 (always; not 4/10) | 10, 3 (marakas), badhaka from 9's sign; table: 8, 10, 3, 12 | R2; R6 p.254 |
| Mother | 4 | 5, 10 (marakas), badhaka by the 4th cusp sign; table: 3, 5, 10, 12 | R3 l.10117; R6 p.254 |
| Spouse | 7 | 8, 1 (marakas), badhaka by the 7th cusp sign; table: 1, 6, 8, 12 | R3; R4 p.86, 208; R6 p.254 |
| First child | 5 | 6, 11; table (children): 4, 6, 11, 12 | R3 p.145; R6 p.254 |
| 2nd / 3rd / 4th child | 7 / 9 / 11 | 2nd and 7th from that house + its badhaka | R2 (child order 5, 7, 9, 11) |
| 1st younger sibling | 3 | 4, 9 + badhaka from 3; recompute cusps with the 3rd cusp as their Asc (R3) | R3 l.9909 |
| Next younger siblings | 5, 7, 9 … | same pattern | R2 |
| Elder sibling | 11 | table: 5, 10, 12 | R6 p.254 |

- The period lords' **sub lords** decide: a planet signifying the relative's house whose sub lord is a badhaka/maraka of that house kills (R3 p.145–149).
- Spouse from the 7th cusp: its star and sub lords give the partner's longevity; the 7th cusp sub lord in a dual sign signifying the 7th's maraka/badhaka → wife dies first (R4 p.86). KSK's Indira Gandhi case: husband's death in the period of significators of 1, 6, 10 [KSK, magazines]. **DECIDE:** the R6 table (1, 6, 8, 12) vs the Indira case (1, 6, 10) — default: badhaka + maraka of the 7th computed per chart (this reproduces both).
- With several siblings or children, the one whose **birth RPs** match the evil period lords dies (R3 l.~9990).
- A parent's death shows in all the children's charts (MC_135, father's death in five sons' charts).
- The 10th is maraka to both parents (2nd from 9, 7th from 4): a promotion and a parent's death can coincide (R2; R3 p.192).
- Separation (not death) from a relative = their 12th: mother 3, 12; father 8, 12; spouse 6, 12; children 4, 12; elder brother 10, 12 (R6 p.254).

### 3.3 Health and disease — R3 l.~7620, l.12125–12930; R6 p.158
- Asc cusp in the star of lord 6 or 8 → low immunity; Asc sub lord in the star of a significator of 6 → sickly; Asc sub lord in the star of an occupant of 1 or 11 → good health.
- **Falls ill:** periods of significators of 6 that also signify 1 (+12 → hospital/bed).
- **Nature:** the 6th cusp sub lord → its star lord → that star lord's sign (body part) (R3 l.~12400). Saturn chronic; Mars acute/surgery; Mercury complications; Jupiter liver/tumour/sugar; Venus throat/kidney. Movable sign short; fixed chronic; dual → relapse (and a 6th sub lord in the star/sub of a planet in a dual sign → relapse).
- **Cure:** significators of 11 (sure if also of 5) following the 6th period; immediate only when the sub-sub of an 11th significator follows. For movable lagnas the 11th (badhaka) both cures and later kills [KSK].
- No cure from chronic disease: no planet in 11, none in the star of the owner/occupant of 11, and the 11th cusp and lord 11 in evil subs (R3).
- Eyes: 2 right, 12 left; the 12th sub lord in 6 and in the star of a 6/8/12 significator → defect. Speech: the 2nd cusp sub lord (Mercury talkative, Mars blunt, Saturn slow, nodes defect).
- Body-part and disease tables per sign/planet/sub (R3 l.~12390–12540; R3 249-sub table) → descriptive data.
- **Defect from birth:** the dasa/bhukti lords running at birth are significators of 6/8/12 [KSK, MC_059 hernia child]. Surgery timing: the cure significator (11) connected with Mars; Pisces = hospital.
- Chronic illness lasts while the dasa lords are in the stars of lords of 6/8/12. Recovery comes in the dasa of a planet in the star of the 11th occupant/lord, even if that planet is lord 6 itself [KSK, MC_060 "Health"].

### 3.4 Marriage and married life — R3 l.13078+; R4; R6
- Houses **2, 7, 11**. Promise: the 7th cusp sub lord signifies 2, 7 or 11 (R4 p.108). Denial: the 7th sub lord signifies 1, 6, 10 (12) — or is in the star of significators of 4, 6, 10 (R4 p.105).
- **DECIDE (blocking houses):** 1, 6, 10 (R4) vs 1, 6, 10, 12 (R3 p.430, R4 elsewhere). Default: 1, 6, 10 with 12 as an additional negative.
- Timing: fruitful significators of 2/7/11 (sub lord also a 2/7/11 significator; reject those in subs of 1/6/10 planets, R4 p.150). Saturn aspecting Venus or the Moon → delay (R3; magazines).
- **Spouse:** the spouse's birth star is ruled by the 7th sub lord (magazines). Partner's profession: significators of 4, 8, 12 (R4 p.85); career wife: the 4th sub lord signifying 4/8/12 (R4 p.98).
- KSK: marriage is judged from **2, 7, 11 only**, not 4/8/12, "like those who failed" (MC_060). The 2nd is for second marriage; the **11th also shows illegal intimacy** (MC_059 Seshadri case). The bio does not label an 11th-only connection as "intimacy" (**DECIDE**, default: not shown).
- **Second marriage:** the 7th sub lord (or its star lord) in a dual sign, or in the star of a dual-sign planet, or Mercury — **and** signifying 2 or 11 (R4 p.181; R6 p.165). The 2nd house = second spouse.
- **Disharmony / separation / divorce:** any planet whose sub lord signifies 6, 10 or 12 → dispute/separation in its periods (R4 p.69); divorce = 1, 6, 10 (R4 p.153). The partner leaves: 7th significator in the sub of a 6th significator; the native leaves: 12 (R3).
- **Love affair:** 5th sub lord and significators of 5; the lover married is the one whose birth RPs are significators of 2/7/11 (R4 p.171). The 2nd sub lord connected with 11 → extramarital (magazines).
- **Compatibility (two saved charts):** the boy's birth RPs are among the girl's 2/7/11 significators and vice versa; dasa/bhukti/antara lords of one = birth RPs of the other "a certainty" (R3 l.~18600; R4). Porutham and Mars dosha are "useless and meaningless" (R4 p.17–20) → not computed.

### 3.5 Children — R2; R3 l.~18412; R4 p.203–280
- Houses **2, 5, 11** (+ Jupiter as karaka). Promise: the 5th cusp sub lord signifies 2, 5 or 11 → children; signifies 1, 4, 10 → "can never have a child at all". For a male native judge the 11th cusp first [magazines].
- **Barren signs:** irrelevant in natal charts; the sub decides [KSK, MC_138] — vs R2's fruitful/barren list and the Horary p.204 pregnancy rule. **Decision:** not used in natal.
- Child order: 5, 7, 9, 11 (1st–4th child) (R2).
- Child birth timing: conjoined periods of fruitful significators of 2, 5, 11; the child's birth RPs = parents' running D/B/A lords "will never fail" (R3 l.~18600).
- Delivery / child health / infant death: significators of 6, 11 and badhaka → infant danger (R4 p.231+).
- **Sex of a child: no rule** — "if anyone declares that he can predict, he is a bluffer" (R2); KSK: "rules are not clear … I have not done any research" (magazines). **GAP** — not output. Number of children likewise: GAP (KSK: judge from the wife's chart, no exact rule).
- Adoption, santana thithi, beejam/kshetram: traditional → excluded.

### 3.6 Profession, service and business — R2; R3 l.~13860–16830; R6
| Matter | Houses / rule |
|---|---|
| Profession (nature) | 10th cusp sign lord + star lord + sub lord → R3 combination table; 10th sub lord's house signification (R3 l.~15340) |
| Employment / first job | 2, 6, 10 ("material trinity"); dasa running between ages 16–30 (R3) |
| Service vs business | 2nd cusp sub lord signifying 1, 2, 6, 10 (not 7) → service; 1, 7, 10 → business (R3) |
| Independent business | 2, 7, 10; 7th sub lord and significators of 7; Mars needed (R3 l.~15700) |
| Promotion | 2, 6, 10, 11; the 11th sub lord (and its star lord) direct and signifying 2/6/10/11 (R3; R6 p.287) |
| Transfer | **DECIDE:** 3, 10, 12 (R6) vs 3, 9, 12 connected with 6 or 10 (R3 p.375) vs 2, 5, 6, 9, 10 (+3) [contrib]. Default: 3, 9, 12 with 6 or 10 (R3, KSK's most detailed statement) |
| Change of job | 3, 5, 9 (R6) vs 3, 9, 12 (R3 l.~15080). **DECIDE**; default 3, 5, 9 |
| Suspension | 1, 5, 9 (12th from 2, 6, 10); 5 or 9 with 12 |
| Termination of service | 1, 5, 9, 12 |
| Retirement | 3, 5, 9 (R3 l.~16570) vs 1, 5, 9 (R3 l.~8680) vs 1, 5, 9, 12 [KSK magazine] vs 9, 12 [KSK, MC_060 "Extension of service"]. **DECIDE**; default 3, 5, 9 + 12 |
| Extension / re-employment | Retirement significator whose sub lord signifies 2/6/10 → retires and is re-appointed (MC_060) |
| Seniority | Same as competition: 1, 2, 3, 6, 10, 11 keep it; 4, 5, 7, 8, 9, 12 lose it to juniors (7th = juniors) [KSK, MC_060–061] |
| Transfer distance | 3 = short distance; 9 = long distance (MC contributor, confirmed case) |
| Pension | 2, 11 (+10); Saturn delays, never denies |
| Reinstatement | 10, 11; the 10th (or 6th) sub lord's star lord signifying 2/6/10 |
| Politics / election | 1, 6, 9, 10, 11 (R3 l.~16830); win 1, 2, 3, 6, 10, 11 vs lose 4, 5, 7, 8, 9, 12 |
| Actor | 5, 6, 10 (+11 prosperous) (R6 p.192) |
| Farming | Mars, Venus, Moon, Jupiter with 2, 6, 10 |
- **Profession houses DECIDE:** 2, 6, 10 (KSK, most cases) vs 2, 6, 10, 11 (R3; promotion). Default: 2, 6, 10 for the job itself, plus 11 for promotion and income growth.
- Nature of work (descriptive, KSK cases): Sun = government; Jupiter = finance; Mercury = accounts and inspection; Venus = assessment; Mars = authority, land (bhukaraka); Saturn = position of trust. The natural-zodiac sign number gives the field: 4th sign = land, 8th = waste/insurance/legacy, 12th = hospital (MC_056–060).
- Nature from the sub lord: within a house's significators, the sub lord's karaka picks the sub-topic, e.g. for the 4th, Moon sub = mother, Venus sub = vehicle, Mars sub = building [KSK, MC_058].
- Earning at all: the 10th sub lord retrograde → never (R6; horary rule — natal **DECIDE**, default not applied, §2.8).

### 3.7 Finance, debt, gains, losses — R3 l.~7720–9560
- Wealth: significators of 2, 6, 10, 11 in subs of significators of 2/6/11 (R3 five-level list). Most planets in the star/sub of lord 8 or 12 → losses.
- Receipt 2, 6, 10, 11; discharge of debts 4, 5, 8, 12; raising loans 6; repayment 8, 12.
- **Lottery:** the 3rd sub lord connected with 5, 6 or 11; the 11th cusp sub lord gives the promise (R5 p.224). **Speculation:** 5 with 6 and 11 → gain; 5 with 8 and 12 → loss.
- Arrears, legacy, insurance, bonus: 8 (with 6/11 → gain; with 12 → pays out). Treasure: Saturn + 4 with 8 and 11 [magazines].
- Money due from another person: 6 and 11, since the other person's loss is your gain [KSK, MC_059 commission case].
- Gifts: receiving 2, 3, 6, 11; giving 5, 8, 9, 12.
- **Who causes the loss** (12 combined with):
  - 3 & 6 → brother or neighbour, openly;
  - 3 & 12 → secretly;
  - 6 & 12 → servants;
  - 11 & 12 → friends turned approver;
  - 9 & 12 → father or a stranger;
  - 4 & 12 → someone in one's own house, street or town;
  - 7 & 12 → a business partner after severing ties.

  [KSK, MC_059 "Loss and litigation"] Loss through informers/theft: 12 combined with 3/6/11/9/4/7 (R6 p.313; MC).

### 3.8 Property and vehicles — R3 l.10232–11320; R6
- Buying a house: 4, 11, 12 (+6 or 9 for possession). Acquisition 2, 4, 11; **sale/disposal: 3, 5, 10**. The 4th sub lord decides whether one owns property; 4 + Mars land/buildings.
- Vehicle: 4 + Venus; the 4th sub lord in the star of a 4th significator and connected with Venus → will own one. Car purchase 4, 9, 10, 11 + Venus; sale **DECIDE**: 3, 4, 5, 10 (KSK 1967) vs 1, 3, 8, 10 (earlier note) — default 3, 4, 5, 10.
- Change of residence: 3 (12th to 4) with 9/12; the 4th sub lord decides the move (R6 p.305).
- Partition of property: 3, 9, 12 with 4 or 10.
- House sale variant: 3, 5, 8, 10 + Mars; vehicle sale 1, 3, 8, 10 + Venus [contrib Anjaneyulu, MC_055] — part of DECIDE #14.
- Luck of a place: a new house, seat or office is lucky or unlucky according to the periods that follow, not the place itself or its facing direction [KSK, MC_056]. The bio never attributes results to a place.

### 3.9 Education — R3 l.11329–11760
- 4 regular study; 9 higher study; 3 inclination; 11 success. Success: lords 4 and 9 in the sub of a significator of 11. Ends: significators of 3, 5, 8. Subject: R3 combination table (engineering, medicine, law …). Ph.D.: 4 and 9 with 11. Foreign study: 9 + 12 (overseas + study 6, 9, 11, 12).

### 3.10 Travel and foreign residence — R3 l.~13585; R6
- Overseas promise: the 12th cusp sub lord signifies 3, 9 or 12 (preferably 9); in the 8th bhava → cannot go. Timing: significators of 3, 9, 12. Settles abroad: + 2 and 11. Passport: 11th sub lord in the star of a significator of 3, 9, 11.
- Return home: **DECIDE** 3, 9, 11, 12 / 3, 9, 11 (R4 p.205) vs 3, 5, 6, 8, 11 [contrib] — default 3, 9, 11 (Reader 4).

### 3.11 Siblings — R3 l.9909–10117
- The 3rd cusp sub lord decides; plurality if it is in/with a dual sign. Co-borns promised: significator of 3 connected with 2 and 11. Danger to a brother: the 3rd sub lord signifies 8 or 10. Harmony: 3 with 11 and 1; enmity: 1 with 3, 6, 8.

### 3.12 Litigation, enemies, imprisonment
- Litigation/competition: 1, 2, 3, 6, 10, 11 win vs 4, 5, 7, 8, 9, 12 lose; the opponent's 11th = the 5th cusp (magazines; R3 l.~8700).
- **Imprisonment — DECIDE:** 2 and 12 (R3 l.~17527; KP Vol II quote) vs 3, 8, 12 (R3 l.~18215) vs 2, 3, 8, 12 with the 12th sub lord being **Rahu** (R6 p.313). Default: R6 (strictest, latest) as the promise test, and periods of significators of 2, 3, 8, 12 for timing. Release: 2, 11. House arrest 4, 8, 12.
- Friends and enemies: lord 11 in star/sub of significators of 1, 2, 3, 6, 10, 11 → helpful friends; 4, 5, 7, 8, 9, 12 → loss through friends (R3 l.~17140).
  - More detail [KSK, MC_058], for lord 11 in the star of:
    - lord 1 → sincere, permanent friend;
    - lord 10 → most helpful;
    - lord 7, 8 or 9 → time-serving;
    - lord 5 → you always lose;
    - lord 6 → the friend loses and you gain.
  - Compatibility with any person (saved charts): the other person's birth-star lord ruling your 1, 2, 3, 6, 10 or 11 → you gain; 4, 5, 7, 8, 9 or 12 → you lose.
- **Missing or absconding person** [KSK, MC_058; MC_059]:
  - Leaving home: 3, 9, 12. Return: 2, 11 (+4; 1 and 10 = rejoining the old place).
  - Child missing (5th), from the native's chart. Lord 5 in the star or sub of:
    - lord 10 → ill;
    - lord 12 → dead;
    - lord 1, 4 or 7 → gone out but alive.
  - Lord 5 connected with 11 → returns. Mars connected with 11 → police help.
- Imprisonment additions (MC_058): Mars + Saturn → for violence. Evil planet with 2 and 12 in a fixed sign → long term. Lord 8 strong and afflicted → dies in jail. Release: benefics in the star of significators of 2 and 11.

### 3.13 Mind, character, spiritual life
- Character: the sign of the star lord of the Asc sub lord (R3 l.~18690, descriptive table). Physical build: same sign (R3 l.~6900).
- Courage 3; depression 2; fear/dreams 12 [magazines].
- **Mood of each period** [KSK, MC_059 "Courage and confidence"]:
  - Houses 3 and 5 = bravery; 8 = fear.
  - A period lord in the star or sub of Mars or the Sun → confident; of Jupiter → buoyant; of Saturn → pessimistic; of Ketu → confused; of Rahu → per Rahu's own star and sub lords. Moon and Mercury are changeable, Venus easy-going.
  - Shown as descriptive text per window.
- Subjects of study (KSK cases): Sun, Virgo, Scorpio → medicine; Mars + Venus → botany, zoology, chemistry; Mars in a Mercury star → maths and chemistry; Venus + Mars + Mercury → music (MC_056; MC_059). Descriptive only. Truthfulness, spending: the 2nd and 12th sub lords (R3).
- Writing 3; speech 2; book completion 3, 11 + Mercury; publication + Jupiter.
- Spiritual: initiation 5, practice 10, progress 11 (R3 l.~17625); sanyasi: the Asc sub lord connected with 3, 10, 12 and Saturn (R6); siddhi: 11th sub lord in the star of a significator of 5 and 10.
- Negotiation/agreements 3, 9 (+11 success, +12 failure); engagement: 2, 7, 11 also signifying 3 and 9.

---

## 4. Timing — finding and ranking the top 3 windows

### 4.1 Rules from the texts
- Results of a house come only in the dasa/bhukti/antara of planets connected with it, and on days, stars and lagnas ruled by them (R2 l.~11830).
- Event = **conjoined period** of the planet, its star lord and its sub lord (R3 l.~3420). The dasa lord must signify the matter (dasa supremacy, §2.7). "A dasa, B bhukti, A antara give the result to the full extent" (R3).
- **Selection among significators:** the RPs at the moment of judgment pick the dasa/bhukti/antara (R3 l.~13400; R6). For a life bio the "moment of judgment" is when the user asks — **DECIDE**: the app computes RPs at the time the bio is generated and uses them only to break ties between equally strong windows (default), since the bio must not change from minute to minute.
- **Repeating events** (job change, transfer, travel, children, residence) recur whenever their significators' periods recur; birth and death happen once (R3 l.~16200).
- **Pinpointing within a window (R3 ch.2; R5 p.161–187):** sensitive points are every sign/star/sub permutation of the D, B, A lords; the event comes when one of them is transited by the D/B/A lords, the Sun or the Moon, or the **Ascendant at the native's current place of residence**. Order of fineness: Jupiter → year, Sun → month, Moon → day, Ascendant → hour [KSK; R5].
- Retrograde transits: retrograde in an evil sub aggravates; stationary = severest (R5 p.287).
- The transit point's sign, star and sub lords are the antara, bhukti and dasa lords in any order. Example: Sun at 21° Aries = Mars sign (antara), Venus star (bhukti), Jupiter sub (dasa) → cure date [KSK, MC_059]. The sub-sub level is also used (MC_056 marriage at 6:32 AM: lagna in the D/B/A/S lords' sign/star/sub/sub-sub).
- The day lord changes at **sunrise**: an event before sunrise belongs to the previous weekday (MC_055; MC_059).
- Customary avoidances (e.g. no Tuesday weddings in Madras) can shift a predicted date. The app ignores them; the user can (KSK, MC_059).
- **Undoing rule:** a result given in A–B can be undone in a later bhukti of a planet 6/8/12 from A and B (R5 p.257) → used to describe "loss of what was gained".

### 4.2 Scoring — APP CHOICE (not a KP rule; for your approval)
For each matter the engine walks every dasa–bhukti–antara of the native's life (birth to 100 years, or to the death window) and scores it:
1. **Gate:** the cusp-sub-lord promise for the matter must be positive (§3); if it is denied, the matter shows "denied" with the reason and no windows.
2. **Dasa, bhukti, antara lords** each scored by how strongly they signify the matter's houses: level 1 (star of occupant) = 6 points … level 6 (aspect) = 1 point; plus a bonus if their **sub lord** also signifies the houses (fruitful), and a penalty if it signifies the 12ths of the houses (§2.4).
3. The dasa lord must score > 0 (dasa supremacy); otherwise the window is dropped.
4. Ties broken by: (a) RPs at judgment time, (b) "A–B–A" full-extent pattern, (c) a matching Sun/Jupiter transit point in the window.
5. Top 3 non-overlapping windows are shown; each with dates, the lords, and a one-line reason ("Venus: occupant of 7, sub lord Jupiter signifies 11"). Past windows are marked PAST.
   - **Ranking covers the whole life, past and future together.** For a person born in the 1970s, a 1990s marriage window can rank #1 and is shown as "#1 most probable — PAST".
   - **One-time vs repeating events.** For one-time events (first marriage, death, birth of the first child), the #1 window is "the" predicted time. If it is past, the bio says the event most probably happened then. Later windows apply only if the chart also promises a repeat (e.g. second marriage per §3.4). For repeating events (job change, transfer, travel, residence), every strong window is listed, past and future.
   - **Actual events (optional user input).** The user can enter "married on 12-5-1996", etc.
     - The engine reports whether the real date fell in window #1, #2, #3 or none, which is a check on birth time and method.
     - The entered events feed rectification (§6.1 step 4).
     - Once a one-time event is confirmed, its future windows are shown only as "repeat, if promised".
6. Each window can be opened to see the transit-pinpointed dates within it (§4.1).

---

## 5. Horary (only as needed)
The bio is natal. Horary (1–249 numbers, R6) is used inside the app for one purpose: KSK's own practice of confirming a natal judgment with the RPs at the moment of the question. A full horary module is **not** planned unless you ask for it. Retrograde-denial rules (§2.8) are horary-only.

---

## 6. Birth-time rectification — R3 l.~21250–21720; R6 p.140–143

### 6.1 KP method (primary)
1. Take the RPs at the moment of judgment (day lord, Moon star lord, Moon sign lord, lagna sign lord, lagna star lord, with nodes representing their agents; reject RPs in the star of a retrograde planet).
2. The birth lagna's sign lord, star lord, sub lord (and sub-sub lord) must be among these RPs. The lagna lord at the moment of judgment = the sub-sub lord of the birth ascendant (R3 example).
3. Within the user's uncertainty range (e.g. ±2 hours) list every Asc sign/star/sub/sub-sub combination ruled by the RPs; compute when each rose → candidate times to the second.
4. If several candidates remain, confirm with past events: the candidate whose dasa windows match the user's known events (marriage date, children's births, parents' deaths, job) wins. "Multiple judgments are allowed" [KSK].
- Validation cases: R6-A (5:23:50 AM), R6-B (3:36:45 AM), R6-C (26-5-1913 6:10:14 PM, date unknown), R3-AS (war-time clock), R5-K (6:53 PM electricity).

### 6.2 Traditional checks (secondary, shown as information only)
- Vighati method (×4 ÷ 9 → birth-star group) — R3 used it as a confirmation; R6 p.141 rejects it as giving multiple answers. **DECIDE**; default: shown as information, not used to choose.
- Prenatal epoch — R3 shows it fails (30 minutes apart gives 2 minutes); KSK used it once as a cross-check (magazines). **Excluded.**

---

## 7. Excluded or flagged methods

| Method | Status | Source |
|---|---|---|
| Moon sign as lagna (when lagna "afflicted") | Excluded — "always the Lagna alone" | R3 l.~10725, l.~18680; early magazines used it |
| Yogas, raja yogas, Gajakesari etc. | Excluded — "fail" | R3 l.~7960, l.~19340 |
| Ashtakavarga | Excluded | magazines |
| Gochara from the Moon sign, sade-sati, ashtama sani, Guru bala, chandrashtama, vedha | Excluded | R3 l.~8740; R5 p.246–264 |
| Exaltation/debilitation as good/bad | Excluded (R6 "container/contents" magnitude only — **DECIDE**, default off) | R6 p.145 |
| Kendradhipatya dosha | Excluded from scoring | R3 p.456–461 |
| Shashtashtaka, dasa-sandhi | Excluded | R3; R4 p.261 |
| Porutham, Mars dosha | Excluded | R4 p.17–20 |
| Navamsa and other divisional charts | Excluded — twins disprove them | R3 profession chapter |
| Western aspects, progressions, transits with orbs | Excluded from scoring (aspects **DECIDE**, §2.2) | R5 p.25 |
| Uranus, Neptune | Descriptive only | R3 l.~15760 |
| Pars Fortuna | Descriptive only | R3; R5 |
| Varshphal (annual chart) | Excluded (KSK showed one once) | magazines |
| Prenatal epoch, Mandi/Gulika rectification | Excluded | R3 l.~21250 |
| Remedies, gems, shanti, homa | Not given. KSK 1963 said remedies help; later KSK: fate cannot be changed, prayer may mitigate. Gem by Asc/11th sub lord could be shown as information — **DECIDE**, default off | R3 p.258; R4 p.279; magazines |
| Sex of children, number of children | GAP — no rule | R2; magazines |
| Muhurta / "lucky time" tables | Out of scope for the bio (possible later feature) | R5 p.195–234 |
| Traditional muhurtha items (chandrashtama, Rahu kalam, inauspicious stars and tithis) | Excluded; KSK deliberately travelled against all of them (15-5-1970) with full success | MC_119 |
| Western progressions (secondary, lunar, solar), regressions, applying/separating orbs | Excluded (KSK listed progression in his 1967 method statement; Readers drop it) — part of DECIDE #2 | MC_055–061 (Bala series); MC_061 |
| Gnana Pradeepika, Prasna Marga (Aruda, Gulika, sphutas, sutras), Bhuvana Deepika navamsa timing, Uttarakalamrita annual dasa, Tajik | Excluded (traditional) | MC_055–060 |
| Omens (nimitta), star-day "rehearsal" heuristic | Excluded | MC_059 |
| Colour remedies, prayers, gems | Not given (KSK sometimes advised them; "astrologer predicts, cannot change fate") | MC_058–060 |
| Sex of child by masculine/feminine signs (Mani) | GAP stays — contributor guess, KSK says no rule | MC_059 |
| Pars Fortuna in KSK cases ("Fortune—from when") | Descriptive only | MC_057 |

---

## 8. Decisions you need to make (summary of every DECIDE)

**User policy (decided):** wherever the sources give two or more rules for the same thing, the app computes **every variant** and shows all of them side by side. Each result is labelled with its source (e.g. "Retirement — R3 houses 3, 5, 9: window A; KSK magazine houses 9, 12: window B"). The "default" column below now only decides which variant is listed first. This does not cover methods you have excluded outright (traditional and Western, §7); those stay off unless you switch them on.

| # | Question | Options | My default |
|---|---|---|---|
| 1 | Ayanamsa | KSK (Newcomb) / Lahiri | KSK, Lahiri as setting |
| 2 | Aspects in significator levels 5–6 and the dasa principle | conjunction only / Hindu aspects / Western degree aspects | conjunction + Hindu aspects for nodes |
| 3 | RP strength order | R6 / R3 / contributors | R6, used for ties only |
| 4 | Node agency order | conjoined→aspect→star→sign (KSK 1965, MC_120, MC_139) / star first (MC_123) | KSK order |
| 5 | Natal retrogression | ignore (KSK MC_139) / apply (R3 ministership case, contributors) | ignore in natal |
| 6 | Combustion | 8°30′ / other / not used | not used |
| 7 | Marriage blocking houses | 1, 6, 10 / 1, 6, 10, 12 | 1, 6, 10; 12 as extra negative |
| 8 | Spouse's death houses | R6 table 1, 6, 8, 12 / Indira case 1, 6, 10 | computed badhaka + maraka of 7th |
| 9 | Transfer | 3, 9, 12 + 6/10 / 3, 10, 12 / 2, 5, 6, 9, 10 | 3, 9, 12 + 6/10 |
| 10 | Change of job | 3, 5, 9 / 3, 9, 12 | 3, 5, 9 |
| 11 | Retirement | 3, 5, 9 / 1, 5, 9 / 1, 5, 9, 12 | 3, 5, 9 + 12 |
| 12 | Imprisonment | 2, 12 / 3, 8, 12 / 2, 3, 8, 12 + Rahu | R6 (2, 3, 8, 12 + Rahu) |
| 13 | Return from abroad | 3, 9, 11 / 3, 9, 11, 12 / 3, 5, 6, 8, 11 | 3, 9, 11 |
| 14 | Vehicle sale | 3, 4, 5, 10 / 1, 3, 8, 10 | 3, 4, 5, 10 |
| 15 | Suicide/murder indications | show / hide | show only within the mode-of-death text |
| 16 | Vighati rectification check | info / off | info |
| 17 | Gem by Asc/11th sub lord | info / off | off |
| 18 | Exaltation magnitude weight | on / off | off |
| 19 | RP moment for the bio | time of generation / none | time of generation, ties only |
| 20 | Scoring scheme (§4.2) | as proposed / changes | as proposed |
| 21 | Profession houses | 2, 6, 10 / 2, 6, 10, 11 | 2, 6, 10; +11 for promotion/income |
| 22 | "Planet in sub of lagna lord cannot kill"; subha kendradhipati as killer (Mani) | use / ignore | ignore |
| 23 | Mark 11th-only connection as "illegal intimacy" (KSK) | show / hide | hide |
| 24 | Significator level 1 = "star **or sub** of occupants" (Mani, other contributors) vs star only (KSK) | star only / star or sub | star only (sub used via §2.4 fruitfulness) |
| 25 | Horary numbers (if a horary module is added) | 1–108 (KSK) / 1–249 (R6, later) | 1–249, with 1–108 option |

Other contradictions already resolved by later KSK statements (no decision needed): lagna vs Moon sign (lagna only); barren signs (not in natal); sub discovery dates (sub 1947, full method 1951); remedies (no remedies); nodes never retrograde.

---

## 9. Gaps (the app will say "no rule in the sources")
- Sex of a child; exact number of children; number/sex of siblings (only "plural if dual sign").
- Disease tables for Jupiter, Venus and Saturn in signs (R3 says "similarly"; R5 p.241 partly fills them).
- MC_141's article continues on a "page 72" missing from the source files.
- Some printed birth data is OCR-damaged (see `?` entries in `docs/kp-test-cases.md`); those cases are used only for the parts that are legible.
- No rule for windows beyond death or for posthumous matters (not needed).

---

## 10. Validation test cases
- Readers: all rows in `docs/kp-test-cases.md` (R3-A … R6-C). Priority set for the first engine build:
  - Chart casting: R3-AN (ayanamsa 22°40′, full cusps), R4-H, R4-O (22°57′), R4-P (22°53′), R5-A (cusps + planets), R3-AT (sidereal times), R5 p.325 Saturn into Pisces 7-4-1966, sub table R5 p.164–170.
  - Dasa arithmetic: R5-C antara table; all printed dasa balances.
  - Events: R3-B (mother's death, marriage), R3-C (death 18-2-1970), R3-AQ (KSK's own service/retirement), R4-G, R4-I, R4-L (marriages), R4-R (wife's death), R4-S/T (divorce), R4-X (child), R4-Z/AA (childless — negative), R5-D (lottery), R5-L (father's death).
  - Rectification: R6-A, R6-B, R6-C, R3-AS, R5-K.
- Magazine cases from the redo pass are listed in `docs/kp-test-cases.md` (section "Magazines"). Others are under CONFIRMED in `docs/magazine-notes.md`, which also has these: Indira Gandhi multi-event chart; Yogananda's death; Bandaranaike's assassination; father's death across five sons' charts (MC_135); KSK aeroplane timing 4:39:20 PM; chart-casting procedure (MC_130); Agra 15-5-1963 worked cusps.
- Acceptance target (APP CHOICE): the engine reproduces printed cusps/planets within 5′, dasa dates within a few days, and ranks the actual event window in its top 3 for at least most of the event cases; every miss is listed for review rather than tuned away.

---

## 11. Next step
After you review this document (accept the defaults or change any DECIDE item), I build the app:
- Backend: FastAPI, Swiss Ephemeris, the engine above, SQLite with single-user login and saved charts.
- Frontend: React — chart entry, rectification wizard, the life bio (each matter: promise, description, top 3 windows with PAST marks), and the reasons behind every statement with citations.
