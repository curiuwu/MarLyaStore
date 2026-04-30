"""Utilities for working with roles and PostgreSQL sequences."""

from sqlalchemy import func, text

from app import db


def normalize_role_name(role_name):
    """Return a normalized role name for comparisons."""
    if role_name is None:
        return None

    normalized = role_name.strip().lower()
    return normalized or None


def get_user_role_name(user):
    """Return the current user's role in normalized form."""
    role = getattr(user, "role", None)
    return normalize_role_name(getattr(role, "role_name", None))


def find_role_by_name(role_name):
    """Find a role by name without depending on letter case."""
    from app.models import Role

    normalized = normalize_role_name(role_name)
    if not normalized:
        return None

    return Role.query.filter(func.lower(Role.role_name) == normalized).first()


def sync_model_sequence(model):
    """Align a PostgreSQL sequence with the current max primary key."""
    primary_key = model.__mapper__.primary_key[0]
    table_name = model.__table__.name

    sequence_name = db.session.execute(
        text("SELECT pg_get_serial_sequence(:table_name, :column_name)"),
        {
            "table_name": table_name,
            "column_name": primary_key.name,
        },
    ).scalar()

    if not sequence_name:
        return

    max_id = db.session.query(func.max(primary_key)).scalar() or 0
    if max_id == 0:
        db.session.execute(
            text("SELECT setval(CAST(:sequence_name AS regclass), 1, false)"),
            {"sequence_name": sequence_name},
        )
        return

    db.session.execute(
        text("SELECT setval(CAST(:sequence_name AS regclass), :current_value, true)"),
        {
            "sequence_name": sequence_name,
            "current_value": max_id,
        },
    )
