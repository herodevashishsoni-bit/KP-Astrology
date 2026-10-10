import React, { useEffect, useState } from 'react'
import { api, hasToken, setToken } from './api.js'
import ChartView from './ChartView.jsx'
import Bio from './Bio.jsx'
import Rectify from './Rectify.jsx'
import Horary from './Horary.jsx'

function Login({ onDone }) {
  const [hasUser, setHasUser] = useState(null)
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')
  useEffect(() => { api.status().then((s) => setHasUser(s.has_user)).catch((e) => setErr(e.message)) }, [])
  const submit = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const r = hasUser ? await api.login(u, p) : await api.setup(u, p)
      setToken(r.token); onDone()
    } catch (e) { setErr(e.message) }
  }
  if (hasUser === null) return <div className="center">Loading…{err && <div className="error">{err}</div>}</div>
  return (
    <form className="center panel" onSubmit={submit}>
      <h2>{hasUser ? 'Log in' : 'Create your account'}</h2>
      {!hasUser && <p className="muted small">This app has a single user. The first account created is the only one.</p>}
      <label>Username</label><input value={u} onChange={(e) => setU(e.target.value)} autoFocus />
      <label>Password (6+ characters)</label><input type="password" value={p} onChange={(e) => setP(e.target.value)} />
      {err && <div className="error">{err}</div>}
      <p><button className="primary" type="submit">{hasUser ? 'Log in' : 'Create account'}</button></p>
    </form>
  )
}

const empty = { name: '', birth_local: '', tz: 'Asia/Kolkata', lat: '', lon: '', place: '', notes: '' }

export function ChartForm({ initial, onSave, onCancel }) {
  const [f, setF] = useState(initial || empty)
  const [err, setErr] = useState('')
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const save = async (e) => {
    e.preventDefault(); setErr('')
    try { await onSave({ ...f, lat: parseFloat(f.lat), lon: parseFloat(f.lon), birth_local: f.birth_local.length === 16 ? f.birth_local + ':00' : f.birth_local }) }
    catch (e) { setErr(e.message) }
  }
  return (
    <form className="panel" onSubmit={save}>
      <div className="row">
        <div><label>Name</label><input value={f.name} onChange={set('name')} required /></div>
        <div><label>Birth date and clock time (local)</label>
          <input type="datetime-local" step="1" value={f.birth_local} onChange={set('birth_local')} required /></div>
      </div>
      <div className="row">
        <div><label>Time zone — IANA name (handles India war time 1942–45) or offset like +05:30</label>
          <input value={f.tz} onChange={set('tz')} required /></div>
        <div><label>Place (label only)</label><input value={f.place} onChange={set('place')} /></div>
      </div>
      <div className="row">
        <div><label>Latitude (N +, S −)</label><input value={f.lat} onChange={set('lat')} required /></div>
        <div><label>Longitude (E +, W −)</label><input value={f.lon} onChange={set('lon')} required /></div>
      </div>
      <label>Notes</label><textarea rows="2" value={f.notes} onChange={set('notes')} />
      {err && <div className="error">{err}</div>}
      <p className="row" style={{ maxWidth: 300 }}>
        <button className="primary" type="submit">Save</button>
        {onCancel && <button type="button" onClick={onCancel}>Cancel</button>}
      </p>
    </form>
  )
}

function ChartList({ onOpen }) {
  const [charts, setCharts] = useState([])
  const [adding, setAdding] = useState(false)
  const [err, setErr] = useState('')
  const load = () => api.charts().then(setCharts).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  return (
    <div className="wrap">
      <div className="row" style={{ alignItems: 'center' }}>
        <h2 style={{ flex: 'none' }}>Saved charts</h2>
        <div style={{ flex: 'none' }}><button className="primary" onClick={() => setAdding(true)}>New chart</button></div>
      </div>
      {err && <div className="error">{err}</div>}
      {adding && <ChartForm onCancel={() => setAdding(false)} onSave={async (c) => { const r = await api.createChart(c); setAdding(false); onOpen(r.id) }} />}
      <div className="panel">
        {charts.length === 0 && <p className="muted">No charts yet.</p>}
        <div className="scroll"><table><tbody>
          {charts.map((c) => (
            <tr key={c.id}>
              <td><button className="link" onClick={() => onOpen(c.id)}>{c.name}</button></td>
              <td>{c.birth_local.replace('T', ' ')}</td><td>{c.tz}</td><td>{c.place}</td>
              <td className="small muted">{c.events.length} known events</td>
              <td><button onClick={async () => { if (confirm(`Delete ${c.name}?`)) { await api.deleteChart(c.id); load() } }}>Delete</button></td>
            </tr>
          ))}
        </tbody></table></div>
      </div>
    </div>
  )
}

