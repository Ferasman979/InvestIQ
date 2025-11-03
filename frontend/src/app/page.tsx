"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { Txn } from "@/lib/types";
import { txns as mockTxns } from "@/lib/mock";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function HomePage() {
  const router = useRouter();

  const [q, setQ] = useState("");
  const [sortKey, setSortKey] = useState<"transaction_date" | "amount">(
    "transaction_date"
  );
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [rows, setRows] = useState<Txn[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [newMerchant, setNewMerchant] = useState("");
  const [newAmount, setNewAmount] = useState<string>("");
  const [newCurrency, setNewCurrency] = useState("CAD");

  useEffect(() => {
    try {
      setRows(mockTxns);
      setError(null);
    } catch (e: any) {
      setError(e.message ?? "error");
    } finally {
      setLoading(false);
    }
  }, []);

  const filtered = useMemo(() => {
    const s = rows.filter((t) =>
      [t.merchant, t.status, t.currency].some((v) =>
        v?.toLowerCase().includes(q.toLowerCase())
      )
    );
    const sorted = [...s].sort((a, b) => {
      if (sortKey === "transaction_date") {
        return (
          a.transaction_date.localeCompare(b.transaction_date) *
          (sortDir === "asc" ? 1 : -1)
        );
      }
      return (a.amount - b.amount) * (sortDir === "asc" ? 1 : -1);
    });
    return sorted;
  }, [q, sortKey, sortDir, rows]);

  function badge(status: string, suspicious: boolean) {
    if (suspicious) return <Badge color="red">suspicious</Badge>;
    if (status === "cleared") return <Badge color="green">cleared</Badge>;
    if (status === "pending") return <Badge color="yellow">pending</Badge>;
    if (status === "approved") return <Badge color="green">approved</Badge>;
    if (status === "blocked") return <Badge color="red">blocked</Badge>;
    return <Badge color="blue">{status}</Badge>;
  }

  function runClientSideVerification(tx: Txn) {
    const highAmount = tx.amount > 5000;
    const shadyMerchant = /fraud|unknown|test/i.test(tx.merchant);

    if (highAmount || shadyMerchant) {
      const updated: Txn = { ...tx, status: "blocked", suspicious_flag: true };
      setRows((prev) =>
        prev.map((t) =>
          t.transaction_id === updated.transaction_id ? updated : t
        )
      );
      router.push(
        `/chat?txId=${encodeURIComponent(
          updated.transaction_id
        )}&merchant=${encodeURIComponent(
          updated.merchant
        )}&amount=${encodeURIComponent(updated.amount)}`
      );
    } else {
      const updated: Txn = { ...tx, status: "approved", suspicious_flag: false };
      setRows((prev) =>
        prev.map((t) =>
          t.transaction_id === updated.transaction_id ? updated : t
        )
      );
    }
  }

  function handleAddTransaction(e: React.FormEvent) {
    e.preventDefault();
    const amountNum = parseFloat(newAmount);
    if (!newMerchant.trim() || Number.isNaN(amountNum)) return;

    const now = new Date().toISOString();
    const newTx: Txn = {
      transaction_id: "tx-new-" + Date.now(),
      user_id: "user-123",
      amount: amountNum,
      currency: newCurrency,
      merchant: newMerchant.trim(),
      transaction_date: now,
      status: "pending",
      suspicious_flag: false,
      created_at: now,
      updated_at: now,
    };

    setRows((prev) => [...prev, newTx]);

    setShowForm(false);
    setNewMerchant("");
    setNewAmount("");

    runClientSideVerification(newTx);
  }

  return (
    <div className="space-y-6">
      {/* HEADER ROW WITH ADD BUTTON */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Transactions</h1>
        <div className="flex items-center gap-3 text-sm">
          <button
            onClick={() => setShowForm((v) => !v)}
            className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm hover:bg-white/5"
          >
            + Add transaction
          </button>
          <a className="text-[var(--muted)] hover:text-white" href="/chat">
            Go to Agent Chat →
          </a>
        </div>
      </div>

      {showForm && (
        <Card>
          <CardHeader
            title="New transaction"
            desc="Creates a pending transaction. Verification may redirect you to chat."
          />
          <CardBody>
            <form
              onSubmit={handleAddTransaction}
              className="flex flex-wrap items-end gap-3"
            >
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[var(--muted)]">Merchant</label>
                <input
                  className="rounded-xl bg-transparent border border-[var(--border)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500/50"
                  value={newMerchant}
                  onChange={(e) => setNewMerchant(e.target.value)}
                  placeholder="e.g., Apple Store"
                  required
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[var(--muted)]">Amount</label>
                <input
                  className="rounded-xl bg-transparent border border-[var(--border)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500/50"
                  type="number"
                  step="0.01"
                  value={newAmount}
                  onChange={(e) => setNewAmount(e.target.value)}
                  placeholder="e.g., 299.00"
                  required
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-[var(--muted)]">Currency</label>
                <input
                  className="rounded-xl bg-transparent border border-[var(--border)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500/50"
                  value={newCurrency}
                  onChange={(e) => setNewCurrency(e.target.value)}
                />
              </div>
              <button
                type="submit"
                className="rounded-xl bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-sm font-medium"
              >
                Add Transaction
              </button>
            </form>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader
          title="Recent Activity"
        />
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
                onChange={(e) => setSortKey(e.target.value as any)}
              >
                <option value="transaction_date">Date</option>
                <option value="amount">Amount</option>
              </select>
              <button
                onClick={() =>
                  setSortDir((d) => (d === "asc" ? "desc" : "asc"))
                }
                className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm hover:bg-white/5"
              >
                {sortDir === "asc" ? "Asc" : "Desc"}
              </button>
            </div>

            {loading && (
              <div className="text-sm text-[var(--muted)]">Loading…</div>
            )}
            {error && <div className="text-sm text-red-300">{error}</div>}

            {!loading && !error && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-[var(--muted)]">
                    <tr className="border-b border-[var(--border)]">
                      <th className="py-3">Date</th>
                      <th>Merchant</th>
                      <th>Amount</th>
                      <th>Currency</th>
                      <th>Status</th>
                      <th className="text-right">Flag</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((t) => (
                      <tr
                        key={t.transaction_id}
                        className="border-b border-[var(--border)] hover:bg-white/5"
                      >
                        <td className="py-3">
                          {new Date(t.transaction_date).toLocaleDateString()}
                        </td>
                        <td>{t.merchant}</td>
                        <td className="font-medium">
                          {t.amount < 0 ? "-" : "+"}$
                          {Math.abs(t.amount).toFixed(2)}
                        </td>
                        <td>{t.currency}</td>
                        <td>{t.status}</td>
                        <td className="text-right">
                          {badge(t.status, t.suspicious_flag)}
                        </td>
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
