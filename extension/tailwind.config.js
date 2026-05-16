/** @type {import('tailwindcss').Config} */
export default {
  content: ["./*.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "#d8dee8",
        surface: "#f6f7f9",
        ink: "#172033",
        muted: "#667085",
        primary: "#2251d1"
      }
    }
  },
  plugins: []
};
