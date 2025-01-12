/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // For create-react-app
    // OR
    "./app/**/*.{js,jsx,ts,tsx}", // For Next.js
    "./pages/**/*.{js,jsx,ts,tsx}", // For Next.js
    "./components/**/*.{js,jsx,ts,tsx}", // For Next.js
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
