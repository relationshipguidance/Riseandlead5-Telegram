import json
import sys
import requests
from datetime import datetime, date
from pathlib import Path

from config import BOT_TOKEN, CHANNEL


# ============================================================
# RISE&LEAD TELEGRAM NATIVE CONTENT ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "telegram_native_history.json"

DAILY_POST_TARGET = 5

# Local India-time publishing slots
SLOTS = [
    ("08:00", "morning_insight"),
    ("11:00", "framework"),
    ("14:00", "executive_perspective"),
    ("17:30", "workplace_reality"),
    ("20:30", "question"),
]

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ============================================================
# CONTENT BANK
# ============================================================

CONTENT_BANK = [

    {
        "topic": "executive_presence",
        "pillar": "Leadership",
        "hook": "EXECUTIVE PRESENCE IS NOT ABOUT SPEAKING MORE.",
        "insight": "It is about increasing the quality of your judgment, communication and composure when the stakes are high.",
        "framework": [
            "Speak to the decision, not every detail.",
            "Make your position clear.",
            "Stay composed when challenged."
        ],
        "takeaway": "People notice how you think under pressure long before they remember how much you spoke.",
        "question": "When you are in a high-stakes conversation, what do people experience first: your clarity, your confidence or your uncertainty?"
    },

    {
        "topic": "recognition",
        "pillar": "Career",
        "hook": "BEING VALUED AND BEING RECOGNISED ARE NOT ALWAYS THE SAME THING.",
        "insight": "Strong work can remain invisible when its business significance is not understood by the people making career decisions.",
        "framework": [
            "Connect your work to business outcomes.",
            "Communicate impact without exaggeration.",
            "Build visibility beyond your immediate circle."
        ],
        "takeaway": "Your contribution needs to be valuable — and legible.",
        "question": "What part of your contribution is valuable but still poorly understood by decision-makers?"
    },

    {
        "topic": "decision_quality",
        "pillar": "Leadership",
        "hook": "SENIOR LEADERS ARE OFTEN PAID FOR THE DECISIONS THEY DON'T DELAY.",
        "insight": "Perfect information rarely arrives before an important decision.",
        "framework": [
            "Separate signal from noise.",
            "Make the trade-offs explicit.",
            "Decide with the information available now."
        ],
        "takeaway": "Decision quality is not the absence of uncertainty. It is the ability to create direction despite it.",
        "question": "Where are you waiting for certainty when what the situation actually requires is judgment?"
    },

    {
        "topic": "career_positioning",
        "pillar": "Career",
        "hook": "YOUR NEXT ROLE IS OFTEN DECIDED BEFORE THE JOB TITLE CHANGES.",
        "insight": "People begin to see you differently when your scope, judgment and influence consistently operate at the next level.",
        "framework": [
            "Think beyond your current responsibilities.",
            "Solve problems with enterprise impact.",
            "Build relationships before you need them."
        ],
        "takeaway": "Career progression starts with how you operate, not just what title you hold.",
        "question": "If your role changed tomorrow, what capability would you need to demonstrate immediately?"
    },

    {
        "topic": "strategic_thinking",
        "pillar": "Leadership",
        "hook": "STRATEGIC THINKING IS NOT THINKING BIGGER. IT IS SEEING FURTHER.",
        "insight": "Strategy requires understanding consequences, dependencies and trade-offs before acting.",
        "framework": [
            "Look beyond the immediate problem.",
            "Identify second-order consequences.",
            "Connect decisions to the larger business context."
        ],
        "takeaway": "A strategic leader sees what today's decision creates tomorrow.",
        "question": "What consequence of a current decision are you not yet discussing?"
    },

    {
        "topic": "visibility",
        "pillar": "Career",
        "hook": "VISIBILITY IS NOT SELF-PROMOTION.",
        "insight": "Professional visibility is the ability to make your thinking, contribution and impact discoverable to the right people.",
        "framework": [
            "Share useful thinking.",
            "Make outcomes visible.",
            "Contribute beyond your immediate team."
        ],
        "takeaway": "You do not need to talk about yourself more. You need your contribution to become easier to understand.",
        "question": "Who outside your immediate team understands the value you create?"
    },

    {
        "topic": "accountability",
        "pillar": "Leadership",
        "hook": "ACCOUNTABILITY CHANGES WHEN YOU STOP EXPLAINING AND START OWNING.",
        "insight": "Senior leadership requires ownership even when the circumstances are imperfect.",
        "framework": [
            "State what happened clearly.",
            "Own your part without defensiveness.",
            "Move quickly toward the next action."
        ],
        "takeaway": "Ownership creates trust faster than a perfect explanation.",
        "question": "When something goes wrong, does your first instinct explain the situation or own the response?"
    },

    {
        "topic": "difficult_conversations",
        "pillar": "Leadership",
        "hook": "DIFFICULT CONVERSATIONS BECOME HARDER WHEN THE MESSAGE IS UNCLEAR.",
        "insight": "Avoidance often creates more damage than a direct, respectful conversation.",
        "framework": [
            "State the issue.",
            "Explain the impact.",
            "Agree on the next action."
        ],
        "takeaway": "Clarity is often more respectful than prolonged ambiguity.",
        "question": "What conversation are you postponing because you are trying to make it comfortable?"
    },

    {
        "topic": "confidence",
        "pillar": "Mindset",
        "hook": "CONFIDENCE IS NOT THE ABSENCE OF DOUBT.",
        "insight": "Confidence becomes stronger when you learn to act without requiring complete emotional certainty first.",
        "framework": [
            "Accept uncertainty.",
            "Trust preparation.",
            "Take the next deliberate action."
        ],
        "takeaway": "You do not need to feel completely ready to behave deliberately.",
        "question": "Where are you waiting to feel confident before taking an action you already know is necessary?"
    },

    {
        "topic": "self_command",
        "pillar": "Mindset",
        "hook": "SELF-COMMAND COMES BEFORE LEADERSHIP COMMAND.",
        "insight": "Your ability to regulate attention, emotion and behaviour determines how consistently you can lead others.",
        "framework": [
            "Notice the reaction.",
            "Create a pause.",
            "Choose the response."
        ],
        "takeaway": "Leadership begins with the ability to govern yourself.",
        "question": "What reaction do you need to become better at managing?"
    },

    {
        "topic": "promotion_readiness",
        "pillar": "Career",
        "hook": "A PROMOTION IS NOT JUST A REWARD FOR PAST PERFORMANCE.",
        "insight": "At senior levels, organisations also look for evidence that someone can operate successfully at greater scope.",
        "framework": [
            "Demonstrate broader judgment.",
            "Take ownership beyond your role.",
            "Build trust across stakeholders."
        ],
        "takeaway": "The strongest promotion signal is evidence of next-level behaviour before the title changes.",
        "question": "What next-level behaviour are you already demonstrating consistently?"
    },

    {
        "topic": "influence",
        "pillar": "Leadership",
        "hook": "INFLUENCE IS NOT ABOUT WINNING EVERY ARGUMENT.",
        "insight": "Influence is the ability to move people toward useful action while understanding their interests and concerns.",
        "framework": [
            "Understand what matters to others.",
            "Frame the issue around outcomes.",
            "Create a path to action."
        ],
        "takeaway": "Influence grows when people can see both the logic and the relevance of your position.",
        "question": "When someone disagrees with you, do you try to prove your point or understand what is driving theirs?"
    },

    {
        "topic": "workplace_reality",
        "pillar": "Workplace Reality",
        "hook": "WORKPLACE PERFORMANCE AND CAREER PROGRESSION ARE NOT ALWAYS THE SAME THING.",
        "insight": "Strong execution matters, but senior progression also depends on visibility, judgment, relationships and perceived scope.",
        "framework": [
            "Deliver reliably.",
            "Understand the organisational context.",
            "Build strategic visibility."
        ],
        "takeaway": "Doing excellent work is essential. Understanding how careers actually move is also essential.",
        "question": "Which part of career progression receives the least attention in your current role?"
    },

    {
        "topic": "leadership_identity",
        "pillar": "Mindset",
        "hook": "THE ROLE CHANGES FASTER THAN THE IDENTITY.",
        "insight": "Moving into a larger role often requires changing how you see responsibility, authority and decision-making.",
        "framework": [
            "Stop waiting for permission.",
            "Think beyond your individual output.",
            "Accept broader accountability."
        ],
        "takeaway": "A bigger role requires a bigger internal operating model.",
        "question": "What part of your current identity may be limiting your next level?"
    },

    {
        "topic": "communication",
        "pillar": "Leadership",
        "hook": "CLEAR COMMUNICATION REDUCES THE COST OF LEADERSHIP.",
        "insight": "Ambiguity creates repeated conversations, conflicting interpretations and slow decisions.",
        "framework": [
            "State the objective.",
            "Clarify ownership.",
            "Define the next decision."
        ],
        "takeaway": "Clarity is not more communication. It is better communication.",
        "question": "Where could one clearer conversation eliminate several future conversations?"
    },

    {
        "topic": "career_transition",
        "pillar": "Career",
        "hook": "A CAREER TRANSITION IS NOT JUST A JOB SEARCH.",
        "insight": "Senior transitions require a clear professional narrative, relevant relationships and evidence of the value you bring next.",
        "framework": [
            "Define the role you are moving toward.",
            "Translate your experience into future value.",
            "Build relationships before asking for opportunities."
        ],
        "takeaway": "The market needs to understand not only what you have done, but what you are positioned to do next.",
        "question": "Can you explain the value of your next career move in one clear sentence?"
    },

    {
        "topic": "focus",
        "pillar": "Mindset",
        "hook": "BUSY IS NOT THE SAME AS EFFECTIVE.",
        "insight": "Senior professionals can become trapped in activity because activity creates the feeling of progress.",
        "framework": [
            "Identify the highest-value outcome.",
            "Remove low-value activity.",
            "Protect time for important thinking."
        ],
        "takeaway": "Progress requires prioritisation, not simply more effort.",
        "question": "What are you doing regularly that creates activity but little strategic value?"
    },

    {
        "topic": "stakeholder_management",
        "pillar": "Leadership",
        "hook": "STAKEHOLDER MANAGEMENT STARTS BEFORE THE MEETING.",
        "insight": "Influence improves when you understand stakeholders' interests, concerns and decision criteria before asking them to support something.",
        "framework": [
            "Know who matters.",
            "Understand what matters to them.",
            "Anticipate objections before the conversation."
        ],
        "takeaway": "Preparation for people is as important as preparation for the proposal.",
        "question": "Which stakeholder's perspective are you currently underestimating?"
    },

    {
        "topic": "professional_reputation",
        "pillar": "Career",
        "hook": "YOUR PROFESSIONAL REPUTATION IS BUILT WHEN YOU ARE NOT IN THE ROOM.",
        "insight": "People form opinions from patterns: how you decide, respond, communicate and deliver over time.",
        "framework": [
            "Be consistent.",
            "Keep commitments.",
            "Make your judgment visible through actions."
        ],
        "takeaway": "Reputation is accumulated evidence.",
        "question": "What three words would your key stakeholders use to describe how you operate?"
    },

    {
        "topic": "resilience",
        "pillar": "Mindset",
        "hook": "RESILIENCE IS NOT ABOUT NEVER BEING AFFECTED.",
        "insight": "Resilience is the capacity to recover perspective and continue acting deliberately when circumstances become difficult.",
        "framework": [
            "Acknowledge what happened.",
            "Separate facts from reaction.",
            "Decide what deserves your energy next."
        ],
        "takeaway": "You cannot control every situation. You can improve the quality of your response.",
        "question": "What situation currently deserves a calmer response rather than a stronger reaction?"
    }
]


