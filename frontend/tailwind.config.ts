import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    borderRadius: {
      none: '0px',
    },
    boxShadow: {
      none: 'none',
      glow: '0 0 12px #ffffff, 0 0 24px #ffffff',
    },
    extend: {
      colors: {
        background: '#000000',
        'text-primary': '#f5f5f5',
        'text-glow': '#ffffff',
      },
      fontFamily: {
        headline: ['Dune Rise', 'League Spartan', 'Arial Black', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
