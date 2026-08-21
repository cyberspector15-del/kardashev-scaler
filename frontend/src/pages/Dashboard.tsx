import { FormEvent, useEffect, useState } from 'react'
import { Logo } from '../components/Logo'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

type Comparison = {
  fixed_output_kwh: number
  tracked_output_kwh: number
  efficiency_gain_pct: number
  session_id: string | null
}

type SunPosition = {
  solar_azimuth: number
  solar_elevation: number
  optimal_panel_tilt_angle: number
}

type KardashevProgress = {
  earth_kardashev_value: number
  session_efficiency_gain_pct: number
  projected_k_shift: number
  projection: { label: string; projected_kardashev_value: number }
}

const navItems = ['Overview', 'Tracker Control', 'Kardashev Progress', 'Usage Intelligence', 'Absorption Optimization', 'Distribution Logic', 'Recommendation Engine']
const futureViews = new Set(navItems.slice(3))

function isoDate(offsetDays = 0) {
  const day = new Date()
  day.setDate(day.getDate() + offsetDays)
  return day.toISOString().slice(0, 10)
}

async function request<T>(path: string, body: object): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(payload.detail ?? 'The request could not be completed.')
  return payload as T
}

export function Dashboard() {
  const [view, setView] = useState('Overview')
  const [latitude, setLatitude] = useState('28.6139')
  const [longitude, setLongitude] = useState('77.2090')
  const [startDate, setStartDate] = useState(isoDate(-7))
  const [endDate, setEndDate] = useState(isoDate(-1))
  const [area, setArea] = useState('2')
  const [efficiency, setEfficiency] = useState('22')
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [progress, setProgress] = useState<KardashevProgress | null>(null)
  const [sun, setSun] = useState<SunPosition | null>(null)
  const [comparisonError, setComparisonError] = useState('')
  const [progressError, setProgressError] = useState('')
  const [sunError, setSunError] = useState('')
  const [isComparing, setIsComparing] = useState(false)
  const [isLoadingProgress, setIsLoadingProgress] = useState(false)
  const [isLoadingSun, setIsLoadingSun] = useState(false)

  const getSunPosition = async () => {
    setIsLoadingSun(true); setSunError('')
    try {
      setSun(await request<SunPosition>('/api/tracker/sun-position', {
        latitude: Number(latitude), longitude: Number(longitude), timestamp: new Date().toISOString(),
      }))
    } catch (error) { setSunError(error instanceof Error ? error.message : 'Sun position is unavailable.') }
    finally { setIsLoadingSun(false) }
  }

  useEffect(() => {
    void getSunPosition()
    const timer = window.setInterval(() => void getSunPosition(), 60_000)
    return () => window.clearInterval(timer)
  // Refresh intentionally follows the current location fields every minute.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latitude, longitude])

  const runComparison = async (event?: FormEvent) => {
    event?.preventDefault(); setIsComparing(true); setComparisonError(''); setProgress(null); setProgressError('')
    try {
      const result = await request<Comparison>('/api/tracker/compare', {
        latitude: Number(latitude), longitude: Number(longitude), start_date: startDate, end_date: endDate,
        panel_specs: { area_m2: Number(area), efficiency_pct: Number(efficiency) },
      })
      setComparison(result)
      if (result.session_id) await getProgress(result.session_id)
      else setProgressError('Comparison complete. Configure Supabase to persist a session and unlock the global projection.')
    } catch (error) { setComparisonError(error instanceof Error ? error.message : 'Comparison is unavailable.') }
    finally { setIsComparing(false) }
  }

  const getProgress = async (sessionId: string) => {
    setIsLoadingProgress(true); setProgressError('')
    try { setProgress(await request<KardashevProgress>('/api/tracker/kardashev-score', { session_id: sessionId })) }
    catch (error) { setProgressError(error instanceof Error ? error.message : 'Global projection is unavailable.') }
    finally { setIsLoadingProgress(false) }
  }

  const maxOutput = comparison ? Math.max(comparison.fixed_output_kwh, comparison.tracked_output_kwh, 0.0001) : 1
  const earthFill = progress ? progress.earth_kardashev_value * 100 : 73

  return (
    <main className="dashboard-shell" aria-label="Kardashev Scaler dashboard">
      <aside className="sidebar">
        <div className="sidebar-mark"><Logo size={38} /></div>
        <nav aria-label="Dashboard sections">
          {navItems.map((item, index) => (
            <button className={`nav-item ${view === item ? 'active' : ''}`} key={item} onClick={() => setView(item)}>
              <span aria-hidden="true">{index < 3 ? '◈' : '○'}</span><span>{item}</span>
            </button>
          ))}
        </nav>
      </aside>
      <section className="dashboard-workspace">
        <header className="topbar">
          <div><span className="eyebrow">Kardashev Scaler</span><h1>{view}</h1></div>
          <div className="location-fields" aria-label="Tracker location">
            <label>Lat<input value={latitude} inputMode="decimal" onChange={(event) => setLatitude(event.target.value)} /></label>
            <label>Lng<input value={longitude} inputMode="decimal" onChange={(event) => setLongitude(event.target.value)} /></label>
          </div>
        </header>
        {futureViews.has(view) ? (
          <section className="coming-soon"><span>Phase 4</span><h2>{view}</h2><p>Coming in Phase 4</p></section>
        ) : (
          <div className="dashboard-grid">
            <section className="panel comparison-panel">
              <div className="panel-heading"><span className="eyebrow">Tracker Control</span><h2>Panel comparison</h2></div>
              <form className="comparison-form" onSubmit={runComparison}>
                <label>Start<input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label>
                <label>End<input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label>
                <label>Area m²<input min="0.1" step="0.1" type="number" value={area} onChange={(event) => setArea(event.target.value)} /></label>
                <label>Efficiency %<input min="1" max="100" step="0.1" type="number" value={efficiency} onChange={(event) => setEfficiency(event.target.value)} /></label>
                <button className="outline-button" disabled={isComparing}>{isComparing ? 'Calculating' : 'Run comparison'}</button>
              </form>
              {isComparing && <div className="skeleton comparison-skeleton" />}
              {comparisonError && <Failure message={comparisonError} retry={() => void runComparison()} />}
              {comparison && !isComparing && <>
                <div className="gain-stat"><span>Efficiency gain</span><strong>+{comparison.efficiency_gain_pct.toFixed(2)}%</strong></div>
                <div className="bar-comparison">
                  <OutputBar label="Fixed tilt" value={comparison.fixed_output_kwh} width={(comparison.fixed_output_kwh / maxOutput) * 100} />
                  <OutputBar label="Sun tracking" value={comparison.tracked_output_kwh} width={(comparison.tracked_output_kwh / maxOutput) * 100} glow />
                </div>
              </>}
            </section>
            <section className="panel progress-panel">
              <div className="panel-heading"><span className="eyebrow">Kardashev Progress</span><h2>Earth-scale measure</h2></div>
              {isLoadingProgress && <div className="skeleton logo-skeleton" />}
              {!isLoadingProgress && <div className="progress-content">
                <Logo fillPercent={earthFill} size={170} />
                <div><span className="eyebrow">Earth Kardashev value</span><strong className="k-value">{progress ? progress.earth_kardashev_value.toFixed(6) : '—'}</strong></div>
              </div>}
              {progress && <div className="support-stats"><span>Session gain <b>+{progress.session_efficiency_gain_pct.toFixed(2)}%</b></span><span>Projected K shift <b>+{progress.projected_k_shift.toFixed(6)}</b></span></div>}
              {progress && <p className="estimate-label">{progress.projection.label}</p>}
              {progressError && <Failure message={progressError} retry={comparison?.session_id ? () => getProgress(comparison.session_id!) : undefined} />}
            </section>
            <section className="panel sun-panel">
              <div className="panel-heading"><span className="eyebrow">Live tracker</span><h2>Sun position</h2><span className="refresh-note">60s refresh</span></div>
              {isLoadingSun && !sun && <div className="skeleton sun-skeleton" />}
              {sun && <div className="sun-stats"><Stat label="Azimuth" value={`${sun.solar_azimuth.toFixed(1)}°`} /><Stat label="Elevation" value={`${sun.solar_elevation.toFixed(1)}°`} /><Stat label="Optimal tilt" value={`${sun.optimal_panel_tilt_angle.toFixed(1)}°`} /></div>}
              {sunError && <Failure message={sunError} retry={getSunPosition} />}
            </section>
          </div>
        )}
      </section>
    </main>
  )
}

function OutputBar({ label, value, width, glow = false }: { label: string; value: number; width: number; glow?: boolean }) {
  return <div className="output-row"><div><span>{label}</span><b>{value.toFixed(3)} kWh</b></div><div className="output-track"><i className={glow ? 'glow-bar' : ''} style={{ width: `${width}%` }} /></div></div>
}

function Stat({ label, value }: { label: string; value: string }) { return <div><span>{label}</span><strong>{value}</strong></div> }

function Failure({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="failure"><p>{message}</p>{retry && <button className="text-button" onClick={() => void retry()}>Retry</button>}</div>
}