# ============================================================
# HISTORY
# ============================================================

def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        return json.loads(
            HISTORY_FILE.read_text(encoding="utf-8-sig")
        )
    except Exception:
        return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ============================================================
# TELEGRAM
# ============================================================

def telegram_request(method, data=None):
    response = requests.post(
        f"{API_URL}/{method}",
        data=data or {},
        timeout=60
    )

    try:
        result = response.json()
    except Exception:
        print(response.text)
        return None

    if not result.get("ok"):
        print("Telegram error:", result.get("description"))
        return None

    return result


def test_bot():
    result = telegram_request("getMe")

    if not result:
        return False

    bot = result["result"]

    print("Telegram connection successful.")
    print(f"Bot      : {bot.get('first_name')}")
    print(f"Username : @{bot.get('username')}")
    print(f"Channel  : {CHANNEL}")

    return True


def send_message(text):
    result = telegram_request(
        "sendMessage",
        {
            "chat_id": CHANNEL,
            "text": text,
            "disable_web_page_preview": True
        }
    )

    return result


def send_poll(question, options):
    return telegram_request(
        "sendPoll",
        {
            "chat_id": CHANNEL,
            "question": question[:300],
            "options": json.dumps(options),
            "is_anonymous": "true",
            "allows_multiple_answers": "false"
        }
    )


