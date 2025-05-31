/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        'hc-text': '#000000',
        'hc-bg': '#FFFFFF',
        'hc-link': '#0000EE',
        'hc-visited': '#551A8B',
        'hc-focus': '#FF0000',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'none': 'none',
      },
      transitionProperty: {
        'none': 'none',
      },
    },
  },
  plugins: [],
  variants: {
    extend: {
      backgroundColor: ['dark', 'high-contrast'],
      textColor: ['dark', 'high-contrast'],
      borderColor: ['dark', 'high-contrast'],
      ringColor: ['dark', 'high-contrast'],
    },
  },
};

