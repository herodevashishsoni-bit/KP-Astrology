# KP Life Bio

A Krishnamurti Paddhati (KP) astrology app that reads a birth chart as a life bio. It follows only the rules in KP Readers 1–6 and the *Astrology & Athrishta* magazines (1963–1971).

For every life matter it shows:
- the **promise**, from the cusp sub lord;
- the **top 3 time windows** (dasa–bhukti–antara), with past windows marked PAST;
- every **source version** side by side, wherever the texts disagree.

It also has birth-time rectification, a horary module, and a single-user login with saved charts.

- Rules the engine implements: [`docs/kp-rules.md`](docs/kp-rules.md). Your decisions are in §8.
- Validation results: [`docs/validation.md`](docs/validation.md).
- Source notes: `docs/kp-rules-notes.md` (Readers) and `docs/magazine-notes.md` (magazines).

## Run

```bash
# backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000

# frontend (development, proxies /api to :8000)
cd frontend
npm install
npm run dev            # http://localhost:5173

# or build once and let the backend serve it
npm run build          # then open http://localhost:8000
```

The first visit asks you to create the single user account. Data is stored in `backend/kp.db` (SQLite). Set `KP_DB_URL` to use another database, and `KP_SECRET` to fix the login-token secret.

## Tests

```bash
cd backend
python -m pytest -q          # engine + API tests
python -m tests.validate     # confirmed-case report (KSK); add "Lahiri" for Lahiri
```

## Engine notes

- **Chart:** Swiss Ephemeris (Moshier; no data files needed). Tropical positions and Placidus cusps, then the ayanamsa subtracted, as KSK did with Raphael. Mean node.
- **Ayanamsa:** KSK, with Lahiri as a second full chart.
- **Aspects:** Western (R1/R2 aspect table and orbs) and Hindu full aspects.
- **Significators:** five levels plus node agency; exaltation only where the sources use it.
- **Windows:** ranked over the whole life. See `docs/validation.md` for how often the real event lands in the top 3.
