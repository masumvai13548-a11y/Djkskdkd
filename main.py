"""
Single-file Telegram bot: Valyrian-style UI + safe admin/user management.

Removed from the original source:
- external card-checking/payment gateways
- card/credential processing
- proxy execution for checking
- external checker API calls

Kept here:
- Telethon bot structure
- API_ID / API_HASH / BOT_TOKEN configuration
- ADMIN_ID support
- premium users
- banned users
- admin management commands
- Valyrian-style menu/navigation
- Railway-friendly single-file entry point
"""

import os
import json
import random
import string
import datetime
from telethon import TelegramClient, events, Button


# ============================================================
# CONFIG
# ============================================================

API_ID = int(os.getenv("API_ID", "30424087"))
API_HASH = os.getenv("API_HASH", "793db34ba0138f1c174434616a681574")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8966483289:AAGgImBEUgc2XPdQEADHy0a_B7eHdQ9UIQk")
ADMIN_ID = {
    int(x.strip())
    for x in os.getenv("ADMIN_ID", "6904041366").split(",")
    if x.strip().isdigit()
}

BOT_NAME = "VALYRIAN"

PREMIUM_FILE = "premium.json"
BANNED_FILE = "banned_users.json"
USERS_FILE = "users.json"
KEYS_FILE = "keys.json"


# ============================================================
# JSON STORAGE
# ============================================================

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_files():
    for filename in (PREMIUM_FILE, BANNED_FILE, USERS_FILE, KEYS_FILE):
        if not os.path.exists(filename):
            save_json(filename, {})


# ============================================================
# ADMIN / USER MANAGEMENT
# ============================================================

def is_admin(user_id):
    return int(user_id) in ADMIN_ID


def is_banned(user_id):
    return str(user_id) in load_json(BANNED_FILE)


def ban_user(user_id, banned_by):
    data = load_json(BANNED_FILE)
    data[str(user_id)] = {
        "banned_at": datetime.datetime.now().isoformat(),
        "banned_by": int(banned_by),
    }
    save_json(BANNED_FILE, data)


def unban_user(user_id):
    data = load_json(BANNED_FILE)
    removed = data.pop(str(user_id), None) is not None
    save_json(BANNED_FILE, data)
    return removed


def add_premium(user_id, days, added_by):
    data = load_json(PREMIUM_FILE)
    expiry = datetime.datetime.now() + datetime.timedelta(days=int(days))
    data[str(user_id)] = {
        "expiry": expiry.isoformat(),
        "days": int(days),
        "added_by": int(added_by),
    }
    save_json(PREMIUM_FILE, data)


def remove_premium(user_id):
    data = load_json(PREMIUM_FILE)
    removed = data.pop(str(user_id), None) is not None
    save_json(PREMIUM_FILE, data)
    return removed


def is_premium(user_id):
    data = load_json(PREMIUM_FILE)
    item = data.get(str(user_id))
    if not item:
        return False

    try:
        expiry = datetime.datetime.fromisoformat(item["expiry"])
    except (KeyError, ValueError):
        return False

    if datetime.datetime.now() >= expiry:
        data.pop(str(user_id), None)
        save_json(PREMIUM_FILE, data)
        return False

    return True


def register_user(user):
    data = load_json(USERS_FILE)
    uid = str(user.id)

    if uid not in data:
        data[uid] = {
            "id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "joined_at": datetime.datetime.now().isoformat(),
        }
        save_json(USERS_FILE, data)


def generate_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def create_premium_key(days):
    keys = load_json(KEYS_FILE)
    key = generate_key()
    keys[key] = {
        "days": int(days),
        "used": False,
        "created_at": datetime.datetime.now().isoformat(),
    }
    save_json(KEYS_FILE, keys)
    return key


def redeem_key(user_id, key):
    keys = load_json(KEYS_FILE)
    item = keys.get(key)

    if not item or item.get("used"):
        return False, "Invalid or already used key."

    add_premium(user_id, int(item["days"]), user_id)
    item["used"] = True
    item["used_by"] = user_id
    item["used_at"] = datetime.datetime.now().isoformat()
    keys[key] = item
    save_json(KEYS_FILE, keys)
    return True, f"Premium activated for {item['days']} days."


# ============================================================
# VALYRIAN UI
# ============================================================

CATEGORIES = {
    "auth": "🔒 Auth Gates",
    "mass": "📊 Mass Checker",
    "shopify": "⚡ Shopify Gates",
    "charge": "💳 Charge Gates",
    "premium": "🎀 Premium Gates",
}

