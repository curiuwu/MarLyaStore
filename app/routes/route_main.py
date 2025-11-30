from flask import Blueprint, render_template, flash

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def main_page():
    return render_template('index.html')