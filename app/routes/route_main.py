from flask import Blueprint, render_template, flash, jsonify
from app import db
from app.models import Role, User, Currency, Valet

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def main_page():
    return render_template('index.html')

