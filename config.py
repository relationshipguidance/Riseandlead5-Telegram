from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def read_env_file(path):
    values = {}

    if not path.exists():
        raise RuntimeError(f".env file not found: {path}")

    for raw_line in path.read_text(
        encoding="utf-8-sig"
    ).splitlines():

        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip()

        # Remove optional surrounding quotes
        if len(value) >= 2:
            if (
                (value.startswith('"') and value.endswith('"'))
                or
                (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]

        values[key] = value

    return values


ENV = read_env_file(ENV_FILE)

BOT_TOKEN = ENV.get("TELEGRAM_BOT_TOKEN", "").strip()
CHANNEL = ENV.get("TELEGRAM_CHANNEL", "").strip()


if not BOT_TOKEN:
    raise RuntimeError(
        f"TELEGRAM_BOT_TOKEN is empty in {ENV_FILE}"
    )


if not CHANNEL:
    raise RuntimeError(
        f"TELEGRAM_CHANNEL is empty in {ENV_FILE}"
    )


API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


print(f"Config loaded: {ENV_FILE}")
print(f"Bot token: FOUND ({len(BOT_TOKEN)} characters)")
print(f"Channel: {CHANNEL}")
