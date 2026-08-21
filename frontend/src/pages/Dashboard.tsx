import { FormEvent, type ReactNode, useEffect, useState } from 'react'
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
type UsageResult = { captured_kwh: number; consumed_kwh: number; waste_kwh: number; deficit_kwh: number; waste_pct: number; flagged_windows: { window: string; waste_kwh: number }[] }
type AbsorptionResult = { zones: { lat: number; lng: number; avg_irradiance: number; panel_density_assumed: number; potential_score: number }[]; top_recommendation: { lat: number; lng: number; potential_score: number } | null }
type DistributionResult = { allocations: { residential_kwh: number; industrial_kwh: number; agricultural_kwh: number }; shortfalls: { sector: string; shortfall_kwh: number }[] }
type RecommendationResult = { recommendations: { priority: 'high' | 'medium' | 'low'; action: string; reason: string }[] }

const navItems = ['Overview', 'Tracker Control', 'Kardashev Progress', 'Usage Intelligence', 'Absorption Optimization', 'Distribution Logic', 'Recommendation Engine']

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
  const [consumed, setConsumed] = useState('4')
  const [usage, setUsage] = useState<UsageResult | null>(null)
  const [absorption, setAbsorption] = useState<AbsorptionResult | null>(null)
  const [distribution, setDistribution] = useState<DistributionResult | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendationResult | null>(null)
  const [moduleError, setModuleError] = useState('')
  const [isModuleLoading, setIsModuleLoading] = useState(false)

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

  const runModule = async <T,>(path: string, payload: object, setResult: (result: T) => void) => {
    setIsModuleLoading(true); setModuleError('')
    try { setResult(await request<T>(path, payload)) }
    catch (error) { setModuleError(error instanceof Error ? error.message : 'This module is unavailable.') }
    finally { setIsModuleLoading(false) }
  }
  const runUsage = () => void runModule<UsageResult>('/api/usage/analyze', { captured_kwh: comparison?.tracked_output_kwh ?? 0, consumed_kwh: Number(consumed) }, setUsage)
  const runAbsorption = () => void runModule<AbsorptionResult>('/api/absorption/zones', { center_lat: Number(latitude), center_lng: Number(longitude), radius_km: 10, grid_size: 3 }, setAbsorption)
  const runDistribution = () => void runModule<DistributionResult>('/api/distribution/model', { total_captured_kwh: comparison?.tracked_output_kwh ?? 0, demand_breakdown: { residential_pct: 40, industrial_pct: 40, agricultural_pct: 20 } }, setDistribution)
  const runRecommendations = () => void runModule<RecommendationResult>('/api/recommendations/generate', { usage, absorption, distribution }, setRecommendations)

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
        {view === 'Usage Intelligence' ? <ModulePanel title="Usage Intelligence" eyebrow="Captured versus consumed" loading={isModuleLoading} error={moduleError} action="Analyze usage" onAction={runUsage}>
          <label>Consumed kWh<input type="number" min="0" step=".1" value={consumed} onChange={(event) => setConsumed(event.target.value)} /></label>
          {usage && <><div className="module-stat-grid"><Stat label="Captured" value={`${usage.captured_kwh.toFixed(2)} kWh`} /><Stat label="Consumed" value={`${usage.consumed_kwh.toFixed(2)} kWh`} /><Stat label="Waste" value={`${usage.waste_kwh.toFixed(2)} kWh`} /><Stat label="Deficit" value={`${usage.deficit_kwh.toFixed(2)} kWh`} /></div><p className="estimate-label">Waste: {usage.waste_pct.toFixed(2)}%</p><WindowList windows={usage.flagged_windows} /></>}</ModulePanel>
        : view === 'Absorption Optimization' ? <ModulePanel title="Absorption Optimization" eyebrow="NASA POWER potential grid" loading={isModuleLoading} error={moduleError} action="Rank zones" onAction={runAbsorption}>
          {absorption && <ZoneTable zones={absorption.zones} />}</ModulePanel>
        : view === 'Distribution Logic' ? <ModulePanel title="Distribution Logic" eyebrow="40% residential · 40% industrial · 20% agricultural" loading={isModuleLoading} error={moduleError} action="Model allocation" onAction={runDistribution}>
          {distribution && <><div className="allocation-list">{Object.entries(distribution.allocations).map(([sector, value]) => <OutputBar key={sector} label={sector.replace('_kwh', '')} value={value} width={Math.min(100, value)} glow />)}</div><Shortfalls items={distribution.shortfalls} /></>}</ModulePanel>
        : view === 'Recommendation Engine' ? <ModulePanel title="Recommendation Engine" eyebrow="Explainable rule set" loading={isModuleLoading} error={moduleError} action="Generate recommendations" onAction={runRecommendations}>
          {recommendations && <RecommendationList items={recommendations.recommendations} />}</ModulePanel>
        : (
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

function ModulePanel({ title, eyebrow, loading, error, action, onAction, children }: { title: string; eyebrow: string; loading: boolean; error: string; action: string; onAction: () => void; children: ReactNode }) {
  return <section className="module-page"><span className="eyebrow">{eyebrow}</span><h2>{title}</h2><div className="module-action"><button className="outline-button" disabled={loading} onClick={onAction}>{loading ? 'Processing' : action}</button></div>{loading && <div className="skeleton module-skeleton" />}{error && <Failure message={error} retry={onAction} />}{children}</section>
}
function WindowList({ windows }: { windows: UsageResult['flagged_windows'] }) { return <div className="data-list"><span className="eyebrow">Highest waste windows</span>{windows.length ? windows.map((item) => <p key={item.window}><b>{item.window}</b><span>{item.waste_kwh.toFixed(3)} kWh</span></p>) : <p>No surplus windows flagged.</p>}</div> }
function ZoneTable({ zones }: { zones: AbsorptionResult['zones'] }) { return <div className="data-list zone-list">{zones.map((zone) => <p key={`${zone.lat}-${zone.lng}`}><b>{zone.lat}, {zone.lng}</b><span>Score {zone.potential_score.toFixed(2)} · GHI {zone.avg_irradiance.toFixed(2)}</span></p>)}</div> }
function Shortfalls({ items }: { items: DistributionResult['shortfalls'] }) { return <div className="data-list"><span className="eyebrow">Shortfalls</span>{items.length ? items.map((item) => <p key={item.sector}><b>{item.sector}</b><span>{item.shortfall_kwh.toFixed(2)} kWh</span></p>) : <p>No baseline shortfalls.</p>}</div> }
function RecommendationList({ items }: { items: RecommendationResult['recommendations'] }) { return <div className="recommendations">{items.map((item, index) => <article className={`recommendation ${item.priority}`} key={`${item.action}-${index}`}><span>{item.priority}</span><h3>{item.action}</h3><p>{item.reason}</p></article>)}</div> }
