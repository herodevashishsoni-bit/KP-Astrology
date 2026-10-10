import React, { useEffect, useState } from 'react'
import { api } from './api.js'

const S = { Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me', Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke' }

function One({ d }) {
  const c = d.chart
  return (
    <div>
      <p className="small">Ayanamsa {c.ayanamsa_name} {c.ayanamsa_dms} · sidereal time {c.sidereal_time_hours.toFixed(4)} h ·
        balance {d.dasa_balance.lord} {d.dasa_balance.years}y {d.dasa_balance.months}m {d.dasa_balance.days}d
        {d.current_period && <> · now <b>{d.current_period.lords.join('–')}</b></>}</p>
      <h4>Cusps</h4>
      <div className="scroll"><table><thead><tr><th>#</th><th>Cusp</th><th>Sign</th><th>Star</th><th>Sub</th><th>S-sub</th></tr></thead><tbody>
        {c.cusps.map((x) => <tr key={x.house}><td>{x.house}</td><td>{x.dms}</td><td>{S[x.sign_lord]}</td><td>{S[x.star_lord]} <span className="muted small">{x.star_name}</span></td><td><b>{S[x.sub_lord]}</b></td><td>{S[x.subsub_lord]}</td></tr>)}
      </tbody></table></div>
      <h4>Planets</h4>
      <div className="scroll"><table><thead><tr><th>Planet</th><th>Position</th><th>House</th><th>Sign</th><th>Star</th><th>Sub</th><th></th></tr></thead><tbody>
        {c.planets.map((p) => <tr key={p.name}><td>{p.name}</td><td>{p.dms}</td><td>{p.house}</td><td>{S[p.sign_lord]}</td><td>{S[p.star_lord]} <span className="muted small">{p.star_name}</span></td><td>{S[p.sub_lord]}</td>
          <td className="small">{p.retro ? 'R ' : ''}{p.dignity || ''}</td></tr>)}
      </tbody></table></div>
    </div>
  )
}

export default function ChartView({ id }) {
  const [d, setD] = useState({})
  const [err, setErr] = useState('')
  useEffect(() => {
    Promise.all([api.chart(id, 'KSK'), api.chart(id, 'Lahiri')])
      .then(([k, l]) => setD({ KSK: k, Lahiri: l })).catch((e) => setErr(e.message))
  }, [id])
  if (err) return <div className="error">{err}</div>
  if (!d.KSK) return <p>Computing…</p>
  const k = d.KSK
  return (
    <div>
      <div className="grid2">
        <div className="panel"><h3 style={{ marginTop: 0 }}>KSK ayanamsa</h3><One d={d.KSK} /></div>
        <div className="panel"><h3 style={{ marginTop: 0 }}>Lahiri ayanamsa</h3><One d={d.Lahiri} /></div>
      </div>
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Planet → star lord → sub lord (KSK)</h3>
        <div className="scroll"><table><thead><tr><th>Planet</th><th>Occ.</th><th>Owns</th><th>Star lord</th><th>its occ./owns</th><th>Sub lord</th><th>its occ./owns</th><th>Signifies (levels 1–4)</th><th>Node acts for</th></tr></thead><tbody>
          {k.significators.map((r) => <tr key={r.planet}><td>{r.planet}</td><td>{r.occupies}</td><td>{r.owns.join(', ')}</td>
            <td>{r.star_lord}</td><td>{r.star_lord_occupies} / {r.star_lord_owns.join(', ')}</td>
            <td>{r.sub_lord}</td><td>{r.sub_lord_occupies} / {r.sub_lord_owns.join(', ')}</td>
            <td><b>{r.signifies.join(', ')}</b></td><td className="small">{r.node_agents.join(', ')}</td></tr>)}
        </tbody></table></div>
      </div>
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Significators of each house (KSK) — strongest first</h3>
        <p className="small muted">Levels: 1 in the star of an occupant · 2 occupant · 3 in the star of the lord · 4 lord · 5 conjoined · 6 aspected. Nodes rank half a level above the planet they act for.</p>
        <div className="scroll"><table><tbody>
          {k.houses.map((h) => <tr key={h.house}><td><b>{h.house}</b></td><td className="chips">
            {h.significators.map((s) => <span key={s.planet} title={s.reason}>{s.planet} {s.level}</span>)}</td></tr>)}
        </tbody></table></div>
      </div>
      <div className="grid2">
        <div className="panel"><h3 style={{ marginTop: 0 }}>Dasas (KSK)</h3>
          <table><tbody>{k.dasas.map((p, i) => <tr key={i}><td>{p.lords[0]}</td><td>{p.start.slice(0, 10)}</td><td>{p.end.slice(0, 10)}</td></tr>)}</tbody></table></div>
        <div className="panel"><h3 style={{ marginTop: 0 }}>Gems (remedy — enabled)</h3>
          {k.gems.suggestions.map((g, i) => <p key={i} className="small"><b>{g.gem}</b> ({g.planet}) — <span className={g.usable ? 'good' : 'bad'}>{g.usable ? 'usable' : 'not usable'}</span>: {g.reason}<br /><span className="muted">{g.rule}</span></p>)}
          <p className="small muted">{k.gems.note}</p>
          <h4>Vighati check (information only)</h4>
          <p className="small">{k.vighati.vighatis_since_sunrise} vighatis since sunrise → remainder {k.vighati.remainder} → {k.vighati.star_group_lord} star group; Moon's star lord {k.vighati.moon_star_lord} —
            <span className={k.vighati.agrees ? 'good' : 'warn'}> {k.vighati.agrees ? 'agrees' : 'differs'}</span>. <span className="muted">{k.vighati.status}</span></p>
        </div>
      </div>
      <div className="panel"><h3 style={{ marginTop: 0 }}>Aspects (KSK chart)</h3>
        <div className="scroll"><table><thead><tr><th>From</th><th>To</th><th>System</th><th>Aspect</th><th>Quality</th><th>Orb</th></tr></thead><tbody>
          {k.aspects.map((a, i) => <tr key={i}><td>{a.from}</td><td>{a.to}</td><td>{a.system}</td><td>{a.aspect}</td><td>{a.quality}</td><td>{a.orb}</td></tr>)}
        </tbody></table></div></div>
    </div>
  )
}
