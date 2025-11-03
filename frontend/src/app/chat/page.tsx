"use client";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

type ChatMessage = { id: string; role: "user" | "assistant"; content: string; timestamp: number };

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: "m0", role: "assistant", content: "Hi. I can analyze transactions and explain anomalies.", timestamp: Date.now() },
  ]);
  const [text, setText] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => { listRef.current?.scrollTo({ top: listRef.current.scrollHeight }); }, [messages]);

  async function send() {
    if (!text.trim()) return;
    const user: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text.trim(),
      timestamp: Date.now(),
    };
    setMessages((m) => [...m, user]);
    setText("");

    const r = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message: user.content }),
    });
    const json = await r.json();
    const asst: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: json.reply,
      timestamp: Date.now(),
    };
    setMessages((m) => [...m, asst]);
  }



  function mockReply(q: string) {
    if (/apple/i.test(q)) return "The Apple charge was flagged due to a higher-than-usual amount.";
    if (/recurr|subscription|rent/i.test(q)) return "Recurring pattern detected. I can schedule a reminder.";
    if (/budget|spend/i.test(q)) return "Top categories this week are Food and Transport.";
    return "Noted. Ask about a transaction, budget, or recurring payment.";
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Agent Chat</h1>
      <Card>
        <CardHeader title="Conversation" desc="Mock agent. Replace with API when ready" />
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
              placeholder="e.g., Why was my Apple charge flagged?"
            />
            <Button onClick={send}>Send</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
