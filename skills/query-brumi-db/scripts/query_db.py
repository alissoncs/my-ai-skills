#!/usr/bin/env python3
"""Run a SQL query against the Brumi MySQL/MariaDB database on Hostinger.

Auth: reads DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME from the
environment (or a --env-file). Requires `pip install pymysql`.

Write queries (INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/TRUNCATE/REPLACE) are
blocked unless --allow-write is passed, since this talks to a production
database.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import pymysql
except ImportError:
    sys.exit("Missing dependency. Install it with: pip install pymysql")

WRITE_KEYWORDS = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def load_env_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the Brumi database on Hostinger.")
    parser.add_argument("--query", help="SQL statement (mutually exclusive with --query-file)")
    parser.add_argument("--query-file", type=Path, help="Read the SQL statement from a file")
    parser.add_argument("--allow-write", action="store_true", help="Allow INSERT/UPDATE/DELETE/DDL statements")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--env-file", type=Path, default=Path(".env"), help="Optional .env file with DB_* vars")
    return parser.parse_args()


def get_query(args: argparse.Namespace) -> str:
    if bool(args.query) == bool(args.query_file):
        sys.exit("Provide exactly one of --query or --query-file")
    return args.query if args.query else args.query_file.read_text(encoding="utf-8")


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("(0 rows)")
        return
    headers = list(rows[0].keys())
    widths = [max(len(h), max((len(str(r[h])) for r in rows), default=0)) for h in headers]
    print(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(str(row[h]).ljust(w) for h, w in zip(headers, widths)))
    print(f"({len(rows)} rows)")


def main() -> None:
    args = parse_args()

    if args.env_file.is_file():
        load_env_file(args.env_file)

    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        sys.exit(f"Missing env vars: {', '.join(missing)} (set them or use --env-file)")

    query = get_query(args).strip()

    if WRITE_KEYWORDS.match(query) and not args.allow_write:
        sys.exit(
            "Refusing to run a write/DDL statement without --allow-write. "
            "This connects to a production database — confirm with the user first."
        )

    conn = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            if cursor.description is None:
                conn.commit()
                print(f"OK. Rows affected: {cursor.rowcount}")
                return
            rows = cursor.fetchall()
    finally:
        conn.close()

    if args.format == "json":
        print(json.dumps(rows, default=str, ensure_ascii=False, indent=2))
    else:
        print_table(rows)


if __name__ == "__main__":
    main()
