"use client";
import { useEffect, useMemo, useState } from "react";
import type { Txn } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { txns as mockTxns } from "@/lib/mock"; // ← use local mock

export default function HomePage() {
  const [q, setQ] = useState("");
  const [sortKey, setSortKey] = useState<"transaction_date" | "amount">("transaction_date");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [rows, setRows] = useState<Txn[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        // When FastAPI is ready, switch to:
        // const r = await fetch("/api/transactions", { cache: "no-store" });
        // if (!r.ok) throw new Error(`HTTP ${r.status}`);
        // const data: Txn[] = await r.json();
        // setRows(data);
        setRows(mockTxns); // mock for now
        setError(null);
      } catch (e: any) {
        setError(e.message ?? "error");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filtered = useMemo(() => {
    const s = rows.filter(t =>
      [t.merchant, t.status, t.currency].some(v => v?.toLowerCase().includes(q.toLowerCase()))
    );
    const sorted = [...s].sort((a, b) => {
      if (sortKey === "transaction_date") {
        return a.transaction_date.localeCompare(b.transaction_date) * (sortDir === "asc" ? 1 : -1);
      }
      return (a.amount - b.amount) * (sortDir === "asc" ? 1 : -1);
    });
    return sorted;
  }, [q, sortKey, sortDir, rows]);

  function badge(status: string, suspicious: boolean) {
    if (suspicious) return <Badge color="red">suspicious</Badge>;
    if (status === "cleared") return <Badge color="green">cleared</Badge>;
    if (status === "pending") return <Badge color="yellow">pending</Badge>;
    return <Badge color="blue">{status}</Badge>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Transactions</h1>
        <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
          <a className="hover:text-white" href="/chat">Go to Agent Chat →</a>
        </div>
      </div>

      <Card>
        <CardHeader title="Recent Activity" desc="Using local mock data" />
        <CardBody>
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <input
                placeholder="Search merchant, status, or currency…"
                className="w-full rounded-xl bg-transparent border border-[var(--border)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500/50"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
              <select
                className="rounded-xl bg-transparent border border-[var(--border)] px-3 py-2 text-sm"
                value={sortKey}
                onChange={(e)=> setSortKey(e.target.value as any)}
              >
                <option value="transaction_date">Date</option>
                <option value="amount">Amount</option>
              </select>
              <button
                onClick={()=> setSortDir(d => d === "asc" ? "desc" : "asc")}
                className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm hover:bg-white/5"
              >{sortDir === "asc" ? "Asc" : "Desc"}</button>
            </div>

            {loading && <div className="text-sm text-[var(--muted)]">Loading…</div>}
            {error && <div className="text-sm text-red-300">{error}</div>}

            {!loading && !error && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-[var(--muted)]">
                    <tr className="border-b border-[var(--border)]">
                      <th className="py-3">Date</th>
                      <th>Merchant</th>
                      <th className="text-right">Amount</th>
                      <th>Currency</th>
                      <th>Status</th>
                      <th className="text-right">Flag</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((t) => (
                      <tr key={t.transaction_id} className="border-b border-[var(--border)] hover:bg-white/5">
                        <td className="py-3">{new Date(t.transaction_date).toLocaleDateString()}</td>
                        <td>{t.merchant}</td>
                        <td className="text-right font-medium">
                          {t.amount < 0 ? "-" : "+"}${Math.abs(t.amount).toFixed(2)}
                        </td>
                        <td className="text-[var(--muted)]">{t.currency}</td>
                        <td>{t.status}</td>
                        <td className="text-right">{badge(t.status, t.suspicious_flag)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
