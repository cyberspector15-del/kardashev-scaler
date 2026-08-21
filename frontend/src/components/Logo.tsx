import { useId } from 'react'

type LogoProps = {
  /** Width in CSS pixels; the logo keeps its reference aspect ratio. */
  size?: number | string
  className?: string
  title?: string
  /** Percentage of the first bar that is illuminated (0–100). */
  fillPercent?: number
}

/** The Kardashev Scaler mark: three rising energy bars on a luminous baseline. */
export function Logo({ size = 240, className, title = 'Kardashev Scaler', fillPercent = 73 }: LogoProps) {
  const glowId = useId().replace(/:/g, '')
  const safeFillPercent = Math.max(0, Math.min(100, fillPercent))
  const fillHeight = 80 * (safeFillPercent / 100)
  const fillY = 208 - fillHeight
  return (
    <svg
      aria-label={title}
      className={className}
      fill="none"
      height="auto"
      role="img"
      style={{ width: size }}
      viewBox="0 0 220 224"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>{title}</title>
      <defs>
        <filter id={glowId} x="-30%" y="-20%" width="160%" height="150%">
          <feGaussianBlur result="blur" stdDeviation="2.5" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g filter={`url(#${glowId})`} stroke="#ffffff" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3">
        <path d="M15 208H205" />
        <rect height="80" rx="22" width="44" x="28" y="128" />
        <rect height="104" rx="22" width="44" x="88" y="104" />
        <rect height="160" rx="22" width="44" x="148" y="48" />
      </g>

      {fillHeight > 0 && (
        <rect fill="#ffffff" height={fillHeight} rx={Math.min(22, fillHeight / 2)} width="44" x="29.5" y={fillY} />
      )}
    </svg>
  )
}
