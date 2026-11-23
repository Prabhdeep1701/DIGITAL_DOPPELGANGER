import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          DEFAULT: '#F5F0E8',
          light: '#FAF7F2',
          dark: '#EDE8DC',
          border: '#E0D8CC',
        },
        forest: {
          DEFAULT: '#2D5A3D',
          light: '#4A7C5C',
          lighter: '#A8C5B5',
          dark: '#1B3A28',
          darker: '#1B2B23',
          muted: '#3D6B50',
        },
        warm: {
          text: '#1A1A1A',
          secondary: '#6B6B5E',
          muted: '#8A8A7A',
          border: '#D4CFC5',
        },
        accent: {
          red: '#C4432B',
          amber: '#B87333',
          gold: '#8B6914',
        },
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
export default config
