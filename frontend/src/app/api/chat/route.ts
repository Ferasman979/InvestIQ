import { NextRequest, NextResponse } from "next/server";

const BASE = process.env.FASTAPI_BASE ?? "http://localhost:8000";

function buildMockTransaction(message: string) {
  const now = new Date().toISOString();
  const highAmount = /high|large|big/i.test(message);
  const fraudMerchant = /fraud|scam/i.test(message);

  return {
    transaction_id: "tx-" + Date.now(),
    user_id: "user-123",
    amount: highAmount ? 6000 : 42.5,
    currency: "CAD",
    merchant: fraudMerchant ? "fraud_shop" : "Amazon",
    transaction_date: now,
    status: "pending",
    suspicious_flag: false,
    created_at: now,
    updated_at: now,
  };
}

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  const tx = buildMockTransaction(String(message ?? ""));

  const url = `${BASE}/api/transactions/api/verify-transaction`;

  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tx),
    });

    if (!r.ok) {
      return NextResponse.json(
        { reply: `Upstream error: ${r.status}` },
        { status: 502 }
      );
    }

    const data = await r.json() as {
      transaction_id: string;
      suspicious: boolean;
      reason: string;
    };

    const reply = data.suspicious
      ? `I blocked this transaction (${data.transaction_id}) because: ${data.reason}.`
      : `This transaction (${data.transaction_id}) looks normal: ${data.reason}.`;

    return NextResponse.json({ reply, raw: data });
  } catch (e: any) {
    return NextResponse.json(
      { reply: "Backend unavailable. Using mock reasoning only.", error: String(e?.message ?? e) },
      { status: 500 }
    );
  }
}
