import React, { useEffect, useState } from 'react'
import { api } from './api.js'

export default function Horary() {
  const [matters, setMatters] = useState([])
  const [f, setF] = useState({ matter_key: 'marriage', number: '', scheme: 249, lat: '', lon: '', ayanamsa: 'KSK', years_ahead: 5 })
  const [res, setRes] = useState(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { api.matters().then(setMatters) }, [])
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const run = async () => {
    setErr(''); setBusy(true); setRes(null)
    try {
      setRes(await api.horary({ ...f, number: f.number ? +f.number : null, scheme: +f.scheme, lat: +f.lat, lon: +f.lon, years_ahead: +f.years_ahead }))
    } catch (e) { setErr(e.message) }
    setBusy(false)
  }
  return (
    <div className="wrap">
      <h2>Horary question</h2>
      <p className="small muted">Think of the question and give a number from 1–249 (R6) or 1–108 (KSK magazines). Leave the number empty to use the moment of asking. The planets are taken for now, at the place you are now.</p>
      <div className="panel">
        <div className="row">
          <div><label>Question about</label><select value={f.matter_key} onChange={set('matter_key')}>
            {matters.map((m) => <option key={m.key} value={m.key}>{m.group} — {m.title}</option>)}</select></div>
          <div><label>Number</label><input value={f.number} onChange={set('number')} placeholder="empty = time of question" /></div>
          <div><label>Scheme</label><select value={f.scheme} onChange={set('scheme')}><option value="249">1–249 (R6)</option><option value="108">1–108 (magazines)</option></select></div>
          <div><label>Ayanamsa</label><select value={f.ayanamsa} onChange={set('ayanamsa')}><option>KSK</option><option>Lahiri</option></select></div>
        </div>
        <div className="row">
          <div><label>Your latitude now</label><input value={f.lat} onChange={set('lat')} /></div>
          <div><label>Your longitude now</label><input value={f.lon} onChange={set('lon')} /></div>
          <div><label>Look ahead (years)</label><input value={f.years_ahead} onChange={set('years_ahead')} /></div>
          <div style={{ flex: 'none' }}><button className="primary" disabled={busy || !f.lat || !f.lon} onClick={run}>{busy ? 'Working…' : 'Judge'}</button></div>
        </div>
        {err && <div className="error">{err}</div>}
      </div>
      {res && (
        <div className="panel">
          <p><b>{res.matter}</b> · {res.chart_info.method} {res.chart_info.division && `(${res.chart_info.division})`} · Ascendant {res.chart_info.asc}</p>
          <p className="small">Ruling planets: <b>{res.ruling_planets.ruling_planets.join(', ')}</b>
            {res.ruling_planets.rejected_retro_star.length > 0 && <span className="muted"> (dropped, in the star of a retrograde planet: {res.ruling_planets.rejected_retro_star.join(', ')})</span>}</p>
          <p className="small">Moon (shows the question): house {res.moon.moon_house}, star lord {res.moon.star_lord} (signifies {res.moon.star_lord_signifies.join(', ')}), sub lord {res.moon.sub_lord} (signifies {res.moon.sub_lord_signifies.join(', ')})</p>
          {res.variants.map((v, i) => (
            <div className="variant" key={i}>
              <div className="small"><b>Houses {v.houses.join(', ')}</b> <span className="muted">— {v.source}</span></div>
              {v.promise && <div className="small">Cusp {v.promise.cusp} sub lord <b>{v.promise.sub_lord}</b>: {v.promise.variants.map((x) => <span key={x.mode} className={x.verdict === 'promised' ? 'good' : x.verdict === 'denied' ? 'bad' : 'warn'}>{x.verdict} ({x.mode}) </span>)}
                <div className="muted">{v.promise.retrograde_variant}</div></div>}
              {v.windows.map((w, j) => (
                <div className={'window' + (j === 0 ? ' rank1' : '')} key={j}>
                  <b>#{j + 1} {w.lords.join(' – ')}</b> · {w.start} → {w.end} <span className="muted small">score {w.score}{w.rp_lords.length > 0 && ` · RPs among lords: ${w.rp_lords.join(', ')}`}</span>
                  {w.pinpoint.length > 0 && <div className="small">Dates: {w.pinpoint.map((p) => `${p.date} (${p.sun})`).join(' · ')}</div>}
                </div>))}
            </div>))}
          <p className="small muted">{res.retrograde_rules}</p>
        </div>)}
    </div>
  )
}
