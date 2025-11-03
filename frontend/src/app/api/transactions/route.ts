import { NextRequest, NextResponse } from "next/server";


const BASE = process.env.FASTAPI_BASE ?? "http://localhost:8000"; // e.g., http://localhost:8000


export async function GET(req: NextRequest) {
const { searchParams } = new URL(req.url);
const qs = searchParams.toString();
const url = `${BASE}/transactions${qs ? `?${qs}` : ""}`;
try {
const r = await fetch(url, { cache: "no-store" });
if (!r.ok) return NextResponse.json({ error: `upstream ${r.status}` }, { status: 502 });
const data = await r.json();
return NextResponse.json(data);
} catch (e: any) {
return NextResponse.json({ error: e?.message ?? "proxy error" }, { status: 500 });
}
}