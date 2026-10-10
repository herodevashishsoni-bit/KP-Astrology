import React, { useEffect, useState } from 'react'
import { api } from './api.js'

function Promise({ p }) {
  if (!p) return null
  return (
    <div className="small">
      <b>Promise</b> — cusp {p.cusp} sub lord <b>{p.sub_lord}</b> (in {p.sub_lord_star}'s star):
      {p.variants.map((v) => (
        <div key={v.mode}>
          <span className={v.verdict === 'promised' ? 'good' : v.verdict === 'denied' ? 'bad' : 'warn'}>{v.verdict}</span>
          {' '}<span className="muted">— signifies {v.houses.join(', ')}; good {v.good.join(', ') || '—'}; against {v.bad.join(', ') || '—'} · {v.source}</span>
        </div>
      ))}
      <div className="muted">Retrograde (shown both ways): {p.retrograde_variant} · {p.retrograde_ignored_note}</div>
    </div>
  )
}

function Window({ w }) {
  return (
    <div className={'window' + (w.rank === 1 ? ' rank1' : '')}>
      <div>
        {w.rank ? <b>#{w.rank} </b> : null}
        <b>{w.lords.join(' – ')}</b> · {w.start} → {w.end} · age {w.age_at_start}
        {' '}<span className={'badge ' + w.status}>{w.status}</span>
        {' '}<span className="muted small">score {w.score}</span>
      </div>
      {w.magnitude && <div className="small warn">{w.magnitude}</div>}
      {w.pinpoint && w.pinpoint.length > 0 && (
        <div className="small">Dates within: {w.pinpoint.map((p) => <span key={p.date} title={p.rule}>{p.date} ({p.sun}) </span>)}</div>)}
      <details className="small muted"><summary>Why</summary><ul>{w.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul></details>
    </div>
  )
}

function Matter({ m }) {
  return (
    <div className="panel matter">
      <h3 style={{ margin: '0 0 4px' }}>{m.title} {m.one_time && <span className="badge muted">one-time</span>} {m.karaka && <span className="muted small">karaka {m.karaka}</span>}</h3>
      {m.span && <div className="small">Span of life — {m.span.rules.map((r, i) => <div key={i}><b>{r.band}</b>: {r.reason} <span className="muted">({r.source})</span></div>)}
        {!m.span.agree && <div className="warn">The two span rules disagree, so no window is pushed down for age.</div>}</div>}
      {m.variants.map((v, i) => (
        <div className="variant" key={i}>
          <div className="small"><b>Houses {v.houses.join(', ')}</b> <span className="muted">— {v.source}</span></div>
          {v.note && <div className="small muted">{v.note}</div>}
          <Promise p={v.promise} />
          {v.known_event_check && (
            <div className={'small ' + (v.known_event_check.in_top_3 ? 'good' : 'warn')}>
              Known event {v.known_event_check.date}: its window ranks #{v.known_event_check.rank_of_its_window ?? '—'}
              {v.known_event_check.in_top_3 ? ' (in the top 3)' : ' (not in the top 3)'}
            </div>)}
          {m.one_time && v.windows[0] && (
            <div className="small">Most probable: <b>{v.windows[0].lords.join(' – ')}</b>, {v.windows[0].start} → {v.windows[0].end}{' '}
              <span className={'badge ' + v.windows[0].status}>{v.windows[0].status}</span>
              {v.windows[0].status === 'PAST' && <span className="muted"> — the event most probably happened then. Later windows apply only if the chart promises a repeat.</span>}</div>)}
          {v.windows.map((w) => <Window key={w.rank} w={w} />)}
          {v.other_strong_windows && v.other_strong_windows.length > 0 && (
            <details className="small"><summary>Other strong windows in time order ({v.other_strong_windows.length})</summary>
              {v.other_strong_windows.map((w, i) => <Window key={i} w={w} />)}</details>)}
        </div>
      ))}
    </div>
  )
}

export default function Bio({ id }) {
  const [aya, setAya] = useState('KSK')
  const [aspects, setAspects] = useState(true)
  const [data, setData] = useState({})
  const [err, setErr] = useState('')
  const [group, setGroup] = useState('All')
  useEffect(() => {
    setErr('')
    const key = aya + aspects
    if (data[key]) return
    api.bio(id, aya, aspects).then((d) => setData((x) => ({ ...x, [key]: d }))).catch((e) => setErr(e.message))
  }, [id, aya, aspects])
  const d = data[aya + aspects]
  const groups = d ? ['All', ...new Set(d.matters.map((m) => m.group))] : []
  return (
    <div>
      <div className="row" style={{ alignItems: 'center', marginBottom: 10 }}>
        <div style={{ flex: 'none' }} className="tabs">
          {['KSK', 'Lahiri'].map((a) => <button key={a} className={aya === a ? 'on' : ''} onClick={() => setAya(a)}>{a} ayanamsa</button>)}
        </div>
        <label style={{ flex: 'none', margin: 0 }}><input type="checkbox" style={{ width: 'auto' }} checked={aspects} onChange={(e) => setAspects(e.target.checked)} /> Western + Hindu aspects</label>
        <select style={{ flex: 'none', width: 200 }} value={group} onChange={(e) => setGroup(e.target.value)}>
          {groups.map((g) => <option key={g}>{g}</option>)}</select>
      </div>
      <p className="small muted">
        Windows are dasa–bhukti–antara periods over the whole life, past and future, ranked by significator strength (kp-rules §4.2).
        Where the sources disagree, every version is shown with its source. In tests on confirmed cases the actual event was in the top 3
        windows only some of the time (see docs/validation.md). Treat the windows as candidates, and enter known events to check the chart.
      </p>
      {err && <div className="error">{err}</div>}
      {!d && !err && <p>Computing…</p>}
      {d && d.ruling_planets_now && <p className="small muted">Ruling planets now (tie-break only): {d.ruling_planets_now.ruling_planets.join(', ')}</p>}
      {d && d.matters.filter((m) => group === 'All' || m.group === group).map((m) => <Matter key={m.key} m={m} />)}
    </div>
  )
}
