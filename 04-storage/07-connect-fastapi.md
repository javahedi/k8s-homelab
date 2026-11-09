# 07 · Connect FastAPI to PostgreSQL

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Replace the hardcoded jobs response with a database query.

**Working directory:** `k8s-homelab-github/04-storage`.

Application code remains in ../03-networking/demo-app.
We improve that existing application rather than duplicate it.

## Prepare the database table

Save the SQL:

```bash
mkdir -p sql

cat > sql/01-jobs.sql <<'SQL'
CREATE TABLE IF NOT EXISTS jobs (
    id integer PRIMARY KEY,
    title text NOT NULL,
    city text NOT NULL
);

INSERT INTO jobs (id, title, city)
VALUES
    (1, 'Python Developer', 'Berlin'),
    (2, 'Kubernetes Administrator', 'Bremen')
ON CONFLICT (id) DO NOTHING;
SQL
```

Inspect before executing:

```bash
cat sql/01-jobs.sql
```

Send it into PostgreSQL:

```bash
kubectl exec -i -n jobs-demo deployment/postgres -- \
  psql -U javad -d javad_jobs -v ON_ERROR_STOP=1 \
  < sql/01-jobs.sql
```

The shell reads the file on the Mac.
-i forwards standard input to psql in the cluster container.

This command modifies the running database.
It does not rebuild or edit the backend.

Verify:

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  psql -U javad -d javad_jobs \
  -c "SELECT id, title, city FROM jobs ORDER BY id;"
```

## Add the Python driver

Ensure requirements.txt contains this entry once:

```text
psycopg[binary]>=3.2,<4
```

Psycopg lets Python connect to PostgreSQL.
The binary extra includes compiled components for supported platforms.

## Update main.py locally

Add imports:

```python
import os
import psycopg
from psycopg.rows import dict_row
```

Replace the existing /api/jobs handler:

```python
@app.get("/api/jobs")
def list_jobs():
    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, city FROM jobs ORDER BY id"
            )
            return cursor.fetchall()
```

Keep the existing FastAPI application and health route.

## Understand the code

| Part | Purpose |
|---|---|
| os.environ | Reads settings supplied to the container |
| psycopg.connect | Opens a database connection |
| connect_timeout | Limits connection establishment to five seconds |
| dict_row | Returns rows as dictionaries |
| cursor.execute | Runs the SQL query |
| fetchall | Retrieves all result rows |
| with blocks | Close the cursor and connection |

This lab opens one connection per request.
Connection pooling and application error handling are later improvements.

## Important boundary

Editing main.py changes only the file on the Mac.

The cluster keeps running the code packaged in its existing image
until a new image is built, imported, and deployed.

The current Compose file also needs database configuration before
it can run this updated backend successfully as a separate local app.

## Review

1. Why does SQL execution change the database immediately?
2. Why does editing main.py not change the cluster immediately?
3. Where will the backend get its password?
4. Why use dictionaries for the returned rows?

---

[← Previous](06-postgresql-service.md) ·
[Next: Build and Deploy v2 →](08-build-and-deploy-v2.md)