# ============================================================
# CONTENT GENERATION
# ============================================================

def choose_topic(day_index):
    return CONTENT_BANK[day_index % len(CONTENT_BANK)]


def build_post(topic, slot_name, day_index):

    if slot_name == "morning_insight":
        return {
            "format": "insight",
            "text": (
                f"{topic['hook']}\n\n"
                f"{topic['insight']}\n\n"
                f"THE RISE&LEAD TAKE\n\n"
                f"{topic['takeaway']}\n\n"
                f"— Rise&Lead"
            )
        }

    if slot_name == "framework":
        points = "\n".join(
            f"{i + 1}. {item}"
            for i, item in enumerate(topic["framework"])
        )

        return {
            "format": "framework",
            "text": (
                f"{topic['pillar'].upper()} FRAMEWORK\n\n"
                f"{topic['hook']}\n\n"
                f"{points}\n\n"
                f"Use this when the situation requires better judgment, "
                f"clearer action or stronger leadership.\n\n"
                f"— Rise&Lead"
            )
        }

    if slot_name == "executive_perspective":
        return {
            "format": "perspective",
            "text": (
                f"EXECUTIVE PERSPECTIVE\n\n"
                f"{topic['hook']}\n\n"
                f"{topic['insight']}\n\n"
                f"The practical question is not whether the situation "
                f"is difficult.\n\n"
                f"The question is whether your response is operating "
                f"at the level the situation requires.\n\n"
                f"— Rise&Lead"
            )
        }

    if slot_name == "workplace_reality":
        return {
            "format": "workplace",
            "text": (
                f"WORKPLACE REALITY\n\n"
                f"{topic['takeaway']}\n\n"
                f"Three things to examine:\n\n"
                f"• What are you currently rewarded for?\n"
                f"• What does the next level require?\n"
                f"• What behaviour needs to change before the title does?\n\n"
                f"— Rise&Lead"
            )
        }

    return {
        "format": "question",
        "text": (
            f"RISE&LEAD QUESTION\n\n"
            f"{topic['question']}\n\n"
            f"Take a minute before answering.\n"
            f"The quality of the question often determines "
            f"the quality of the decision that follows.\n\n"
            f"— Rise&Lead"
        )
    }


