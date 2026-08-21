import { Link } from 'react-router-dom'
import { Logo } from '../components/Logo'

export function Home() {
  return (
    <main className="home-screen">
      <section className="home-centerpiece" aria-label="Kardashev Scaler">
        <Logo className="home-logo" size="min(60vw, 420px)" />
        <h1>Kardashev Scaler</h1>
        <Link className="outline-button" to="/dashboard">Enter</Link>
      </section>
    </main>
  )
}
