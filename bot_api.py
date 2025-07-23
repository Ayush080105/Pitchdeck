import os
import json
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Create folder for conversation history
os.makedirs("conversations", exist_ok=True)

app = FastAPI()


with open("questions.txt", "r", encoding="utf-8") as f:
    sample_questions = f.read().strip()

with open("sample_pitches.txt", "r", encoding="utf-8") as f:
    sample_pitches = f.read().strip()

# Default system prompt
system_prompt = f"""
You are a seasoned Venture Capitalist (VC) with expertise in evaluating startup pitches.
Your job is to:
1. Carefully analyze the founder's pitch.
2. Ask insightful, high-quality questions one at a time.
3. Wait for the founder's answer before asking the next question.
4. End the session when you're satisfied or the founder types "exit".
5. Dont ask very long questions. Ask one question at a time only strictly.
6. After the Q&A ends, evaluate the pitch and answers:
   - Give a score out of 10.
   - List 2-3 strengths.
   - List 2-3 areas for improvement.
   - Conclude with a final verdict: Invest / Needs Work / Pass.

Be thoughtful, critical, and constructive. Ask follow-ups if needed.

Below are examples of good questions you may be inspired by:
-----
{sample_questions}
-----

And here are some example founder pitches to guide your expectations:
-----
{sample_pitches}
-----

Now, begin the session.
"""

evaluation_prompt = """
You are now done asking questions. Based on the entire conversation so far, give a comprehensive evaluation:

1. Score out of 10
2. 2-3 Strengths
3. 2-3 Areas for improvement
4. Final Verdict: Invest / Needs Work / Pass

Make it concise, insightful, and professional.
"""
# In-memory cache: session_id → conversation + session_complete flag
session_data: Dict[str, Dict] = {}

class UserInput(BaseModel):
    message: str
    session_id: str  # uniquely identifies a session (can be uuid4 from frontend)

def load_session(session_id: str):
    path = f"conversations/{session_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return [{"role": "system", "content": system_prompt}]

def save_session(session_id: str, conversation):
    with open(f"conversations/{session_id}.json", "w") as f:
        json.dump(conversation, f, indent=2)

@app.post("/vc/message")
def vc_qna(user_input: UserInput):
    session_id = user_input.session_id
    message = user_input.message.strip()

    # Load or initialize conversation
    conversation = load_session(session_id)

    # Check if session already completed
    if conversation and any(m["content"] == evaluation_prompt for m in conversation):
        return {"message": "Session already ended. Please restart."}

    # If "exit", trigger evaluation
    if message.lower() == "exit":
        conversation.append({"role": "user", "content": "exit"})
        conversation.append({"role": "user", "content": evaluation_prompt})

        response = client.chat.completions.create(
            messages=conversation,
            model="llama3-70b-8192"
        )
        reply = response.choices[0].message.content.strip()
        conversation.append({"role": "assistant", "content": reply})
        save_session(session_id, conversation)

        return {
            "message": "Q&A complete. Here's your final evaluation:",
            "evaluation": reply,
            "done": True
        }

    # Add user input
    conversation.append({"role": "user", "content": message})

    # Get assistant reply
    response = client.chat.completions.create(
        messages=conversation,
        model="llama3-70b-8192"
    )
    reply = response.choices[0].message.content.strip()
    conversation.append({"role": "assistant", "content": reply})

    # Save updated conversation
    save_session(session_id, conversation)

    return {
        "message": reply,
        "done": False
    }

@app.post("/vc/reset")
def reset_session(user_input: UserInput):
    session_id = user_input.session_id
    conversation = [{"role": "system", "content": system_prompt}]
    save_session(session_id, conversation)
    return {"message": f"Session '{session_id}' reset."}
