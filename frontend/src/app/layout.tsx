import type { Metadata } from "next";
import "./globals.css";


export const metadata: Metadata = {
    title: "Fraud IQ",
    description: "Transactions + Agent Chat",
};


export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
        <body>
        <header className="border-b border-border">
        <nav className="container flex items-center justify-between h-16">
        <div className="flex items-center gap-2">
        <span className="font-semibold">Fraud IQ</span>
        </div>
        <div className="flex gap-4 text-sm text-muted">
        <a href="/" className="hover:text-white">Transactions</a>
        <a href="/chat" className="hover:text-white">Agent Chat</a>
        </div>
        </nav>
        </header>
        <main className="container py-8">{children}</main>
        </body>
        </html>
    );
}