import logging
import logging.config
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Папка для логов
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "encoding": "utf-8",
        },
    },

    "loggers": {
        "": {  # root-логгер
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "sqlalchemy.engine": {  # Лог SQLAlchemy
            "handlers": ["console", "file"],
            "level": "INFO",  # поменяй на DEBUG если хочешь видеть все запросы
            "propagate": False,
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

setup_logging()
logger = logging.getLogger(__name__)

# Подключение SQLAlchemy
engine = create_engine(
    "postgresql+psycopg2://market_user:password@62.60.216.29:5432/marketplace",
    echo=False  # echo=True, если хочешь видеть SQL сразу в stdout
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger.info("База данных подключена")