from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_roadmap(user, retrieved_context):
    prompt = f"""
You are a career coach for Indian engineering students.
Generate a detailed personalized career roadmap in Markdown.

User details:
- Name: {user.name or 'Student'}
- Education: {user.education}
- Target Role: {user.target_role}
- Prep Time: {user.prep_time_weeks} weeks

Use this relevant knowledge to make it accurate:
{retrieved_context}

Structure:
- Overview & Goals
- Week-by-week plan
- Daily hours & resources (free preferred)
- Milestones & Hyderabad/India job tips
Keep it motivating and realistic.
"""

    response = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",  # Top free reasoning/coding model 2026 (256K context, strong)
        # Alternatives: "arcee-ai/trinity-large-preview:free" for chat/mock, or "nvidia/nemotron-3-nano-30b-a3b:free"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7,
    )

    return response.choices[0].message.content