/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#2D5A27',
          600: '#1e3a1e',
          700: '#163016',
        },
        accent: {
          500: '#4A90E2',
          600: '#3b82d6',
        },
        success: {
          500: '#7CB342',
          600: '#689f35',
        },
        warning: {
          500: '#FFC107',
          600: '#e0a806',
        },
        danger: {
          500: '#E74C3C',
          600: '#d43f2f',
        },
        border: '#e2e8f0', // Neutral gray for borders
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}