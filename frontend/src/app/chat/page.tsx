"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const txId = searchParams.get("txId");
  const merchant = searchParams.get("merchant");
  const amount = searchParams.get("amount");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  // Initial welcome or verification prompt
  useEffect(() => {
    const base: ChatMessage[] = [];
    if (txId && merchant && amount) {
      base.push({
        id: "m0",
        role: "assistant",
        content: `We flagged a transaction (${txId}) at ${merchant} for $${amount}. Please answer the following security question:\nWhat is your mother's maiden name?.`,
        timestamp: Date.now(),
      });
    } else {
      base.push({
        id: "m0",
        role: "assistant",
        content: "Hi! I can help verify transactions that were flagged as suspicious.",
        timestamp: Date.now(),
      });
    }
    setMessages(base);
  }, [txId, merchant, amount]);

  // Scroll to bottom on new messages
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!text.trim()) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text.trim(),
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setText("");

    try {
      // If user wants to verify a transaction
      if (txId && merchant && amount) {
        const response = await fetch(`${API_BASE}/verify-transaction`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            transaction_id: txId,
            user_id: "U001", // Replace with real user_id later
            amount: parseFloat(amount),
            merchant: merchant,
            category: "online",
            tx_date: new Date().toISOString(),
            country: "CA",
          }),
        });

        const data = await response.json();
        let replyText = "";

        if (data.suspicious) {
          replyText = `⚠️ Transaction ${data.transaction_id} was flagged as *suspicious* (${data.reason}).\n\nSecurity Question: ${
            data.security_question ?? "Can you confirm if this is your transaction? (YES / NO)"
          }`;
        } else {
          replyText = `✅ Transaction ${data.transaction_id} looks safe and has been *approved*.`;
        }

        const asstMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: replyText,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, asstMsg]);
      } else {
        // General chat fallback (not tied to a transaction)
        const fallbackMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "I can only verify transactions right now. Try providing a transaction ID, merchant, and amount in the URL.",
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, fallbackMsg]);
      }
    } catch (error) {
      console.error("Error verifying transaction:", error);
      const errMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "🚨 Sorry, I couldn’t reach the verification service. Please try again later.",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errMsg]);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Transaction Verification Assistant</h1>
      <Card>
        <CardHeader
          title="Fraud Detection Chat"
          desc="This assistant verifies flagged transactions and confirms ownership."
        />
        <CardBody className="space-y-4">
          <div ref={listRef} className="h-[450px] overflow-y-auto pr-2">
            <div className="space-y-3">
              {messages.map((m) => (
                <div key={m.id} className="flex">
                  <div
                    className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
                      m.role === "user"
                        ? "ml-auto bg-blue-500/20 text-right"
                        : "bg-gray-800/20 text-left"
                    }`}
                  >
                    <div className="opacity-70 text-xs mb-1">{m.role}</div>
                    <div>{m.content}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type YES, NO, or ask about the transaction"
            />
            <Button onClick={handleSend}>Send</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
