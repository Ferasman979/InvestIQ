from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from db_config import get_db
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

llm = ChatGoogleGenerativeAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash-lite",
    temperature=0.2
)

class GenerateSecurityQuestionRequest(BaseModel):
    pass

class VerifyRequest(BaseModel):
    user_answer: str
    question: str
    context: str

def fetch_recent_transactions():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT merchant, amount, category, transaction_date
        FROM hist_transactions
        WHERE transaction_date >= CURDATE() - INTERVAL 2 DAY
        ORDER BY transaction_date DESC
        LIMIT 3
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def fetch_personal_details():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT first_name, last_name, dob, mother_maiden_name, first_car_make, first_pet_name 
        FROM personal_details_plaintext
        LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def format_personal_details_context(details):
    if not details:
        return ""
    fields = [
        ("First Name", details.get("first_name")),
        ("Last Name", details.get("last_name")),
        ("Date of Birth", str(details.get("dob")) if details.get("dob") else None),
        ("Mother's Maiden Name", details.get("mother_maiden_name")),
        ("First Car Make", details.get("first_car_make")),
        ("First Pet Name", details.get("first_pet_name"))
    ]
    return "\n".join(f"{k}: {v}" for k, v in fields if v is not None and v != "")

@app.post("/generate-security-question")
def generate_security_question(req: GenerateSecurityQuestionRequest):
    try:
        # --- TRANSACTION-BASED QUESTION ---
        txns = fetch_recent_transactions()
        if not txns:
            return JSONResponse(status_code=404, content={"error": "No transactions found"})

        context_str = "\n".join([
            f"{t['merchant']} ({t['category']}) on {t['transaction_date'].strftime('%Y-%m-%d')}"
            for t in txns
        ])

        prompt1 = f"""
You are a friendly banking assistant. Below is a list of recent transactions (merchant, category, date in YYYY-MM-DD).

Write one polite, natural question asking the user for the merchant’s name. The question must:
- Mention the transaction category.
- Refer to when it happened using only natural terms like "today," "yesterday," or "the day before yesterday."
- Never use vague terms like "recent" or "past" or include the actual date.

Do not mention transaction amounts or any other details. Output only the question.

Transactions:
{context_str}
"""







        llm_response1 = llm.invoke(prompt1)
        question1 = llm_response1.content.strip()

        # --- PERSONAL DETAILS QUESTION ---
        personal_details = fetch_personal_details()
        personal_details_str = format_personal_details_context(personal_details)

        prompt2 = f"""
You are a digital banking assistant. Based on the following personal details, ask ONE friendly and specific security question to verify the user. Use the available details (name, date of birth, mother's maiden name, first car make, first pet name), picking what is most relevant. Make the question clear and refer directly to one named detail. Respond ONLY with the question and nothing else.

Personal details:
{personal_details_str}
"""

        llm_response2 = llm.invoke(prompt2)
        question2 = llm_response2.content.strip()

        # Compose both questions for frontend to display
        blocking_msg = "Hi, I have blocked your transaction, cuz it seemed suspicious! Please answer a couple of questions to verify it's you."
        full_question1 = f"{blocking_msg}\n\nQuestion 1: {question1}"
        full_question2 = f"Question 2: {question2}"

        return {
            "security_questions": [full_question1, full_question2],
            "contexts": [context_str, personal_details_str]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/verify-security-answer")
def verify_security_answer(req: VerifyRequest):
    try:
        prompt = f"""
Context:
{req.context}

Security question:
{req.question}

User's answer:
{req.user_answer}

Is this answer semantically correct based on the question and context? Return only 'True' or 'False'.
"""
        llm_response = llm.invoke(prompt)
        verdict = llm_response.content.strip().lower()
        if verdict not in ['true', 'false']:
            verdict = 'false'

        return {"result": verdict}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
