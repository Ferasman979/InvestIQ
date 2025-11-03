"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const txId = searchParams.get("txId");
  const merchant = searchParams.get("merchant");
  const amount = searchParams.get("amount");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const base: ChatMessage[] = [];
    if (txId && merchant && amount) {
      base.push({
        id: "m0",
        role: "assistant",
        content: `We flagged a transaction (${txId}) at ${merchant} for $${amount}. Is this your transaction? Reply YES or NO.`,
        timestamp: Date.now(),
      });
    } else {
      base.push({
        id: "m0",
        role: "assistant",
        content: "Hi. I can help verify transactions and explain suspicious activity.",
        timestamp: Date.now(),
      });
    }
    setMessages(base);
  }, [txId, merchant, amount]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages]);

  function handleSend() {
    if (!text.trim()) return;

    const user: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text.trim(),
      timestamp: Date.now(),
    };
    setMessages((m) => [...m, user]);

    const replyText = mockReply(user.content, txId, merchant, amount);
    const asst: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: replyText,
      timestamp: Date.now(),
    };
    setMessages((m) => [...m, asst]);
    setText("");
  }

  function mockReply(
    input: string,
    txId: string | null,
    merchant: string | null,
    amount: string | null
  ) {
    const normalized = input.trim().toLowerCase();
    if ((normalized === "yes" || normalized === "y") && txId) {
      return `Thanks, confirmed. I will approve transaction ${txId} and remove the suspicious flag.`;
    }
    if ((normalized === "no" || normalized === "n") && txId) {
      return `Understood. I will keep transaction ${txId} blocked and notify your bank's security team.`;
    }
    if (/why|reason|flag/i.test(normalized) && txId) {
      return `This transaction was flagged based on amount and merchant pattern. Once you confirm, I can approve it.`;
    }
    return "Got it. Reply YES if this transaction is yours, or NO if it is not.";
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Agent Chat</h1>
      <Card>
        <CardHeader
          title="Verification assistant"
          desc="Answer questions about flagged transactions. Backend will approve/deny later."
        />
        <CardBody className="space-y-4">
          <div ref={listRef} className="h-[450px] overflow-y-auto pr-2">
            <div className="space-y-3">
              {messages.map((m) => (
                <div key={m.id} className="flex">
                  <div
                    className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
                      m.role === "user" ? "ml-auto bg-white/10" : "bg-indigo-600/20"
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
              placeholder="Type YES or NO, or ask why it was flagged"
            />
            <Button onClick={handleSend}>Send</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
