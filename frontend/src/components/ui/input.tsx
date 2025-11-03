import * as React from "react";
import clsx from "clsx";


type Props = React.InputHTMLAttributes<HTMLInputElement>;


export const Input = React.forwardRef<HTMLInputElement, Props>(function Input({ className, ...props }, ref) {
return (
<input
ref={ref}
className={clsx(
"w-full rounded-xl bg-transparent border border-border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/50",
className
)}
{...props}
/>
);
});