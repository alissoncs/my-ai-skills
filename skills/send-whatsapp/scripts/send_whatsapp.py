#!/usr/bin/env python3
"""Send a WhatsApp message via pywhatkit (WhatsApp Web automation).

Requires:
- `pip install pywhatkit`
- The default browser logged into WhatsApp Web (https://web.whatsapp.com)
  at least once before running.

pywhatkit drives WhatsApp Web by opening a browser tab, waiting for it to
load, typing the message and pressing Enter — there is no official WhatsApp
API involved.
"""

import argparse
import sys
from pathlib import Path

try:
    import pywhatkit
except ImportError:
    sys.exit("Missing dependency. Install it with: pip install pywhatkit")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a WhatsApp message via WhatsApp Web.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--to", help="Recipient phone number in international format, e.g. +5551995027624")
    target.add_argument("--group-id", help="WhatsApp group invite id (the part after chat.whatsapp.com/)")

    parser.add_argument("--message", help="Message text (mutually exclusive with --message-file)")
    parser.add_argument("--message-file", type=Path, help="Read the message from a file")

    parser.add_argument("--hour", type=int, help="Hour (0-23) to schedule the send; omit to send instantly")
    parser.add_argument("--minute", type=int, help="Minute (0-59) to schedule the send; required with --hour")

    parser.add_argument("--wait-time", type=int, default=20, help="Seconds to wait for WhatsApp Web to load (default: 20)")
    parser.add_argument("--tab-close", action="store_true", default=True, help="Close the browser tab after sending (default: on)")
    parser.add_argument("--no-tab-close", dest="tab_close", action="store_false", help="Keep the browser tab open after sending")
    parser.add_argument("--close-time", type=int, default=5, help="Seconds to wait before closing the tab (default: 5)")

    return parser.parse_args()


def get_message(args: argparse.Namespace) -> str:
    if bool(args.message) == bool(args.message_file):
        sys.exit("Provide exactly one of --message or --message-file")
    return args.message if args.message else args.message_file.read_text(encoding="utf-8")


def main() -> None:
    args = parse_args()
    message = get_message(args)

    scheduled = args.hour is not None or args.minute is not None
    if scheduled and (args.hour is None or args.minute is None):
        sys.exit("--hour and --minute must be given together")

    common_kwargs = dict(
        message=message,
        wait_time=args.wait_time,
        tab_close=args.tab_close,
        close_time=args.close_time,
    )

    if args.group_id:
        if scheduled:
            pywhatkit.sendwhatmsg_to_group(args.group_id, message, args.hour, args.minute, args.wait_time, args.tab_close, args.close_time)
        else:
            pywhatkit.sendwhatmsg_to_group_instantly(args.group_id, **common_kwargs)
        print(f"Sent to group: {args.group_id}")
    else:
        if scheduled:
            pywhatkit.sendwhatmsg(args.to, message, args.hour, args.minute, args.wait_time, args.tab_close, args.close_time)
        else:
            pywhatkit.sendwhatmsg_instantly(args.to, **common_kwargs)
        print(f"Sent to: {args.to}")


if __name__ == "__main__":
    main()
