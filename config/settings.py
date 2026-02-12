from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', BASE_DIR / 'output'))

# AI provider selection (mock | groq | other)
AI_PROVIDER = os.getenv('AI_PROVIDER', 'mock')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_ENDPOINT = os.getenv('AI_ENDPOINT', '')

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Defaults and constants
DEFAULT_TOTAL_AREA = 100.0
DEFAULT_FLOOR_COUNT = 1
DEFAULT_ROOM_COUNT = 1
DEFAULT_ENTRANCE = 'south'
DEFAULT_WALLS_THICKNESS = 0.3

# Filenames
FILENAME_PREFIX = 'plan'

# Schema definition constants
ROOM_TYPES = ['bedroom', 'living_room', 'kitchen', 'bathroom', 'hall', 'stairs', 'basement', 'terrace', 'balcony', 'other']

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