# ============================================================
# POLL
# ============================================================

def build_poll(topic):
    return {
        "question": topic["question"],
        "options": [
            "Clarity",
            "Confidence",
            "Visibility",
            "Execution"
        ]
    }


# ============================================================
# DAILY SCHEDULING
# ============================================================

def today_string():
    return date.today().isoformat()


def get_day_index():
    start = date(2026, 9, 25)
    return (date.today() - start).days


def published_keys(history):
    return {
        item.get("key")
        for item in history
    }


def publish_slot(slot_index):
    history = load_history()

    now = datetime.now()
    today = today_string()

    slot_time, slot_name = SLOTS[slot_index]
    key = f"{today}_{slot_name}"

    if key in published_keys(history):
        print(f"Already published: {key}")
        return False

    day_index = get_day_index()

    topic = choose_topic(day_index)
    generated = build_post(topic, slot_name, day_index)

    print()
    print("=" * 60)
    print("RISE&LEAD TELEGRAM")
    print("=" * 60)
    print(f"Date    : {today}")
    print(f"Slot    : {slot_time}")
    print(f"Format  : {generated['format']}")
    print(f"Topic   : {topic['topic']}")
    print()

    if generated["format"] == "question":
        poll = build_poll(topic)

        result = send_poll(
            poll["question"],
            poll["options"]
        )

        if not result:
            return False

        message_id = result["result"].get("message_id")

    else:
        result = send_message(generated["text"])

        if not result:
            return False

        message_id = result["result"].get("message_id")

    history.append({
        "key": key,
        "date": today,
        "slot": slot_time,
        "format": generated["format"],
        "topic": topic["topic"],
        "pillar": topic["pillar"],
        "message_id": message_id,
        "published_at": now.isoformat()
    })

    save_history(history)

    print(f"Published successfully.")
    print(f"Telegram message ID: {message_id}")

    return True