function ChartPage({ id, onBack }) {
  const [rec, setRec] = useState(null)
  const [tab, setTab] = useState('bio')
  const [editing, setEditing] = useState(false)
  const load = () => api.charts().then((cs) => setRec(cs.find((c) => c.id === id)))
  useEffect(() => { load() }, [id])
  if (!rec) return <div className="wrap">Loading…</div>
  return (
    <div className="wrap">
      <p><button className="link" onClick={onBack}>← All charts</button></p>
      <h2 style={{ marginTop: 0 }}>{rec.name} <span className="muted small">{rec.birth_local.replace('T', ' ')} · {rec.tz} · {rec.lat}, {rec.lon} {rec.place && '· ' + rec.place}</span>
        {' '}<button className="link small" onClick={() => setEditing(!editing)}>edit</button></h2>
      {editing && <ChartForm initial={rec} onCancel={() => setEditing(false)} onSave={async (c) => { await api.updateChart(id, c); setEditing(false); load() }} />}
      <div className="tabs">
        {[['bio', 'Life bio'], ['chart', 'Chart & significators'], ['events', 'Known events']].map(([k, t]) => (
          <button key={k} className={tab === k ? 'on' : ''} onClick={() => setTab(k)}>{t}</button>))}
      </div>
      {tab === 'bio' && <Bio id={id} key={JSON.stringify(rec.events) + rec.birth_local} />}
      {tab === 'chart' && <ChartView id={id} key={rec.birth_local + rec.tz} />}
      {tab === 'events' && <Events rec={rec} onChange={load} />}
    </div>
  )
}

function Events({ rec, onChange }) {
  const [matters, setMatters] = useState([])
  const [m, setM] = useState('marriage')
  const [d, setD] = useState('')
  const [note, setNote] = useState('')
  const [err, setErr] = useState('')
  useEffect(() => { api.matters().then(setMatters) }, [])
  const title = (k) => (matters.find((x) => x.key === k) || {}).title || k
  return (
    <div className="panel">
      <p className="muted small">Enter events that already happened. The bio then reports where each real date ranks among the predicted windows. This checks the birth time and the method, and the dates also help rectification.</p>
      <div className="row">
        <div><label>Matter</label><select value={m} onChange={(e) => setM(e.target.value)}>
          {matters.map((x) => <option key={x.key} value={x.key}>{x.group} — {x.title}</option>)}</select></div>
        <div><label>Date</label><input type="date" value={d} onChange={(e) => setD(e.target.value)} /></div>
        <div><label>Note</label><input value={note} onChange={(e) => setNote(e.target.value)} /></div>
        <div style={{ flex: 'none' }}><button className="primary" disabled={!d} onClick={async () => {
          try { await api.addEvent(rec.id, { matter_key: m, date: d, note }); setD(''); setNote(''); onChange() } catch (e) { setErr(e.message) } }}>Add</button></div>
      </div>
      {err && <div className="error">{err}</div>}
      <table style={{ marginTop: 10 }}><tbody>
        {rec.events.map((e) => (
          <tr key={e.id}><td>{title(e.matter_key)}</td><td>{e.date}</td><td>{e.note}</td>
            <td><button onClick={async () => { await api.deleteEvent(rec.id, e.id); onChange() }}>Remove</button></td></tr>))}
      </tbody></table>
    </div>
  )
}

export default function App() {
  const [logged, setLogged] = useState(hasToken())
  const [view, setView] = useState({ page: 'list' })
  useEffect(() => {
    const h = () => setLogged(false)
    window.addEventListener('kp-logout', h)
    return () => window.removeEventListener('kp-logout', h)
  }, [])
  if (!logged) return <Login onDone={() => setLogged(true)} />
  return (
    <>
      <div className="topbar">
        <h1>KP Life Bio</h1>
        <button className="link" onClick={() => setView({ page: 'list' })}>Charts</button>
        <button className="link" onClick={() => setView({ page: 'rectify' })}>Rectification</button>
        <button className="link" onClick={() => setView({ page: 'horary' })}>Horary</button>
        <button className="link" onClick={() => { setToken(''); setLogged(false) }}>Log out</button>
      </div>
      {view.page === 'list' && <ChartList onOpen={(id) => setView({ page: 'chart', id })} />}
      {view.page === 'chart' && <ChartPage id={view.id} onBack={() => setView({ page: 'list' })} />}
      {view.page === 'rectify' && <Rectify />}
      {view.page === 'horary' && <Horary />}
    </>
  )
}
