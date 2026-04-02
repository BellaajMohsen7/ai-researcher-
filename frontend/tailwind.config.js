/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core Synthesis Palette
        background: '#0a0e14',
        surface: '#0a0e14',
        
        // Depth Layers
        'surface-container-low': '#0f141a',
        'surface-container': '#151a21',
        'surface-container-high': '#1b2028',
        'surface-container-highest': '#20262f',
        
        // Data streams
        primary: '#49f4c8',
        'primary-container': '#00d4aa',
        secondary: '#58a6ff',
        'secondary-container': '#0060aa',
        tertiary: '#c79eff',
        'tertiary-container': '#bc8cff',
        
        // Typography & States
        'on-surface': '#f1f3fc',
        'on-surface-variant': '#a8abb3',
        'outline-variant': '#44484f',
      },
      fontFamily: {
        headline: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #49f4c8 0%, #00d4aa 100%)',
      },
      boxShadow: {
        'ambient': '0px 0px 32px 0px rgba(73, 244, 200, 0.08)',
      }
    },
  },
  plugins: [],
}
