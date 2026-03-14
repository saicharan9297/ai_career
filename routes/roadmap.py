from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from openai import OpenAI
from dotenv import load_dotenv
import os
import markdown

load_dotenv()

roadmap_bp = Blueprint('roadmap', __name__, url_prefix='/roadmap')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@roadmap_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    roadmap = None
    error = None
    loading = False

    print(f"DEBUG: Roadmap page accessed by {current_user.username} | Method: {request.method} | Role: {current_user.target_role}")

    if request.method == 'POST':
        loading = True
        print("DEBUG: POST received - starting generation")

        name = current_user.name or current_user.username or "Student"
        age = current_user.age or 22
        education = current_user.education or "B.Tech"
        role = current_user.target_role or "Software Engineer"
        weeks = current_user.prep_time_weeks or 8

        print(f"DEBUG: Generating for → Name: {name}, Role: {role}, Weeks: {weeks}")

        if not all([education, role, weeks]):
            error = "Profile incomplete. Please update education, target role & prep time first."
            flash(error, "warning")
            loading = False
            print("DEBUG: Profile incomplete")

        else:
            prompt = f"""
You are a professional career coach for students in Hyderabad, India.
Generate a realistic, step-by-step preparation roadmap for {name} (age {age}, {education} graduate).

Target Role: {role}
Available Preparation Time: {weeks} weeks

Strict Rules:
- Content must be 100% tailored to {role}
- If role is full stack developer → HTML, CSS, JavaScript, React, Node.js, databases, Git, projects, portfolio, LeetCode, GitHub
- If role is IAS/UPSC related → Polity, History, Geography, Economy, Current Affairs, Ethics
- NO UPSC/IAS content if role is not IAS-related
- Use only English, professional tone
- Divide into exactly {weeks} weeks
- Each week: title, daily hours (4-6 hrs), topics, free resources, 1-2 quizzes/projects
- Add Hyderabad/India job market tips in final section

Output in clean Markdown format only.

# Personalized Roadmap for {name} - {role} ({weeks} weeks)

## Overview & Goals

## Week 1
Topics
Resources
Project

Continue until week {weeks}

## Final Tips & Job Strategy (Hyderabad/India focused)
"""

            try:
                response = client.chat.completions.create(
                    model="meta-llama/llama-3.1-8b-instruct",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1800,
                    temperature=0.7,
                )

                raw_roadmap = response.choices[0].message.content.strip()

                # Convert markdown to HTML
                roadmap = markdown.markdown(raw_roadmap)

                loading = False

                print(f"DEBUG: SUCCESS - Roadmap generated (length: {len(raw_roadmap)} chars)")

            except Exception as e:
                loading = False
                error = f"Generation failed: {str(e)}. Check API key or try later."
                flash(error, "danger")
                print(f"DEBUG ERROR: {str(e)}")

    return render_template(
        'roadmap.html',
        roadmap=roadmap,
        error=error,
        loading=loading
    )