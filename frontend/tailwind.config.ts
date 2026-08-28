import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--bg-dark)',
        foreground: 'var(--text-primary)',
        panel: 'var(--bg-panel)',
      },
    },
  },
  plugins: [],
}
export default config
