import json
import sys
from pathlib import Path
import requests

from config import API_URL, CHANNEL


BASE_DIR = Path(__file__).resolve().parent
POSTS_FILE = BASE_DIR / "posts.json"
PUBLISHED_FILE = BASE_DIR / "published.json"


def load_json(path, default):
    try:
        if not path.exists():
            return default

        text = path.read_text(encoding="utf-8-sig")

        if not text.strip():
            return default

        return json.loads(text)

    except Exception as e:
        print(f"ERROR reading JSON: {path}")
        print(f"DETAIL: {e}")
        sys.exit(1)


def save_json(path, data):
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def telegram_request(method, data=None, files=None):
    url = f"{API_URL}/{method}"

    try:
        response = requests.post(
            url,
            data=data,
            files=files,
            timeout=60
        )

    except requests.RequestException as e:
        print(f"Telegram connection error: {e}")
        return None

    try:
        result = response.json()

    except ValueError:
        print("Telegram returned an invalid response.")
        print(response.text)
        return None

    if not result.get("ok"):
        print(
            "Telegram API error:",
            result.get("description", "Unknown error")
        )
        return None

    return result


def test_connection():
    result = telegram_request("getMe")

    if not result:
        return False

    bot = result["result"]

    print()
    print("Telegram connection successful.")
    print(f"Bot name : {bot.get('first_name')}")
    print(f"Username : @{bot.get('username')}")
    print()

    return True


def send_text(text):
    if not text.strip():
        print("ERROR: Empty post.")
        return None

    if len(text) > 4096:
        print(
            f"ERROR: Telegram text limit exceeded "
            f"({len(text)} characters)."
        )
        return None

    return telegram_request(
        "sendMessage",
        data={
            "chat_id": CHANNEL,
            "text": text,
            "disable_web_page_preview": "false"
        }
    )


def send_photo(image_path, caption):
    if len(caption) > 1024:
        print(
            f"ERROR: Telegram photo caption limit exceeded "
            f"({len(caption)} characters)."
        )
        return None

    image_path = Path(image_path)

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return None

    try:
        with open(image_path, "rb") as photo:
            return telegram_request(
                "sendPhoto",
                data={
                    "chat_id": CHANNEL,
                    "caption": caption
                },
                files={
                    "photo": photo
                }
            )

    except OSError as e:
        print(f"Could not open image: {e}")
        return None


def publish_post(post):
    post_id = str(post.get("id", "")).strip()
    text = post.get("text", "").strip()
    image = post.get("image", "").strip()

    if not post_id:
        print("ERROR: Post has no ID.")
        return False

    if not text:
        print(f"ERROR: Post {post_id} has no text.")
        return False

    print()
    print("=" * 60)
    print(f"Publishing post: {post_id}")
    print("=" * 60)

    if image:
        result = send_photo(
            BASE_DIR / image,
            text
        )
    else:
        result = send_text(text)

    if not result:
        print("POST FAILED")
        return False

    message = result.get("result", {})

    print()
    print("POST PUBLISHED")
    print(
        f"Telegram message ID: "
        f"{message.get('message_id')}"
    )

    return True


def get_next_post():
    posts = load_json(
        POSTS_FILE,
        []
    )

    published = load_json(
        PUBLISHED_FILE,
        []
    )

    published_ids = {
        str(item.get("id"))
        for item in published
    }

    for post in posts:
        post_id = str(post.get("id", "")).strip()

        if post_id and post_id not in published_ids:
            return post

    return None


def mark_published(post):
    published = load_json(
        PUBLISHED_FILE,
        []
    )

    published.append({
        "id": str(post["id"])
    })

    save_json(
        PUBLISHED_FILE,
        published
    )


def publish_next():
    post = get_next_post()

    if not post:
        print()
        print("No unpublished posts available.")
        print("Add new content to posts.json.")
        print()
        return False

    success = publish_post(post)

    if success:
        mark_published(post)

        print()
        print(
            f"Post {post['id']} marked as published."
        )
        print()

        return True

    return False


def status():
    posts = load_json(
        POSTS_FILE,
        []
    )

    published = load_json(
        PUBLISHED_FILE,
        []
    )

    published_ids = {
        str(item.get("id"))
        for item in published
    }

    total = len(posts)

    done = len([
        p for p in posts
        if str(p.get("id")) in published_ids
    ])

    remaining = total - done

    print()
    print("Rise&Lead Telegram Publisher")
    print("-" * 40)
    print(f"Total posts : {total}")
    print(f"Published   : {done}")
    print(f"Remaining   : {remaining}")
    print()


def reset():
    save_json(
        PUBLISHED_FILE,
        []
    )

    print()
    print("Published history has been reset.")
    print()


def show_help():
    print()
    print("Rise&Lead Telegram Publisher")
    print()
    print("Commands:")
    print()
    print("  python main.py test")
    print("      Test Telegram bot connection")
    print()
    print("  python main.py status")
    print("      Show publishing queue")
    print()
    print("  python main.py publish")
    print("      Publish next unpublished post")
    print()
    print("  python main.py reset")
    print("      Reset publishing history")
    print()


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "test":
        test_connection()

    elif command == "status":
        status()

    elif command == "publish":
        publish_next()

    elif command == "reset":
        reset()

    else:
        show_help()


if __name__ == "__main__":
    main()
