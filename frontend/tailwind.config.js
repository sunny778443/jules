/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          blue: "#00f0ff",
          dark: "#0a0a16",
          darker: "#05050b",
          border: "#1e1e38",
          neon: "#ff007f",
          glow: "#00ffd2",
        }
      }
    },
  },
  plugins: [],
}
