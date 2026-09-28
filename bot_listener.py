import json
import time
import requests

from config import API_URL, CHANNEL


JOIN_URL = "https://t.me/riseandlead5"
WEBSITE_URL = "https://riseandlead.pythonanywhere.com"


def telegram_request(method, data=None, timeout=60):
    try:
        response = requests.post(
            f"{API_URL}/{method}",
            data=data or {},
            timeout=timeout
        )

        result = response.json()

        if not result.get("ok"):
            print("Telegram error:", result.get("description"))
            return None

        return result

    except Exception as e:
        print("Request error:", e)
        return None


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    return telegram_request("sendMessage", data)


def answer_callback(callback_id, text=None):
    data = {
        "callback_query_id": callback_id
    }

    if text:
        data["text"] = text

    return telegram_request("answerCallbackQuery", data)


def check_membership(user_id):
    result = telegram_request(
        "getChatMember",
        {
            "chat_id": CHANNEL,
            "user_id": user_id
        }
    )

    if not result:
        return False

    member = result.get("result", {})
    status = member.get("status")

    return status in ["member", "administrator", "creator"]


def send_join_message(chat_id):
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Join Rise&Lead",
                    "url": JOIN_URL
                }
            ],
            [
                {
                    "text": "I've Joined",
                    "callback_data": "check_join"
                }
            ]
        ]
    }

    text = (
        "Welcome to Rise&Lead!\n\n"
        "Leadership. Career Growth. Mindset.\n\n"
        "Practical insights for professionals and leaders "
        "who want to think bigger, lead better and grow "
        "with intention.\n\n"
        "Inside our Telegram channel you'll get:\n"
        "- Leadership insights\n"
        "- Career growth strategies\n"
        "- Mindset perspectives\n"
        "- Workplace lessons\n"
        "- Rise&Lead updates\n\n"
        "Join the channel below.\n"
        "After joining, tap \"I've Joined\"."
    )

    send_message(
        chat_id,
        text,
        keyboard
    )


def handle_update(update):
    message = update.get("message")

    if message:
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text.startswith("/start") and chat_id:
            send_join_message(chat_id)
            return

    callback = update.get("callback_query")

    if callback:
        callback_id = callback.get("id")
        user = callback.get("from", {})
        user_id = user.get("id")
        chat_id = callback.get("message", {}).get("chat", {}).get("id")

        if callback.get("data") == "check_join":
            answer_callback(
                callback_id,
                "Checking your membership..."
            )

            if check_membership(user_id):
                welcome_keyboard = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Explore Rise&Lead",
                                "url": WEBSITE_URL
                            }
                        ]
                    ]
                }

                send_message(
                    chat_id,
                    "You're in!\n\n"
                    "Welcome to the Rise&Lead community.\n\n"
                    "Follow the channel for leadership, career "
                    "and mindset insights designed for professionals "
                    "and leaders.",
                    welcome_keyboard
                )

            else:
                send_message(
                    chat_id,
                    "It looks like you haven't joined the channel yet.\n\n"
                    "Please tap \"Join Rise&Lead\", join the channel, "
                    "and then tap \"I've Joined\"."
                )


def run():
    print()
    print("=" * 60)
    print("Rise&Lead Telegram Join Bot")
    print("=" * 60)
    print(f"Channel: {CHANNEL}")
    print()

    result = telegram_request("getMe")

    if not result:
        print("Could not connect to Telegram.")
        return

    bot = result["result"]

    print(f"Bot: @{bot.get('username')}")
    print("Bot connection successful.")
    print()

    webhook = telegram_request("getWebhookInfo")

    if webhook:
        webhook_url = webhook.get("result", {}).get("url", "")

        if webhook_url:
            print("Webhook detected:")
            print(webhook_url)
            print()
            print("Removing webhook so polling can start...")

            telegram_request(
                "deleteWebhook",
                {"drop_pending_updates": "false"}
            )

            print("Webhook removed.")
            print()

    offset = None

    print("Listening for users...")
    print("Press CTRL+C to stop.")
    print()

    while True:
        try:
            data = {
                "timeout": 50,
                "allowed_updates": json.dumps(
                    ["message", "callback_query"]
                )
            }

            if offset is not None:
                data["offset"] = offset

            result = telegram_request(
                "getUpdates",
                data,
                timeout=60
            )

            if not result:
                time.sleep(3)
                continue

            updates = result.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                try:
                    handle_update(update)
                except Exception as e:
                    print("Update error:", e)

        except KeyboardInterrupt:
            print()
            print("Bot stopped.")
            break

        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
