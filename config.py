from dotenv import load_dotenv
import os

load_dotenv()


def _normalize_database_uri(uri: str | None) -> str | None:
    if not uri:
        return uri

    # requirements.txt installs psycopg2-binary, so fall back to it when
    # the newer psycopg driver is referenced in .env but not installed.
    if uri.startswith("postgresql+psycopg://"):
        try:
            import psycopg  # type: ignore  # noqa: F401
        except ModuleNotFoundError:
            return uri.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)

    return uri

class Config():
    SQLALCHEMY_DATABASE_URI=_normalize_database_uri(os.getenv('SQLALCHEMY_DATABASE_URI'))
    SQLALCHEMY_TRACK_MODIFICATIONS=os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY=os.getenv('SECRET_KEY')
