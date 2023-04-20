/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../core/**/*.{html,js}',
  ],
  theme: {
    extend: {
      colors: {
        'base-dark': '#101728',
        'base-dark-light': '#0e1524',
        'base-blue': '#1f41bb',
        'base-purple': '#260e69',
        'base-red': '#ff3c5f',
        'base-light-purple': '#9340ff',

      },
    },
  },
  plugins: [

  ],
}
