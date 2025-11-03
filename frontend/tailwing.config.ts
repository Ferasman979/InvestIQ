import type { Config } from "tailwindcss";


const config: Config = {
content: [
"./app/**/*.{ts,tsx}",
"./components/**/*.{ts,tsx}",
],
theme: {
extend: {
colors: {
background: "#0a0b0e",
card: "#0f1115",
border: "#1a1d23",
muted: "#7e8695",
primary: "#4f46e5"
},
borderRadius: {
xl: "1rem",
'2xl': "1.25rem"
}
},
},
plugins: [],
};
export default config;