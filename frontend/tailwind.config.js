/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Black & White Professional palette
        surface: {
          50:  '#FFFFFF',
          100: '#F5F5F5',
          200: '#E8E8E8',
          300: '#D0D0D0',
          400: '#A0A0A0',
          500: '#707070',
          600: '#505050',
          700: '#303030',
          800: '#1A1A1A',
          900: '#0D0D0D',
          950: '#000000',
        },
        accent: {
          cyan:    '#000000',   // remapped to black for B&W
          blue:    '#111111',
          amber:   '#555555',
          red:     '#222222',
          purple:  '#333333',
          emerald: '#444444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
