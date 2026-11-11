# 07 — Verify frontend → backend → PostgreSQL

## Inspect on the Mac

```bash
kubectl get pods -n jobs-demo -o wide
kubectl get services -n jobs-demo
kubectl get endpointslices -n jobs-demo
```

Our three Pods were ready and running on worker1. The EndpointSlices matched their Pod addresses:

| Application | Service IP and port | Pod IP and port |
|---|---|---|
| frontend | 10.107.196.100:80 | 10.244.235.246:80 |
| backend | 10.107.208.50:8000 | 10.244.235.253:8000 |
| postgres | 10.103.48.203:5432 | 10.244.235.249:5432 |

Frontend was a NodePort Service with port 31554. Backend and postgres were ClusterIP Services.

## Make an application request

Mac terminal 1:

```bash
kubectl port-forward -n jobs-demo service/frontend 8082:80
```

Keep it running. Mac terminal 2:

```bash
curl http://localhost:8082/api/jobs
```

Our response began with job JSON, including `Python Developer`, and the application worked. In our app, the frontend proxy forwards `/api/jobs` to the backend, which queries PostgreSQL.

This verifies the application path through the frontend Pod using port-forward. It does not verify the external NodePort path, and port-forward to a Service selects a backend Pod rather than testing traffic to the Service's ClusterIP.

Stop port-forward with Ctrl+C in terminal 1.

## If the request fails

Start with relevant logs:

```bash
kubectl logs -n jobs-demo deployment/frontend --tail=50
kubectl logs -n jobs-demo deployment/backend --tail=50
kubectl logs -n jobs-demo deployment/postgres --tail=50
```

- No localhost connection: check whether port-forward is still running.
- Frontend proxy error: check backend readiness, Service endpoints, and proxy destination.
- Backend database error: check postgres readiness, Service endpoints, database configuration, and logs.
- DNS failure: check the exact name and namespace before assuming CoreDNS is broken.

Do not print database Secret values into notes or commit them to Git.