# UI placeholders only. No external checker is connected.
ITEMS = {
    "auth": [
        ("⚡ Auth Gate 1", "/auth1"),
        ("⚡ Auth Gate 2", "/auth2"),
        ("⚡ Auth Gate 3", "/auth3"),
        ("⚡ Auth Gate 4", "/auth4"),
        ("⚡ Auth Gate 5", "/auth5"),
        ("⚡ Auth Gate 6", "/auth6"),
    ],
    "mass": [
        ("⚡ Mass Gate 1", "/mass1"),
        ("⚡ Mass Gate 2", "/mass2"),
        ("⚡ Mass Gate 3", "/mass3"),
        ("⚡ Mass Gate 4", "/mass4"),
    ],
    "shopify": [
        ("⚡ Shopify Gate 1", "/shopify1"),
        ("⚡ Shopify Gate 2", "/shopify2"),
        ("⚡ Shopify Gate 3", "/shopify3"),
        ("⚡ Shopify Gate 4", "/shopify4"),
        ("⚡ Shopify Gate 5", "/shopify5"),
        ("⚡ Shopify Gate 6", "/shopify6"),
    ],
    "charge": [
        ("⚡ Charge Gate 1", "/charge1"),
        ("⚡ Charge Gate 2", "/charge2"),
        ("⚡ Charge Gate 3", "/charge3"),
        ("⚡ Charge Gate 4", "/charge4"),
        ("⚡ Charge Gate 5", "/charge5"),
        ("⚡ Charge Gate 6", "/charge6"),
    ],
    "premium": [
        ("🎀 Premium Gate 1", "/premium1"),
        ("🎀 Premium Gate 2", "/premium2"),
        ("🎀 Premium Gate 3", "/premium3"),
        ("🎀 Premium Gate 4", "/premium4"),
    ],
}


def main_text():
    return (
        f"⚡ <b>{BOT_NAME}</b>\n\n"
        "Welcome to the control panel.\n"
        "Select a category below to continue.\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


def main_buttons():
    return [
        [
            Button.inline("🔒 Auth Gates", b"ui:auth"),
            Button.inline("📊 Mass Checker", b"ui:mass"),
        ],
        [
            Button.inline("⚡ Shopify Gates", b"ui:shopify"),
            Button.inline("💳 Charge Gates", b"ui:charge"),
        ],
        [Button.inline("🎀 Premium Gates", b"ui:premium")],
        [Button.inline("🚫 Close", b"ui:close")],
    ]


def category_text(category, page=1):
    per_page = 4
    items = ITEMS[category]
    total = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total))
    current = items[(page - 1) * per_page: page * per_page]

    lines = [f"⚡ <b>{CATEGORIES[category]}</b>", ""]
    for label, command in current:
        lines += [
            label,
            f"Command: <code>{command}</code>",
            "Status: UI",
            "",
        ]
    lines.append(f"✓ <i>Page {page} of {total}</i>")
    return "\n".join(lines)


def category_buttons(category, page=1):
    per_page = 4
    items = ITEMS[category]
    total = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total))
    current = items[(page - 1) * per_page: page * per_page]

    rows = []
    for i in range(0, len(current), 2):
        rows.append([
            Button.inline(label, data=f"ui:item:{category}:{command}".encode())
            for label, command in current[i:i + 2]
        ])

    nav = []
    if page > 1:
        nav.append(
            Button.inline(
                "◀️ Back",
                data=f"ui:page:{category}:{page - 1}".encode(),
            )
        )
    if page < total:
        nav.append(
            Button.inline(
                "Next ▶️",
                data=f"ui:page:{category}:{page + 1}".encode(),
            )
        )
    if nav:
        rows.append(nav)

    rows.append([
        Button.inline("🔙 Main Menu", b"ui:main"),
        Button.inline("🚫 Close", b"ui:close"),
    ])
    return rows


# ============================================================
# CLIENT
# ============================================================

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError(
        "Set API_ID, API_HASH and BOT_TOKEN as Railway environment variables."
    )

client = TelegramClient("valyrian_bot", API_ID, API_HASH)


# ============================================================
# START / BASIC COMMANDS
# ============================================================

@client.on(events.NewMessage(pattern=r"^/start$"))
async def start_handler(event):
    sender = await event.get_sender()
    register_user(sender)

    if is_banned(sender.id):
        await event.reply("🚫 You are banned from using this bot.")
        return

    await event.reply(
        main_text(),
        buttons=main_buttons(),
        parse_mode="html",
    )


@client.on(events.NewMessage(pattern=r"^/menu$"))
async def menu_handler(event):
    await event.reply(
        main_text(),
        buttons=main_buttons(),
        parse_mode="html",
    )


@client.on(events.NewMessage(pattern=r"^/help$"))
async def help_handler(event):
    await event.reply(
        "📚 <b>Commands</b>\n\n"
        "/start — Open menu\n"
        "/menu — Open menu\n"
        "/info — Your account info\n"
        "/redeem KEY — Redeem premium key\n"
        "/id — Show your Telegram ID\n\n"
        "<b>Admin</b>\n"
        "/addprem ID DAYS\n"
        "/rmprem ID\n"
        "/ban ID\n"
        "/unban ID\n"
        "/genkey DAYS\n"
        "/stats",
        parse_mode="html",
    )


@client.on(events.NewMessage(pattern=r"^/id$"))
async def id_handler(event):
    await event.reply(f"🆔 Your ID: <code>{event.sender_id}</code>", parse_mode="html")


