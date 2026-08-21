type LogoProps = {
  /** Width in CSS pixels; the logo keeps its reference aspect ratio. */
  size?: number | string
  className?: string
  title?: string
}

/** The Kardashev Scaler mark: three rising energy bars on a luminous baseline. */
export function Logo({ size = 240, className, title = 'Kardashev Scaler' }: LogoProps) {
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
        <filter id="white-glow" x="-30%" y="-20%" width="160%" height="150%">
          <feGaussianBlur result="blur" stdDeviation="2.5" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g filter="url(#white-glow)" stroke="#ffffff" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3">
        <path d="M15 208H205" />
        <rect height="80" rx="22" width="44" x="28" y="128" />
        <rect height="104" rx="22" width="44" x="88" y="104" />
        <rect height="160" rx="22" width="44" x="148" y="48" />
      </g>

      <path d="M29.5 150C29.5 137.85 39.35 128 51.5 128C63.65 128 73.5 137.85 73.5 150V186C73.5 198.15 63.65 208 51.5 208C39.35 208 29.5 198.15 29.5 186V150Z" fill="#ffffff" />
    </svg>
  )
}
