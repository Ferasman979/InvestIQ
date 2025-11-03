import * as React from "react";
import clsx from "clsx";


type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "ghost" };


export function Button({ className, variant = "default", ...props }: Props) {
return (
<button
className={clsx(
"inline-flex items-center justify-center rounded-xl text-sm font-medium px-3 py-2 transition",
variant === "default" && "bg-primary/90 hover:bg-primary",
variant === "ghost" && "bg-transparent hover:bg-white/5",
className
)}
{...props}
/>
);
}