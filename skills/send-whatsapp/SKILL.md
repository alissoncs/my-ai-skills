---
name: send-whatsapp
description: Send a WhatsApp message (to a contact or a group) using pywhatkit. Use whenever the user asks to send, schedule, or forward a WhatsApp message.
---

# Send WhatsApp

Sends WhatsApp messages via `scripts/send_whatsapp.py`, built on [pywhatkit](https://github.com/Ankit404butfound/PyWhatKit). This automates WhatsApp Web in the default browser — it is not the official WhatsApp Business API, so it requires a visible browser window and a moment for the page to load.

## One-time setup

1. `pip install pywhatkit`
2. Log into https://web.whatsapp.com in the default browser at least once (scan the QR code from the phone). The session must stay logged in.

## Usage

Send instantly to a contact:

```bash
python scripts/send_whatsapp.py --to "+5551995027624" --message "Olá!"
```

Send to a group (use the id from the group's invite link, `chat.whatsapp.com/<id>`):

```bash
python scripts/send_whatsapp.py --group-id "XXXXXXXXXXXXXXXXXXXXXX" --message "Olá pessoal!"
```

Schedule for a specific time instead of sending instantly:

```bash
python scripts/send_whatsapp.py --to "+5551995027624" --message "Bom dia!" --hour 9 --minute 0
```

Options:
- `--message-file path.txt` instead of `--message` to read the text from a file
- `--wait-time N` — seconds to wait for WhatsApp Web to load before typing (default 20; slow connections may need more)
- `--no-tab-close` — keep the browser tab open after sending instead of auto-closing it
- `--close-time N` — seconds to wait before closing the tab (default 5)

`--to` must include the country code (e.g. `+55` for Brazil).

## Notes

- Always confirm the recipient and message text with the user before sending — this is not easily reversible and opens a visible browser window.
- Never impersonate another person or organization in the message content.
- Immediately after calling `sendwhatmsg`/`sendwhatmsg_instantly`, pywhatkit switches focus to the browser and simulates keystrokes — avoid touching the keyboard/mouse while it runs.
