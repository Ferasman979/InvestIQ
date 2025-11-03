import clsx from "clsx";


export function Badge({ children, color }: { children: React.ReactNode; color?: "green" | "yellow" | "red" | "blue" }) {
const map = {
green: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
yellow: "bg-yellow-500/15 text-yellow-300 border-yellow-500/20",
red: "bg-red-500/15 text-red-300 border-red-500/20",
blue: "bg-blue-500/15 text-blue-300 border-blue-500/20",
} as const;
return (
<span className={clsx("border px-2 py-0.5 rounded-lg text-xs", map[color ?? "blue"]) }>{children}</span>
);
}