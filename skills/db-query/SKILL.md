---
name: db-query
description: Run SQL queries against any configured MySQL/MariaDB database, selected by name (e.g. "brumi"). Use whenever the user asks to inspect, query, or update data in one of their databases.
---

# DB Query

Generic MySQL/MariaDB query runner (`scripts/db_query.py`, Python + `pymysql`). All connection details live in one config file, keyed by name; you just pick which database with `--db <name>`.

## One-time setup

1. `pip install pymysql`
2. Copy `db_connections.example.json` to `db_connections.json` (next to this file — already gitignored, never commit real credentials) and fill in one entry per database:
   ```json
   {
     "brumi": {
       "host": "srv0000.hstgr.io",
       "port": 3306,
       "user": "...",
       "password": "...",
       "database": "..."
     },
     "another_db": { "...": "..." }
   }
   ```
3. For a Hostinger-hosted database, enable it for remote access first: hPanel → Databases → Remote MySQL → add the IP this script runs from. Without that you get a timeout, not an auth error.

## Usage

List configured databases:
```bash
python scripts/db_query.py --list
```

Read query:
```bash
python scripts/db_query.py --db brumi --query "SELECT id, title FROM Property LIMIT 10"
```

From a file, JSON output:
```bash
python scripts/db_query.py --db brumi --query-file query.sql --format json
```

Write query (blocked by default):
```bash
python scripts/db_query.py --db brumi --query "UPDATE Property SET status='sold' WHERE id=42" --allow-write
```

Use a config file in another location: `--config /path/to/db_connections.json`.

## Notes

- INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/TRUNCATE/REPLACE/GRANT/REVOKE are refused unless `--allow-write` is passed.
- Always show the user the exact query and which `--db` it targets, and confirm before running anything with `--allow-write` — assume every configured database may be production, with no undo.
- Prefer `LIMIT` on exploratory SELECTs against large tables.
