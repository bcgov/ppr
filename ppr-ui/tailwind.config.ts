/** @type {import('tailwindcss').Config} */
export default {
  content: [],
  theme: {
    extend: {
      colors: {
        bcGovColor: {
          darkBlue: '#003366',
          ltBlue: '#e2e8ee'
        },
        // used color generator recommended by tailwind docs: https://uicolors.app/create
        bcGovGray: {
          50: '#f8f9fa',
          100: '#f1f3f5',
          200: '#e9ecef',
          300: '#dee2e6',
          400: '#ced4da',
          500: '#adb5bd',
          600: '#868e96',
          700: '#495057',
          800: '#343a40',
          900: '#212529',
          950: '#232529'
        },
        blue: {
          50: '#e4edf7',
          100: '#e0e7ed',
          150: '#b3c2d1',
          200: '#8099b3',
          300: '#4d7094',
          350: '#38598a',
          400: '#26527d',
          500: '#1669bb',
          600: '#125192',
          700: '#002e5e',
          800: '#002753',
          900: '#002049',
          950: '#001438'
        },
        red: {
          50: '#fef2f2',
          100: '#fde3e4',
          200: '#fdcbcc',
          300: '#faa7a9',
          400: '#f57478',
          500: '#eb484d',
          600: '#d3272c',
          700: '#b52024',
          800: '#961e21',
          900: '#7d1f22',
          950: '#440b0d'
        },
        yellow: {
          50: '#fffbeb',
          100: '#fef2c7',
          200: '#fee589',
          300: '#fdd14c',
          400: '#fcba19',
          500: '#f69b0a',
          600: '#da7505',
          700: '#b55108',
          800: '#933e0d',
          900: '#79340e',
          950: '#451903'
        },
        green: {
          700: '#2e7d32'
        }
      }
    }
  },
  plugins: []
}
