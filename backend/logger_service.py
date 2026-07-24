import logging
import database
from models import SystemLog
import datetime

logger = logging.getLogger("jarvis")
logger.setLevel(logging.INFO)

# Setup handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def log_event(module: str, message: str, level: str = "INFO"):
    logger.info(f"[{module}] {message}")
    db = database.SessionLocal()
    try:
        log_entry = SystemLog(
            level=level,
            module=module,
            message=message,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log event to database: {e}")
    finally:
        db.close()
