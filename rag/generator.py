import openai
from config import Config

openai.api_key = Config.OPENAI_API_KEY

def generate_response(context, difficulty):
    prompt = f"""
    You are an interview system.

    Context:
    {context}

    Generate a {difficulty} level interview question based on the context.
    Also provide the correct answer and a hint.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]
