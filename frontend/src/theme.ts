/** Global visual tokens. This monochrome palette is the only permitted palette. */
export const theme = {
  colors: {
    background: '#000000',
    textPrimary: '#f5f5f5',
    textGlow: '#ffffff',
  },
  radius: '0px',
  shadows: {
    none: 'none',
    glow: '0 0 12px #ffffff, 0 0 24px #ffffff',
  },
  fonts: {
    headline: 'Dune Rise, League Spartan, Arial Black, sans-serif',
    body: 'DM Sans, sans-serif',
  },
} as const
