// Shared domain types for frontend

export type TxnStatus =
  | "pending"
  | "verified"
  | "failed"
  | "approved"
  | "blocked"
  | "cleared";

export type Txn = {
  transaction_id: string;
  user_id: string;
  amount: number;
  currency: string;
  merchant: string;
  transaction_date: string; // ISO string
  status: TxnStatus;
  suspicious_flag: boolean;
  created_at?: string;
  updated_at?: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
};
