from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_answer(question, user_answer):
    prompt = f"""
You are an interview evaluator.

Question:
{question}

Candidate Answer:
{user_answer}

Give:
1. A score between 0 and 1
2. Short feedback

Return format:
Score: <number>
Feedback: <text>
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
