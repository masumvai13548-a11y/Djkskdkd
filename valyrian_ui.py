"""
Valyrian-style UI layer.

Presentation/navigation only. No payment, card-checking, charging,
credential validation, or external gateway execution is implemented here.
"""

from telethon import Button, events

BOT_NAME = "VALYRIAN"

CATEGORIES = {
    "auth": "🔒 Auth Gates",
    "mass": "📊 Mass Checker",
    "shopify": "⚡ Shopify Gates",
    "charge": "💳 Charge Gates",
    "premium": "🎀 Premium Gates",
}

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
        [Button.inline("🔒 Auth Gates", b"v_auth"),
         Button.inline("📊 Mass Checker", b"v_mass")],
        [Button.inline("⚡ Shopify Gates", b"v_shopify"),
         Button.inline("💳 Charge Gates", b"v_charge")],
        [Button.inline("🎀 Premium Gates", b"v_premium")],
        [Button.inline("🚫 Close", b"v_close")],
    ]


def category_text(category, page=1, per_page=4):
    title = CATEGORIES[category]
    items = ITEMS[category]
    total = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total))
    current = items[(page - 1) * per_page: page * per_page]

    lines = [f"⚡ <b>{title}</b>", ""]
    for label, command in current:
        lines += [
            label,
            f"Command: <code>{command}</code>",
            "Status: UI",
            ""
        ]
    lines.append(f"✓ <i>Page {page} of {total}</i>")
    return "\n".join(lines)


def category_buttons(category, page=1, per_page=4):
    items = ITEMS[category]
    total = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total))
    current = items[(page - 1) * per_page: page * per_page]

    rows = []
    for i in range(0, len(current), 2):
        pair = current[i:i + 2]
        rows.append([Button.inline(label, data=f"v_item:{category}:{command}".encode())
                     for label, command in pair])

    nav = []
    if page > 1:
        nav.append(Button.inline("◀️ Back", data=f"v_page:{category}:{page-1}".encode()))
    if page < total:
        nav.append(Button.inline("Next ▶️", data=f"v_page:{category}:{page+1}".encode()))
    if nav:
        rows.append(nav)

    rows.append([
        Button.inline("🔙 Main Menu", b"v_main"),
        Button.inline("🚫 Close", b"v_close")
    ])
    return rows


def install(client):
    """Install the UI callbacks into an existing Telethon client."""

    @client.on(events.CallbackQuery(pattern=b"v_main"))
    async def v_main(event):
        await event.answer()
        await event.edit(main_text(), buttons=main_buttons(), parse_mode="html")

    @client.on(events.CallbackQuery(pattern=b"v_close"))
    async def v_close(event):
        await event.answer()
        await event.edit(
            "🚫 <b>Menu closed.</b>\n\nSend /start to open it again.",
            parse_mode="html"
        )

    for key in CATEGORIES:
        pattern = f"v_{key}".encode()

        async def category_handler(event, key=key):
            await event.answer()
            await event.edit(
                category_text(key, 1),
                buttons=category_buttons(key, 1),
                parse_mode="html"
            )

        client.add_event_handler(
            category_handler,
            events.CallbackQuery(pattern=pattern)
        )

    @client.on(events.CallbackQuery(pattern=b"v_page:"))
    async def v_page(event):
        await event.answer()
        _, category, page = event.data.decode().split(":", 2)
        page = int(page)
        await event.edit(
            category_text(category, page),
            buttons=category_buttons(category, page),
            parse_mode="html"
        )

    @client.on(events.CallbackQuery(pattern=b"v_item:"))
    async def v_item(event):
        await event.answer("UI button only.", alert=True)

    return client
