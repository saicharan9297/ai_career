from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import db, User
from werkzeug.exceptions import BadRequestKeyError

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Optional: show message if profile is incomplete
    if not current_user.education or not current_user.target_role or not current_user.prep_time_weeks:
        flash("Please complete your profile to unlock full features (roadmap, progress, etc.)", "info")
    
    return render_template('dashboard.html', user=current_user)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            age_str = request.form.get('age', '').strip()
            education = request.form.get('education', '').strip()
            target_role = request.form.get('target_role', '').strip()
            prep_time_str = request.form.get('prep_time_weeks', '8').strip()

            # Basic validation
            if not all([name, age_str, education, target_role, prep_time_str]):
                flash("All fields are required!", "danger")
                return redirect(url_for('main.profile'))

            age = int(age_str)
            prep_time_weeks = int(prep_time_str)

            if age < 18 or age > 40:
                flash("Age must be between 18 and 40.", "danger")
                return redirect(url_for('main.profile'))

            if prep_time_weeks < 4 or prep_time_weeks > 52:
                flash("Preparation time must be between 4 and 52 weeks.", "danger")
                return redirect(url_for('main.profile'))

            # Update user
            current_user.name = name
            current_user.age = age
            current_user.education = education
            current_user.target_role = target_role
            current_user.prep_time_weeks = prep_time_weeks

            db.session.commit()

            flash("Profile updated successfully! You can now generate your roadmap.", "success")
            return redirect(url_for('main.dashboard'))

        except (ValueError, BadRequestKeyError):
            flash("Invalid input. Please check age and weeks fields.", "danger")
            return redirect(url_for('main.profile'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('main.profile'))

    # GET: show form with current values
    return render_template('profile.html', user=current_user)