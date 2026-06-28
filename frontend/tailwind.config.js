/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        antique: {
          gold: '#C9A96E',
          'gold-light': '#D4B97E',
          'gold-dark': '#B89A5E',
          wood: '#4A2C2A',
          'wood-light': '#5C3C3A',
          'wood-dark': '#3A1C1A',
          cream: '#F5E6D3',
          'cream-light': '#FAF3EB',
          'cream-dark': '#E8D5C0',
          bronze: '#CD7F32',
          'bronze-light': '#D4914A',
          'bronze-dark': '#B8702A',
          sepia: '#5C3A1E',
          'sepia-light': '#8B6238',
          'sepia-dark': '#3D2510',
          parchment: '#F4E8D1',
          ink: '#2C1810',
        },
      },
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'vintage': '0 4px 20px rgba(74, 44, 42, 0.15)',
        'vintage-lg': '0 8px 40px rgba(74, 44, 42, 0.2)',
        'golden': '0 0 20px rgba(201, 169, 110, 0.3)',
      },
      borderColor: {
        'antique': '#C9A96E',
      },
      backgroundImage: {
        'parchment': 'url("data:image/svg+xml,%3Csvg width=\'100\' height=\'100\' viewBox=\'0 0 100 100\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\' opacity=\'0.03\'/%3E%3C/svg%3E")',
      },
    },
  },
  plugins: [],
}
