import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


# Load .env for local Windows execution.
# GitHub Actions supplies these values through environment variables.
if load_dotenv:
    load_dotenv(ENV_FILE)


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHANNEL = os.getenv("TELEGRAM_CHANNEL", "").strip()


if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is not set. "
        "Set it in .env locally or GitHub Actions Secrets."
    )


if not CHANNEL:
    raise RuntimeError(
        "TELEGRAM_CHANNEL is not set. "
        "Set it in .env locally or GitHub Actions Secrets."
    )


API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


print("Config loaded successfully.")
print(f"Bot token: FOUND ({len(BOT_TOKEN)} characters)")
print(f"Channel: {CHANNEL}")
