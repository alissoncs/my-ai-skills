---
name: query-brumi-db
description: Connect to and query the Brumi (brumiimoveis.com.br) production MySQL/MariaDB database hosted on Hostinger. Use whenever the user asks to inspect, query, or update data in the Brumi database.
---

# Query Brumi DB

Runs SQL against the Brumi database via `scripts/query_db.py` (Python, `pymysql` driver — pure Python, no compiled dependencies).

This is the **production** database behind brumiimoveis.com.br. Treat every write as high-blast-radius.

## One-time setup

1. `pip install pymysql`
2. In Hostinger hPanel → Databases → Remote MySQL, add the IP this script will run from (Hostinger blocks external connections by default — without this you'll get a connection timeout/refused error, not an auth error).
3. Get the DB host, port, user, password, and database name from hPanel → Databases (or from the production `DATABASE_URL` if already deployed — NOT the local docker one in `brumi-site/.env`, which points at `127.0.0.1:3307`).
4. Create `.env` next to this skill (never commit it — already gitignored) with:
   ```
   DB_HOST=...
   DB_PORT=3306
   DB_USER=...
   DB_PASSWORD=...
   DB_NAME=...
   ```

## Usage

Read query:
```bash
python scripts/query_db.py --query "SELECT id, title FROM Property LIMIT 10"
```

From a file, JSON output:
```bash
python scripts/query_db.py --query-file query.sql --format json
```

Write query (blocked by default — production safety):
```bash
python scripts/query_db.py --query "UPDATE Property SET status='sold' WHERE id=42" --allow-write
```

## Notes

- INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/TRUNCATE/REPLACE/GRANT/REVOKE are refused unless `--allow-write` is passed.
- Always show the user the exact query and confirm before running it with `--allow-write` — there is no undo on production data.
- Prefer `LIMIT` on exploratory SELECTs against large tables.
