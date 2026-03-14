from flask import Blueprint

practice_bp = Blueprint('practice', __name__)

@practice_bp.route('/')
def index():
    return "Practice page coming soon!"