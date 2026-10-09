# Reading process — how to continue in a new session

Give this file to a new Claude Code session on repo `herodevashishsoni-bit/kp-astrology`, branch `claude/loving-mendel-bsogj3`, and say: "Follow docs/PROCESS.md."

## Goal of the project
Build a KP (Krishnamurti Paddhati) astrology web app (FastAPI + React). It works as a life "bio":
- It covers every life matter found in the texts, including death of the native and of family members, stated directly as the texts allow.
- Each matter shows its top 3 scored time windows; windows in the past are marked PAST.
- It includes birth-time rectification by ruling planets.
- It has single-user logins and saved charts.

Use ONLY rules from KP Readers 1–6 and the *Astrology & Athrishta* magazines 1963–1971. Flag contradictions, unclear points and traditional or Western methods; do not invent rules. The ephemeris will be decided after reading (leaning towards Swiss Ephemeris + KSK/Lahiri-type ayanamsa + Placidus, validated against the printed cases).

Order of work:
1. Read everything.
2. Write `docs/kp-rules.md` (per matter: rules, citations, gaps, contradictions, scoring) for user review.
3. Build the app.

## Files
| File | Purpose |
|---|---|
| `texts/extracted/*.txt` | Full extracted text of the 6 Readers and the magazines |
| `mc/MC_000` … `mc/MC_141` | Magazine text split into ~950-line chunks in chronological order; pages duplicating the Readers already removed (marked `[...N lines duplicate of Readers...]`) |
| `docs/kp-rules-notes.md` | Notes from Readers 1–6 (complete) |
| `docs/kp-test-cases.md` | Test cases from the Readers |
| `docs/magazine-notes.md` | Running notes on the magazines, one section per chunk |
| `docs/reading-log.md` | What has been read; last line says **Next to read** |
| `docs/PROCESS.md` | This file |

## Status
- Readers 1–6: read in full.
- Magazines: MC_000 to MC_119 read in full with detailed notes in magazine-notes.md (MC_000–010 notes are the "[detailed redo]" sections at the end of that file, after MC_078).
- Always trust the "Next to read" line in `docs/reading-log.md` over this file.

## Step-by-step process (repeat for each chunk)

### 1. Start of session (once)
- Read `docs/reading-log.md`.
- Read ALL of `docs/magazine-notes.md` and `docs/kp-rules-notes.md`, so you know every rule, contradiction, test case and CHECK prediction noted so far.

### 2. Read the chunk
- Use the Read tool on `mc/MC_0xx` with limit 800, then offset 801 for the rest.
- Read every line and skip nothing.

### 3. Append notes
Add a section `## MC_0xx (Month Year)` to `docs/magazine-notes.md`:
- Append with `cat >> docs/magazine-notes.md <<'EOF' ... EOF`.
- Do it after each 800-line part, so nothing is lost.

### 4. What to note (as detailed as the existing notes)
- **Every rule and every restatement**, with its nuance, and who stated it: KSK or a named contributor.
- **Contradictions** with earlier rules, said explicitly.
- **FLAG or REJECT** for traditional methods, which are rejected: yogas, ashtakavarga, gochara from Moon sign, Prasna Gyana or Shat Panchasika slokas, gemstones.
- **FLAG** for Western methods (aspects, progressions, Uranus/Neptune) and for early-period practices such as taking the Moon sign as lagna when the lagna is afflicted.
- **Every dated case**, with:
  - birth date, time and place (latitude/longitude)
  - cusps and planet degrees if given
  - dasa balance and periods
  - the significators used
  - event date and time, and the RPs at the event
  - whether it was CONFIRMED or is a prediction to CHECK
- **Outcomes of earlier CHECK predictions** if a later issue reports them.
- **Mundane or out-of-scope material:** one line only.

### 5. Every 5 chunks
- Add a line to `docs/reading-log.md` (e.g. `- MC_071–MC_075 (Aug–Oct 1967): read in full; notes in magazine-notes.md`).
- Replace its "Next to read" line.
- Commit and push:
  ```
  git add docs && git commit -m "Reading notes: magazines <months> (MC_0xx-0yy)" && git push -u origin claude/loving-mendel-bsogj3
  ```

### 6. Session length
After about 15–20 chunks, commit, push and stop. Start a new session with this file; fresh sessions are cheaper.

### 7. Do not
Do not build the app or write `docs/kp-rules.md` until all of MC_141 is read, unless the user asks.

## Key conventions already established
- **Placidus houses.** A house runs from its cusp to the next cusp. A house's lord is the lord of the sign the cusp falls in, even at 29°. An intercepted sign gives no lordship.
- **KSK ayanamsa** (Newcomb rate; e.g. 22°38' in 1919, 22°46' in 1929, ~23°18' in 1967). Mean node.
- **Significator order:**
  1. Planets in the star of occupants.
  2. Occupants.
  3. Planets in the star of lords.
  4. Lords.
  5. Planets conjoined with or aspected by these.
  - A node in a significator's sign, or conjoined with it, is stronger than that planet.
- **Star lord and sub lord.** The star lord gives the nature of the result (houses it occupies and owns). The sub lord decides favourable or unfavourable.
- **Ruling planets (RPs):** day lord, Moon star lord, Moon sign lord, lagna sign lord, lagna star lord, plus any node linked to them.
- **Horary number** 1–108 gives the ascendant (one 3°20' pada each).
