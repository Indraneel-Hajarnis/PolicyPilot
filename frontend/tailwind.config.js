/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#eef2ff',
          100: '#dde5ff',
          200: '#c3cfff',
          300: '#99abff',
          400: '#6b7dff',
          500: '#4a54ff',
          600: '#3730f5',
          700: '#2d22d8',
          800: '#261daf',
          900: '#1a1562',
          950: '#0c0a3b',
        },
        teal: {
          50: '#effefb',
          100: '#c8fff4',
          200: '#91fee9',
          300: '#52f5da',
          400: '#1ee0c5',
          500: '#06c4ac',
          600: '#029e8e',
          700: '#067e73',
          800: '#0a645d',
          900: '#0d524d',
          950: '#003331',
        },
        amber: {
          50: '#fffbeb',
          100: '#fff3c6',
          200: '#ffe588',
          300: '#ffd24a',
          400: '#ffbe20',
          500: '#f99b07',
          600: '#dd7302',
          700: '#b74f06',
          800: '#943d0c',
          900: '#7a330d',
          950: '#461902',
        },
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          700: '#1e293b',
          800: '#0f172a',
          900: '#0a0f1f',
          950: '#050810',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(30, 224, 197, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(30, 224, 197, 0.4)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
