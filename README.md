# Valyrian UI Project

`Gatewaybot_original.py` is the original uploaded source, unchanged.

`valyrian_ui.py` is a separate UI/navigation layer based on the supplied
Valyrian-style screenshots: main menu, 2-column category buttons,
pagination, Back/Main Menu/Close.

`config_template.py` documents the configuration names without storing
credentials.

The UI module intentionally does not implement card checking, charging,
payment processing, credential validation, or external gateway execution.

Integration example:

    from valyrian_ui import install
    install(client)

Your existing `/start` handler can use:

    from valyrian_ui import main_text, main_buttons
    await event.reply(main_text(), buttons=main_buttons(), parse_mode="html")

Run the original bot with its existing dependencies/configuration.
