# 02 — Logs and restarts

## Read recent output

```bash
kubectl logs -n jobs-demo deployment/backend --tail=30 --timestamps
kubectl logs -n jobs-demo deployment/frontend --tail=30 --timestamps
kubectl logs -n jobs-demo deployment/postgres --tail=30 --timestamps
```

These logs are application stdout/stderr. They do not automatically contain every file-based application log or every SQL query. Selecting a Deployment is convenient, but with multiple replicas it does not mean you have inspected every Pod.

## Follow a request live

```bash
kubectl logs -n jobs-demo deployment/backend --tail=5 --timestamps -f
```

Make the `/api/jobs` request from the previous lesson. A new request entry appeared in the backend log. Ctrl+C stops following; the container keeps running.

## Interpret the observed messages

| Message | Interpretation |
|---|---|
| Application startup complete | Backend startup completed |
| GET /api/jobs ... 200 OK | A specific request succeeded |
| PostgreSQL: Skipping initialization | Existing database directory found |
| Ready to accept connections | PostgreSQL completed startup |
| Checkpoint complete | Normal PostgreSQL maintenance |

Look for repeated exceptions, failed requests, authentication errors, disk errors and recurring startup sequences. Correlate timestamps across components. UTC `09:15` and `10:15+01:00` represent the same instant.

## What “previous container” means

The same Pod can run a new container execution after an earlier one stops. No image change or manual Pod replacement is required.

```bash
kubectl logs -n jobs-demo <pod-name> --previous --tail=40 --timestamps
```

This requests the previous execution's retained logs in that Pod. It does not retrieve logs from any deleted historical Pod. Availability depends on retained runtime logs.

The backend had one restart with Reason `Unknown`, exit code 255. Its previous logs showed startup only. We could not establish the cause from those logs. Similar startup times suggested a Node/VM event but did not prove it.

## Multiple containers

```bash
kubectl logs -n monitoring deployment/monitoring-grafana -c grafana --tail=60
```

`-c grafana` selects the main Grafana container, rather than its dashboard or data-source helper.

Exit code 137 alone does not prove OOM. Use the recorded termination reason and events. Later in this chapter, `OOMKilled` explicitly appeared for Grafana.
