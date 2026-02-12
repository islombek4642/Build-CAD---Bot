import uuid
from datetime import datetime
from pathlib import Path
from config.settings import OUTPUT_DIR, FILENAME_PREFIX


def unique_name(ext: str, prefix: str = FILENAME_PREFIX) -> Path:
    stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    uid = uuid.uuid4().hex[:8]
    name = f"{prefix}_{stamp}_{uid}.{ext}"
    return OUTPUT_DIR / name
