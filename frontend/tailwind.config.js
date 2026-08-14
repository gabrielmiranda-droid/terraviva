/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        field: {
          50: "#f7fbf3",
          100: "#e8f4dc",
          700: "#3f6f2a",
          800: "#2f531f",
          900: "#223c18"
        }
      }
    }
  },
  plugins: []
};
