import streamlit as st
import requests

# Dark themed header styled like a chat contact bar
chat_header = """
<div style="
    display: flex;
    align-items: center;
    padding: 16px;
    background: #1a1e25;
    border-bottom: 1px solid #22242c;
    margin-bottom: 10px;">
  <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" width="42" style="border-radius:21px; margin-right:16px; border:2px solid #4ea8de;">
  <span style="font-size: 22px; font-weight: 600; color: #eaf6fb;">Digital Assistant</span>
</div>
"""

st.markdown(
    """
    <style>
        .stApp {
            background-color: #171923;
        }
    </style>
    """, unsafe_allow_html=True
)

st.markdown(chat_header, unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []

def add_message(sender, text, is_user=False):
    style = (
        "background: linear-gradient(135deg,#22283a,#353c4d); color: #f6f6f6; border-radius: 10px 10px 10px 0; padding: 12px 18px; margin-bottom: 8px; max-width: 75%;" if not is_user
        else "background: linear-gradient(135deg,#4ea8de,#243447); color: #f6f6f6; border-radius: 10px 10px 0 10px; padding: 12px 18px; margin-bottom: 8px; margin-left:auto; max-width: 75%; text-align: right;"
    )
    html = f'<div style="{style}"><strong>{sender}:</strong> {text}</div>'
    st.session_state.messages.append(html)

# INITIALIZE QUESTIONS AND CONTEXTS
if 'questions' not in st.session_state:
    resp = requests.post("http://localhost:8000/generate-security-question", json={})
    if resp.status_code == 200:
        data = resp.json()
        questions = data.get("security_questions", [])
        contexts = data.get("contexts", [])
        if questions:
            st.session_state.questions = questions
            st.session_state.contexts = contexts
            st.session_state.current_question_idx = 0
            st.session_state.answers = []
            add_message("Digital Assistant", "Hello! Thank you for connecting. Can you answer the security questions below?")
            add_message("Digital Assistant", f"Security Question: {questions[0]}")
        else:
            st.error("No security questions received.")
    else:
        st.error(f"Failed to generate question: {resp.text}")

for msg_html in st.session_state.messages:
    st.markdown(msg_html, unsafe_allow_html=True)

# Show question/answer input
if 'questions' in st.session_state and st.session_state.questions:
    idx = st.session_state.current_question_idx
    question = st.session_state.questions[idx]
    context = st.session_state.contexts[idx]
    if idx < len(st.session_state.questions):
        user_answer = st.text_input("Type your response and hit send...", key=f"answer_input_{idx}")
        if st.button("Send", key=f"send_btn_{idx}") and user_answer:
            add_message("You", user_answer, is_user=True)
            payload = {
                "user_answer": user_answer,
                "question": question,
                "context": context
            }
            resp = requests.post("http://localhost:8000/verify-security-answer", json=payload)
            result = resp.json().get("result", "").lower()
            if result == "true":
                add_message("Digital Assistant", "Your answer is right, approved.")
            else:
                add_message("Digital Assistant", "Your answer was incorrect. Not approved.")
            st.session_state.answers.append(user_answer)
            # Move to next question or end
            if idx + 1 < len(st.session_state.questions):
                st.session_state.current_question_idx += 1
                add_message("Digital Assistant", f"Security Question: {st.session_state.questions[idx+1]}")
                st.rerun()
            else:
                add_message("Digital Assistant", "Verification process completed.")
else:
    st.info("Connect to backend and await questions...")