@client.on(events.NewMessage(pattern=r"^/info$"))
async def info_handler(event):
    sender = await event.get_sender()
    register_user(sender)

    premium = "ACTIVE" if is_premium(sender.id) else "FREE"
    await event.reply(
        f"👤 <b>Account</b>\n\n"
        f"ID: <code>{sender.id}</code>\n"
        f"Username: @{sender.username or 'None'}\n"
        f"Plan: <b>{premium}</b>\n"
        f"Admin: {'YES' if is_admin(sender.id) else 'NO'}",
        parse_mode="html",
    )


@client.on(events.NewMessage(pattern=r"^/redeem(?:\s+(.+))?$"))
async def redeem_handler(event):
    key = event.pattern_match.group(1)
    if not key:
        await event.reply("Usage: <code>/redeem KEY</code>", parse_mode="html")
        return

    ok, message = redeem_key(event.sender_id, key.strip())
    await event.reply(("✅ " if ok else "❌ ") + message)


# ============================================================
# ADMIN COMMANDS
# ============================================================

async def require_admin(event):
    if not is_admin(event.sender_id):
        await event.reply("⛔ Admin only.")
        return False
    return True


@client.on(events.NewMessage(pattern=r"^/addprem\s+(\d+)\s+(\d+)$"))
async def addprem_handler(event):
    if not await require_admin(event):
        return

    user_id = int(event.pattern_match.group(1))
    days = int(event.pattern_match.group(2))
    add_premium(user_id, days, event.sender_id)
    await event.reply(f"✅ Premium added: <code>{user_id}</code> for {days} days.", parse_mode="html")


@client.on(events.NewMessage(pattern=r"^/rmprem\s+(\d+)$"))
async def rmprem_handler(event):
    if not await require_admin(event):
        return

    user_id = int(event.pattern_match.group(1))
    ok = remove_premium(user_id)
    await event.reply("✅ Premium removed." if ok else "❌ User has no premium record.")


@client.on(events.NewMessage(pattern=r"^/ban\s+(\d+)$"))
async def ban_handler(event):
    if not await require_admin(event):
        return

    user_id = int(event.pattern_match.group(1))
    ban_user(user_id, event.sender_id)
    await event.reply(f"🚫 Banned <code>{user_id}</code>.", parse_mode="html")


@client.on(events.NewMessage(pattern=r"^/unban\s+(\d+)$"))
async def unban_handler(event):
    if not await require_admin(event):
        return

    user_id = int(event.pattern_match.group(1))
    ok = unban_user(user_id)
    await event.reply("✅ Unbanned." if ok else "❌ User is not banned.")


@client.on(events.NewMessage(pattern=r"^/genkey\s+(\d+)$"))
async def genkey_handler(event):
    if not await require_admin(event):
        return

    days = int(event.pattern_match.group(1))
    key = create_premium_key(days)
    await event.reply(
        f"🔑 Premium key generated:\n\n<code>{key}</code>\n"
        f"Duration: {days} days",
        parse_mode="html",
    )


@client.on(events.NewMessage(pattern=r"^/stats$"))
async def stats_handler(event):
    if not await require_admin(event):
        return

    users = load_json(USERS_FILE)
    premium = load_json(PREMIUM_FILE)
    banned = load_json(BANNED_FILE)

    await event.reply(
        f"📊 <b>Bot Statistics</b>\n\n"
        f"Users: {len(users)}\n"
        f"Premium: {len(premium)}\n"
        f"Banned: {len(banned)}",
        parse_mode="html",
    )


# ============================================================
# UI CALLBACKS
# ============================================================

@client.on(events.CallbackQuery(pattern=b"ui:main"))
async def ui_main(event):
    await event.answer()
    await event.edit(
        main_text(),
        buttons=main_buttons(),
        parse_mode="html",
    )


@client.on(events.CallbackQuery(pattern=b"ui:close"))
async def ui_close(event):
    await event.answer()
    await event.edit(
        "🚫 <b>Menu closed.</b>\n\nSend /start to open it again.",
        parse_mode="html",
    )


@client.on(events.CallbackQuery(pattern=b"ui:(auth|mass|shopify|charge|premium)$"))
async def ui_category(event):
    await event.answer()
    category = event.data.decode().split(":", 1)[1]

    await event.edit(
        category_text(category, 1),
        buttons=category_buttons(category, 1),
        parse_mode="html",
    )


@client.on(events.CallbackQuery(pattern=b"ui:page:"))
async def ui_page(event):
    await event.answer()

    _, _, category, page = event.data.decode().split(":", 3)
    page = int(page)

    if category not in CATEGORIES:
        await event.answer("Invalid page.", alert=True)
        return

    await event.edit(
        category_text(category, page),
        buttons=category_buttons(category, page),
        parse_mode="html",
    )


@client.on(events.CallbackQuery(pattern=b"ui:item:"))
async def ui_item(event):
    # Safe UI placeholder: no external gateway is executed.
    await event.answer(
        "This button is UI-only; no external API is connected.",
        alert=True,
    )


# ============================================================
# RUN
# ============================================================

async def main():
    init_files()
    await client.start(bot_token=BOT_TOKEN)
    print(f"{BOT_NAME} bot is running.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
