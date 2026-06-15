/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        ivory: "var(--cc-ivory)",
        cream: "var(--cc-cream)",
        blush: "var(--cc-blush)",
        gold: "var(--cc-accent)",
        "gold-light": "var(--cc-accent-light)",
        brown: "var(--cc-brown)",
        "brown-mid": "var(--cc-brown-mid)",
        muted: "var(--cc-muted)",
      },
      fontFamily: {
        serif: ["var(--cc-font-serif)"],
        sans: ["var(--cc-font-sans)"],
      },
      backdropBlur: { xs: "4px" },
    },
  },
  plugins: [],
};
