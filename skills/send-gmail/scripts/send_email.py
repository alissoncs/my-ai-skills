#!/usr/bin/env python3
"""Send an email through Gmail's SMTP server.

Auth: reads GMAIL_ADDRESS and GMAIL_APP_PASSWORD from the environment
(or a --env-file). The app password must be a 16-char Gmail "App Password"
(https://myaccount.google.com/apppasswords) — a normal account password
will not work with SMTP.
"""

import argparse
import mimetypes
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


def load_env_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send an email via Gmail SMTP.")
    parser.add_argument("--to", required=True, help="Comma-separated recipient addresses")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", help="Plain-text or HTML body (mutually exclusive with --body-file)")
    parser.add_argument("--body-file", type=Path, help="Read the body from a file")
    parser.add_argument("--html", action="store_true", help="Treat the body as HTML")
    parser.add_argument("--cc", help="Comma-separated CC addresses")
    parser.add_argument("--bcc", help="Comma-separated BCC addresses")
    parser.add_argument("--attach", action="append", default=[], help="Path to a file to attach (repeatable)")
    parser.add_argument("--env-file", type=Path, default=Path(".env"), help="Optional .env file with GMAIL_ADDRESS/GMAIL_APP_PASSWORD")
    return parser.parse_args()


def build_message(args: argparse.Namespace, sender: str) -> EmailMessage:
    if bool(args.body) == bool(args.body_file):
        sys.exit("Provide exactly one of --body or --body-file")

    body = args.body if args.body else args.body_file.read_text(encoding="utf-8")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = args.to
    if args.cc:
        msg["Cc"] = args.cc
    msg["Subject"] = args.subject

    if args.html:
        msg.set_content("This email requires an HTML-capable client.")
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    for path_str in args.attach:
        path = Path(path_str)
        if not path.is_file():
            sys.exit(f"Attachment not found: {path}")
        ctype, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (ctype.split("/", 1) if ctype else ("application", "octet-stream"))
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)

    return msg


def all_recipients(args: argparse.Namespace) -> list[str]:
    recipients = [addr.strip() for addr in args.to.split(",") if addr.strip()]
    for field in (args.cc, args.bcc):
        if field:
            recipients += [addr.strip() for addr in field.split(",") if addr.strip()]
    return recipients


def main() -> None:
    args = parse_args()

    if args.env_file.is_file():
        load_env_file(args.env_file)

    sender = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender or not app_password:
        sys.exit(
            "Missing credentials. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD "
            "(environment variables or an --env-file), using a Gmail App Password."
        )

    msg = build_message(args, sender)
    recipients = all_recipients(args)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg, from_addr=sender, to_addrs=recipients)

    print(f"Sent to: {', '.join(recipients)}")


if __name__ == "__main__":
    main()
