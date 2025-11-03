export function Card({ children, className }: { children: React.ReactNode; className?: string }) {
return <div className={`card ${className ?? ""}`}>{children}</div>;
}


export function CardHeader({ title, desc }: { title: string; desc?: string }) {
return (
<div className="p-4 border-b border-border">
<h2 className="text-lg font-semibold">{title}</h2>
{desc && <p className="text-sm text-muted mt-1">{desc}</p>}
</div>
);
}


export function CardBody({ children, className }: { children: React.ReactNode; className?: string }) {
return <div className={`p-4 ${className ?? ""}`}>{children}</div>;
}