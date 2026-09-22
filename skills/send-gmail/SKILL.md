---
name: send-gmail
description: Send an email through the user's Gmail account. Use whenever the user asks to send, compose, or forward an email (with optional attachments, CC/BCC, or HTML body) and Gmail is their mail provider.
---

# Send Gmail

Sends email via Gmail's SMTP server using `scripts/send_email.py` (Python 3, stdlib only — no dependencies to install).

## One-time setup (tell the user if credentials are missing)

1. Enable 2-Step Verification on the Google account.
2. Create an App Password at https://myaccount.google.com/apppasswords (select "Mail").
3. Set two environment variables (or put them in a `.env` file next to the script — never commit that file):
   - `GMAIL_ADDRESS` — the full Gmail address to send from
   - `GMAIL_APP_PASSWORD` — the 16-character app password (not the account password)

## Usage

```bash
python scripts/send_email.py \
  --to "someone@example.com" \
  --subject "Subject line" \
  --body "Plain text body"
```

Options:
- `--body-file path.txt` instead of `--body` to read the body from a file
- `--html` to send `--body`/`--body-file` content as HTML
- `--cc`, `--bcc` — comma-separated addresses
- `--attach path` — repeatable, attaches one or more files
- `--env-file path` — load credentials from a specific file (default: `.env` in the current directory)

Multiple recipients: pass a comma-separated list to `--to`, `--cc`, or `--bcc`.

## Notes

- Always confirm the recipient, subject, and body with the user before sending — sending an email is not easily reversible.
- If login fails with an authentication error, the most common cause is using the regular account password instead of an App Password, or 2-Step Verification not being enabled.
