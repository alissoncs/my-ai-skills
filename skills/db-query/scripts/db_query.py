#!/usr/bin/env python3
"""Run a SQL query against any MySQL/MariaDB database, picked by name.

Connections are defined once in a JSON config (default: db_connections.json
next to this script) keyed by a short name, e.g.:

    {
      "brumi": {"host": "...", "port": 3306, "user": "...", "password": "...", "database": "..."},
      "other_project": {"host": "...", "port": 3306, "user": "...", "password": "...", "database": "..."}
    }

Pick which one to use with --db <name>. Requires `pip install pymysql`.
"""

import argparse
import json
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

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "db_connections.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query a named MySQL/MariaDB database.")
    parser.add_argument("--db", required=True, help="Connection name as defined in the config file")
    parser.add_argument("--query", help="SQL statement (mutually exclusive with --query-file)")
    parser.add_argument("--query-file", type=Path, help="Read the SQL statement from a file")
    parser.add_argument("--allow-write", action="store_true", help="Allow INSERT/UPDATE/DELETE/DDL statements")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help=f"Path to the connections JSON file (default: {DEFAULT_CONFIG.name})")
    parser.add_argument("--list", action="store_true", help="List the connection names defined in the config and exit")
    return parser.parse_args()


def load_connections(config_path: Path) -> dict:
    if not config_path.is_file():
        sys.exit(
            f"Config file not found: {config_path}\n"
            "Create it from db_connections.example.json with your connection details."
        )
    return json.loads(config_path.read_text(encoding="utf-8"))


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
    connections = load_connections(args.config)

    if args.list:
        for name in connections:
            print(name)
        return

    if args.db not in connections:
        sys.exit(f"Unknown --db '{args.db}'. Available: {', '.join(connections) or '(none configured)'}")

    conn_info = connections[args.db]
    query = get_query(args).strip()

    if WRITE_KEYWORDS.match(query) and not args.allow_write:
        sys.exit(
            "Refusing to run a write/DDL statement without --allow-write. "
            "Confirm with the user before running it against this database."
        )

    conn = pymysql.connect(
        host=conn_info["host"],
        port=int(conn_info.get("port", 3306)),
        user=conn_info["user"],
        password=conn_info["password"],
        database=conn_info["database"],
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
