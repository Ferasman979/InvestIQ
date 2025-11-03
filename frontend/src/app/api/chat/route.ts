import { NextRequest, NextResponse } from "next/server";


export async function POST(req: NextRequest) {
const { message } = await req.json();

let reply = "I need more details.";
if (/apple/i.test(message)) reply = "The Apple charge was flagged due to higher-than-usual amount compared to your 30-day average.";
if (/recurr|subscription|rent/i.test(message)) reply = "I see a recurring pattern. I can schedule a reminder one day before due date.";
if (/budget|spend/i.test(message)) reply = "Your top categories this week are Food and Transport. Consider a $200 cap for Food.";
return NextResponse.json({ reply });
}