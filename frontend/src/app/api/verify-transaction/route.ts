import { NextRequest, NextResponse } from "next/server";

const BASE = process.env.FASTAPI_BASE ?? "http://localhost:8000";
// FastAPI path from your code: /api/transactions/api/verify-transaction

export async function POST(req: NextRequest) {
  const tx = await req.json(); // full Transaction payload from frontend

  const url = `${BASE}/api/transactions/api/verify-transaction`;

  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tx),
    });

    const data = await r.json();
    return NextResponse.json(data, { status: r.status });
  } catch (e: any) {
    return NextResponse.json(
      { error: e?.message ?? "proxy error" },
      { status: 500 }
    );
  }
}
