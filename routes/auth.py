from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        age = request.form.get('age')
        education = request.form.get('education')
        target_role = request.form.get('target_role')
        prep_time_weeks = request.form.get('prep_time_weeks')

        # Validation (existing + new)
        if not all([username, email, password, name, age, education, target_role, prep_time_weeks]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('auth.register'))

        if int(age) < 18:
            flash('Age must be 18 or above!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register'))

        try:
            new_user = User(
                username=username, 
                email=email,
                name=name,
                age=int(age),
                education=education,
                target_role=target_role,
                prep_time_weeks=int(prep_time_weeks)
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))