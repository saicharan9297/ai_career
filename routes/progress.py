from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import db
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

progress_bp = Blueprint('progress', __name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Assume roadmap has 4 steps – store in user or separate table later
STEPS = [
    "Week 1-2: DSA Basics",
    "Week 3-5: Advanced DSA",
    "Week 6-8: System Design",
    "Week 9-12: Mock Interviews"
]

@progress_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Simple progress (0-100% based on completed steps)
    completed_steps = 1  # Dummy – later DB nunchi
    total_steps = len(STEPS)
    progress_percent = (completed_steps / total_steps) * 100

    if request.method == 'POST':
        step_index = int(request.form.get('step'))
        user_answer = request.form.get('answer')

        # LLM generate quiz for step (3 MCQs)
        prompt = f"Generate 3 multiple choice quiz questions for {STEPS[step_index]} (Software Engineer prep). Each with 4 options, correct answer marked."

        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.5,
        )
        quiz = response.choices[0].message.content

        # Simple score (dummy – later check answer)
        score = 80 if user_answer else 0
        if score >= 70:
            completed_steps += 1
            flash('Quiz passed! Next step unlocked.', 'success')
        else:
            flash('Try again! Score: ' + str(score) + '%', 'warning')

        db.session.commit()  # Save progress

    return render_template('progress.html', steps=STEPS, completed_steps=completed_steps, progress_percent=progress_percent)

@progress_bp.route('/quiz/<int:step_index>', methods=['GET', 'POST'])
@login_required
def quiz(step_index):
    # LLM generate quiz for specific step
    prompt = f"Create 5 MCQ questions for {STEPS[step_index]} in Software Engineer roadmap. Format: Q1: Question? a) opt1 b) opt2 c) opt3 d) opt4 Correct: c"

    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.6,
    )
    quiz_content = response.choices[0].message.content

    if request.method == 'POST':
        # Score logic (dummy)
        score = 75
        flash(f'Quiz completed! Score: {score}%')
        return redirect(url_for('progress.index'))

    return render_template('quiz.html', quiz_content=quiz_content, step=STEPS[step_index])