from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re
import traceback

load_dotenv()

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def aggressive_json_repair(broken: str) -> str:
    """
    Very aggressive repair for LLM-generated JSON that is often truncated mid-object
    """
    s = broken.strip()

    s = re.sub(r'^[^[]*\[', '[', s, flags=re.DOTALL)
    s = re.sub(r'\][^]]*$', ']', s, flags=re.DOTALL)
    s = re.sub(r'```json|```|json\s*', '', s, flags=re.IGNORECASE)

    s = re.sub(r',\s*([}\]])', r'\1', s, flags=re.DOTALL)

    open_curlies = s.count('{') - s.count('}')
    open_squares = s.count('[') - s.count(']')

    if open_curlies > 0:
        s += '}' * open_curlies
    if open_squares > 0:
        s += ']' * open_squares

    lines = s.splitlines()
    if lines and not lines[-1].strip().endswith(('}', ']')):
        last_line = lines[-1].rstrip()
        if last_line.endswith(',') or last_line.endswith(':') or '"' in last_line[-1]:
            s = '\n'.join(lines[:-1]) + '\n    }\n  ]\n'

    s = re.sub(r',\s*([}\]])', r'\1', s)
    s = s.rstrip(', \t\n\r')

    return s


def is_valid_quiz_question(q):
    """Basic structural validation"""
    required = {'question', 'options', 'correct'}
    if not all(k in q for k in required):
        return False
    if not isinstance(q['options'], list) or len(q['options']) != 4:
        return False
    if not isinstance(q['correct'], int) or q['correct'] not in range(4):
        return False
    return True


@quiz_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    score = None
    feedback = None
    error = None

    role = current_user.target_role or "Software Engineer"

    questions = []

    if request.method == 'GET':
        # Always generate fresh questions when the page is loaded / retaken
        questions = generate_quiz_questions(role)
        if questions:
            session['quiz_questions'] = questions
            session.modified = True
            print("DEBUG: Fresh questions generated and stored in session for this visit")
        else:
            questions = []
            print("DEBUG: Failed to generate questions - using empty list")

    elif request.method == 'POST':
        # On submit: load from session (just generated on GET)
        questions = session.get('quiz_questions', [])
        print(f"DEBUG: POST - Loaded {len(questions)} questions from session")

        if not questions:
            flash("No questions available. Please refresh to start a new quiz.", "warning")
        else:
            score_value = 0
            feedback_list = []
            answered_count = 0

            for i, q in enumerate(questions):
                user_key = f'q{i}'
                user_ans = request.form.get(user_key)

                if user_ans is not None and user_ans.strip():
                    try:
                        choice = int(user_ans)
                        answered_count += 1
                        if choice == q['correct']:
                            score_value += 1
                            feedback_list.append(f"Q{i+1}: Correct ✓")
                        else:
                            correct_answer = q['options'][q['correct']]
                            feedback_list.append(f"Q{i+1}: Wrong - Correct: {correct_answer}")
                    except ValueError:
                        feedback_list.append(f"Q{i+1}: Invalid answer")
                else:
                    feedback_list.append(f"Q{i+1}: Not answered")

            score = f"Your score: {score_value}/{len(questions)} ({answered_count} answered)"
            feedback = "<br>".join(feedback_list)

            # Clear the old questions so retake / refresh generates new ones
            session.pop('quiz_questions', None)
            session.modified = True
            print("DEBUG: Cleared old quiz questions from session after submission")

    return render_template(
        'quiz.html',
        questions=questions,
        score=score,
        feedback=feedback,
        error=error,
        role=role
    )


def generate_quiz_questions(role: str):
    """Helper function to generate and parse questions"""
    prompt = f"""Generate **exactly 5** multiple-choice questions for someone preparing to become a {role}.

Rules (follow strictly):
- Output ONLY valid JSON — no explanations, no markdown, no extra text
- Exactly this structure:
[
  {{
    "question": "short clear question text",
    "options": ["A. First choice", "B. Second choice", "C. Third choice", "D. Fourth choice"],
    "correct": 0   // 0,1,2 or 3 — index of correct option
  }},
  ...
]
- Make sure every object has "question", "options" (exactly 4 items), "correct"
- Do NOT truncate — complete all 5 questions
"""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1800,
            temperature=0.35,
            timeout=180
        )

        raw = response.choices[0].message.content.strip()
        print("DEBUG: Raw LLM response length:", len(raw))
        print("DEBUG: Raw LLM response first 800 chars:\n", raw[:800])

        repaired = aggressive_json_repair(raw)
        print("DEBUG: After repair:\n", repaired[:1000], "...")

        parsed = json.loads(repaired)

        if not isinstance(parsed, list):
            raise ValueError("Root is not a list")

        valid_questions = [q for q in parsed if is_valid_quiz_question(q)]

        if len(valid_questions) == 0:
            raise ValueError("No valid questions found")

        print(f"DEBUG: Successfully generated {len(valid_questions)} valid questions")
        return valid_questions[:5]

    except Exception as e:
        print("───────────────────────────────────────────────")
        print("QUIZ GENERATION FAILED:", str(e))
        traceback.print_exc()
        print("───────────────────────────────────────────────")
        flash("Quiz generation failed — using sample questions.", "warning")

        # Fallback sample questions
        return [
            {
                "question": f"What is a key responsibility of a {role}?",
                "options": [
                    "A. Writing maintainable code",
                    "B. Managing finances",
                    "C. Cooking meals",
                    "D. Driving vehicles"
                ],
                "correct": 0
            },
            {
                "question": f"Which skill is essential for a {role}?",
                "options": ["A. Singing", "B. Problem-solving", "C. Painting", "D. Dancing"],
                "correct": 1
            },
            {
                "question": f"What tool might a {role} use daily?",
                "options": ["A. Hammer", "B. IDE / Code editor", "C. Sewing machine", "D. Stethoscope"],
                "correct": 1
            },
            {
                "question": f"Best practice in {role}?",
                "options": ["A. Ignore errors", "B. Write tests", "C. Copy code", "D. Skip documentation"],
                "correct": 1
            },
            {
                "question": f"Common challenge in {role}?",
                "options": ["A. Debugging", "B. Sleeping", "C. Eating", "D. Watching TV"],
                "correct": 0
            },
        ]