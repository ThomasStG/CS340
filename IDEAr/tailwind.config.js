/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {
      screens: {
        mobile: "700px",
      },
    },
  },
  plugins: [],
};