def publish_all_today():
    history = load_history()
    today = today_string()

    existing = {
        item.get("key")
        for item in history
        if item.get("date") == today
    }

    published = 0

    for index, (slot_time, slot_name) in enumerate(SLOTS):

        key = f"{today}_{slot_name}"

        if key in existing:
            continue

        if publish_slot(index):
            published += 1

    print()
    print(f"Today's new posts published: {published}")


def run_due():

    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute

    due = []

    for index, (slot_time, _) in enumerate(SLOTS):

        hour, minute = map(int, slot_time.split(":"))
        slot_minutes = hour * 60 + minute

        if current_minutes >= slot_minutes:
            due.append(index)

    if not due:
        print("No Telegram slot is due yet.")
        return

    history = load_history()
    today = today_string()

    for index in due:
        slot_time, slot_name = SLOTS[index]
        key = f"{today}_{slot_name}"

        if not any(x.get("key") == key for x in history):
            publish_slot(index)
            break

    else:
        print("All currently due slots are already published.")


# ============================================================
# STATUS
# ============================================================

def status():

    history = load_history()
    today = today_string()

    today_posts = [
        item for item in history
        if item.get("date") == today
    ]

    print()
    print("Rise&Lead Telegram Native Engine")
    print("-" * 45)
    print(f"Channel             : {CHANNEL}")
    print(f"Daily target        : {DAILY_POST_TARGET}")
    print(f"Content topics      : {len(CONTENT_BANK)}")
    print(f"Total published     : {len(history)}")
    print(f"Published today     : {len(today_posts)}")
    print(f"Remaining today     : {max(0, DAILY_POST_TARGET - len(today_posts))}")
    print()

    for slot_time, slot_name in SLOTS:
        key = f"{today}_{slot_name}"

        done = any(
            item.get("key") == key
            for item in history
        )

        print(
            f"{slot_time}  "
            f"{'PUBLISHED' if done else 'PENDING'}  "
            f"{slot_name}"
        )

    print()


def reset_today():

    history = load_history()
    today = today_string()

    history = [
        item for item in history
        if item.get("date") != today
    ]

    save_history(history)

    print(f"Today's Telegram publishing history reset: {today}")


# ============================================================
# MAIN
# ============================================================

def main():

    command = (
        sys.argv[1].lower()
        if len(sys.argv) > 1
        else "status"
    )

    if command == "test":
        test_bot()

    elif command == "status":
        status()

    elif command == "publish":
        publish_slot(0)

    elif command == "publish-all":
        publish_all_today()

    elif command == "run":
        run_due()

    elif command == "reset-today":
        reset_today()

    else:
        print()
        print("Rise&Lead Telegram Native Engine")
        print()
        print("Commands:")
        print("  python main.py test")
        print("  python main.py status")
        print("  python main.py publish")
        print("  python main.py publish-all")
        print("  python main.py run")
        print("  python main.py reset-today")
        print()


if __name__ == "__main__":
    main()
