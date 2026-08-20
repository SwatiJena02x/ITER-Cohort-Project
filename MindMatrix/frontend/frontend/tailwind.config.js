/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],

  theme: {
    extend: {
      colors: {
        'board-bg': '#FAFAF7',
        'board-panel': '#FFFFFF',
        'board-grid': '#E7E4D8',
        'board-ink': '#1C2321',
        'board-faint': '#6B7268',

        marker: {
          blue: '#2B4FE0',
          green: '#1E8E5A',
          red: '#D63B3B',
          amber: '#DE9A1F',
        },
      },

      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        hand: ['"Caveat"', 'cursive'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },

      backgroundImage: {
        'grid-board':
          'linear-gradient(#E7E4D8 1px, transparent 1px), linear-gradient(90deg, #E7E4D8 1px, transparent 1px)',
      },

      backgroundSize: {
        grid: '28px 28px',
      },

      boxShadow: {
        board:
          '0 1px 0 rgba(28,35,33,0.04), 0 8px 24px -12px rgba(28,35,33,0.18)',
      },
    },
  },

  plugins: [],
}