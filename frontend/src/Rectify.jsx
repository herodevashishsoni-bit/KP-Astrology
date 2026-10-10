import React, { useEffect, useState } from 'react'
import { api } from './api.js'

export default function Rectify() {
  const [f, setF] = useState({ date: '', time_from: '', time_to: '', tz: 'Asia/Kolkata', lat: '', lon: '', judge_lat: '', judge_lon: '', reject_retro: true })
  const [events, setEvents] = useState([])
  const [matters, setMatters] = useState([])
  const [res, setRes] = useState(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { api.matters().then(setMatters) }, [])
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })
  const run = async () => {
    setErr(''); setBusy(true); setRes(null)
    try {
      const ev = Object.fromEntries(events.filter((e) => e.date).map((e) => [e.key, e.date]))
      setRes(await api.rectify({ ...f, lat: +f.lat, lon: +f.lon, judge_lat: f.judge_lat ? +f.judge_lat : null, judge_lon: f.judge_lon ? +f.judge_lon : null, events: ev }))
    } catch (e) { setErr(e.message) }
    setBusy(false)
  }
  return (
    <div className="wrap">
      <h2>Birth-time rectification (KP ruling planets)</h2>
      <p className="small muted">Method (R3; R6 p.140–143; MC_058): the ruling planets are taken now, at your current place. The birth Ascendant's sign, star and sub lords must all be ruling planets. Every stretch of your time range that fits is a candidate. Known events then rank the candidates.</p>
      <div className="panel">
        <div className="row">
          <div><label>Birth date</label><input type="date" value={f.date} onChange={set('date')} /></div>
          <div><label>Earliest possible time</label><input type="time" value={f.time_from} onChange={set('time_from')} /></div>
          <div><label>Latest possible time (max 6 h range)</label><input type="time" value={f.time_to} onChange={set('time_to')} /></div>
          <div><label>Time zone</label><input value={f.tz} onChange={set('tz')} /></div>
        </div>
        <div className="row">
          <div><label>Birth latitude</label><input value={f.lat} onChange={set('lat')} /></div>
          <div><label>Birth longitude</label><input value={f.lon} onChange={set('lon')} /></div>
          <div><label>Your latitude now (judgment)</label><input value={f.judge_lat} onChange={set('judge_lat')} placeholder="same as birth" /></div>
          <div><label>Your longitude now</label><input value={f.judge_lon} onChange={set('judge_lon')} placeholder="same as birth" /></div>
        </div>
        <label><input type="checkbox" style={{ width: 'auto' }} checked={f.reject_retro} onChange={set('reject_retro')} /> Drop a ruling planet that is in the star of a retrograde planet (R6). KSK did not drop one in MC_058; untick to compare.</label>
        <h4>Known events (optional)</h4>
        {events.map((e, i) => (
          <div className="row" key={i}>
            <div><select value={e.key} onChange={(x) => setEvents(events.map((y, j) => j === i ? { ...y, key: x.target.value } : y))}>
              {matters.map((m) => <option key={m.key} value={m.key}>{m.title}</option>)}</select></div>
            <div><input type="date" value={e.date} onChange={(x) => setEvents(events.map((y, j) => j === i ? { ...y, date: x.target.value } : y))} /></div>
            <div style={{ flex: 'none' }}><button onClick={() => setEvents(events.filter((_, j) => j !== i))}>×</button></div>
          </div>))}
        <p className="row" style={{ maxWidth: 360 }}>
          <button onClick={() => setEvents([...events, { key: 'marriage', date: '' }])}>Add event</button>
          <button className="primary" disabled={busy || !f.date || !f.time_from || !f.time_to} onClick={run}>{busy ? 'Working…' : 'Find birth time'}</button>
        </p>
        {err && <div className="error">{err}</div>}
      </div>
      {res && (
        <div className="panel">
          <p>Ruling planets now: <b>{res.ruling_planets.join(', ')}</b> <span className="muted small">(with nodes' agents: {res.allowed_with_nodes.join(', ')})</span></p>
          {res.candidates.length === 0 && <p className="warn">No part of the range fits the ruling planets. Widen the range, or try again later (KSK: "multiple judgments are allowed").</p>}
          <div className="scroll"><table><thead><tr><th>Candidate (UTC)</th><th>Ascendant</th><th>Sign</th><th>Star</th><th>Sub</th><th>Sub-sub</th><th>RP score</th><th>Event fit</th></tr></thead><tbody>
            {res.candidates.slice(0, 25).map((c, i) => (
              <tr key={i}><td>{c.start_utc.slice(0, 19)} – {c.end_utc.slice(11, 19)}</td><td>{c.asc}</td><td>{c.sign_lord}</td><td>{c.star_lord}</td><td>{c.sub_lord}</td><td>{c.subsub_lord}</td>
                <td>{c.rp_score}<div className="small muted">{c.notes.join('; ')}</div></td>
                <td>{c.event_fit ? <>{c.event_fit.fit}<div className="small muted">{c.event_fit.events.map((e) => `${e.matter} #${e.rank ?? '—'}`).join(', ')}</div></> : '—'}</td></tr>))}
          </tbody></table></div>
          <p className="small muted">Times are UTC. Add your zone offset to get local time.</p>
        </div>)}
    </div>
  )
}
