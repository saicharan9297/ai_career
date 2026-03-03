from flask import Flask, render_template, request, session, redirect, url_for
from config import Config
from models.models import db, User
from rag.rag_engine import generate_question
from services.adaptive_engine import adjust_difficulty
from services.roadmap_service import generate_roadmap
# from flask import Flask, render_template, request, session, redirect, url_for
# from config import Config
# from models.models import db, User

#  This "Try" block lets the server start even if the library is 'missing'
# try:
#     from rag.rag_engine import generate_question
#     from services.adaptive_engine import adjust_difficulty
#     from services.roadmap_service import generate_roadmap
# except ModuleNotFoundError:
#     print("⚠️ AI modules not found, but starting server for Frontend testing...")
#     generate_question = None 
#     adjust_difficulty = None
#     generate_roadmap = None

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)


# ===================================
# Home Page
# ===================================
@app.route("/")
def index():
    return render_template("index.html")


# ===================================
# Register
# ===================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return "All fields are required!", 400

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return "User already exists!", 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ===================================
# Login
# ===================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials!", 401

    return render_template("login.html")
# ===================================
# Dashboard Page
# ===================================
@app.route("/dashboard")
def dashboard():
    # Only allow logged-in users to see the dashboard
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("dashboard.html", username=session.get("username"))

# ===================================
# Logout
# ===================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===================================
# Generate Interview Question
# ===================================
@app.route("/generate_question", methods=["POST"])
def generate():

    # Protect route
    if "user_id" not in session:
        return redirect(url_for("login"))

    role = request.form.get("role")
    topic = request.form.get("topic")
    difficulty = request.form.get("difficulty", 1)

    if not role or not topic:
        return "Role and Topic are required!", 400

    try:
        difficulty = int(difficulty)
    except ValueError:
        difficulty = 1

    session["role"] = role
    session["topic"] = topic
    session["difficulty"] = difficulty

    try:
        question = generate_question(role, topic, difficulty)
    except Exception as e:
        return f"Error generating question: {str(e)}", 500

    return render_template(
        "practice.html",
        question=question,
        role=role,
        topic=topic,
        difficulty=difficulty
    )


# ===================================
# Submit Answer (Adaptive Engine)
# ===================================
@app.route("/submit_answer", methods=["POST"])
def submit_answer():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_answer = request.form.get("answer")
    current_difficulty = session.get("difficulty", 1)

    is_correct = True if user_answer and len(user_answer) > 10 else False

    new_difficulty = adjust_difficulty(current_difficulty, is_correct)

    session["difficulty"] = new_difficulty

    return render_template(
        "result.html",
        correct=is_correct,
        new_difficulty=new_difficulty
    )


# ===================================
# Generate Career Roadmap
# ===================================
@app.route("/roadmap", methods=["POST"])
def roadmap():

    if "user_id" not in session:
        return redirect(url_for("login"))

    age = request.form.get("age")
    education = request.form.get("education")
    role = request.form.get("role")
    hours = request.form.get("hours")

    if not role:
        return "Role is required!", 400

    try:
        plan = generate_roadmap(age, education, role, hours)
    except Exception as e:
        return f"Error generating roadmap: {str(e)}", 500

    return render_template("roadmap.html", roadmap=plan)


# ===================================
# Run Application
# ===================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
