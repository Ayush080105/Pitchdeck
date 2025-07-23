import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

system_prompt = """
You are a seasoned Venture Capitalist (VC) with expertise in evaluating startup pitches.
Your job is to:
1. Carefully analyze the founder's pitch.
2. Ask insightful, high-quality questions one at a time.
3. Wait for the founder's answer before asking the next question.
4. End the session when you're satisfied or the founder types "exit".
5. After the Q&A ends, evaluate the pitch and answers:
   - Give a score out of 10.
   - List 2-3 strengths.
   - List 2-3 areas for improvement.
   - Conclude with a final verdict (e.g., "Invest", "Needs Work", "Pass").

Be thoughtful, critical, and constructive. Ask follow-ups if needed.
"""

conversation = [{"role": "system", "content": system_prompt}]

def chat_with_groq():
    print("👩‍💼 VC: Hello Founder! Please paste your pitch below to get started.\n")

    while True:
        user_input = input("🧑‍💼 Founder: ")
        if user_input.lower().strip() == "exit":
            print("\n📊 VC: Thank you. Let me evaluate your pitch...\n")
            break

        conversation.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            messages=conversation,
            model="llama3-70b-8192"
        )

        assistant_reply = response.choices[0].message.content.strip()
        print(f"\n👩‍💼 VC: {assistant_reply}\n")

        conversation.append({"role": "assistant", "content": assistant_reply})

    
    evaluation_prompt = """
You are now done asking questions. Based on the entire conversation so far, give a comprehensive evaluation:
1. Rate the pitch out of 10.
2. Mention 2-3 strengths of the pitch and answers.
3. Suggest 2-3 areas of improvement.
4. Conclude with a clear verdict: Invest / Needs Work / Pass.
Be specific and professional, dont give html in return.
"""
    conversation.append({"role": "user", "content": evaluation_prompt})

    final_eval = client.chat.completions.create(
        messages=conversation,
        model="llama3-70b-8192"
    )
    final_feedback = final_eval.choices[0].message.content.strip()

    print("\n Final Evaluation:")
    print(final_feedback)

if __name__ == "__main__":
    chat_with_groq()
