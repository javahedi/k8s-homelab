# 09 · Verify Database Integration

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Verify the frontend receives jobs from PostgreSQL through backend v2.

**Working directory:** `k8s-homelab-github/04-storage`.

## 1. Forward the frontend Service

In a separate terminal:

```bash
kubectl port-forward -n jobs-demo service/frontend 8082:80
```

Keep that terminal open.

Open:

```text
http://localhost:8082
```

This is access to the cluster app from the Mac.
It is not a separate local Docker Compose deployment.

## 2. Query through Nginx

```bash
curl -i http://localhost:8082/api/jobs
```

Verified response: HTTP 200 with the initial two jobs.

Matching the old hardcoded response alone does not prove the database
is being queried, because both sources initially contain the same data.

## 3. Add a database-only record

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  psql -U javad -d javad_jobs -v ON_ERROR_STOP=1 \
  -c "INSERT INTO jobs (id, title, city)
      VALUES (3, 'Storage Engineer', 'Hamburg')
      ON CONFLICT (id) DO NOTHING;"
```

## 4. Query again

```bash
curl -s http://localhost:8082/api/jobs
```

Refresh the frontend page.

Verified response included:

```json
[
  {"id":1,"title":"Python Developer","city":"Berlin"},
  {"id":2,"title":"Kubernetes Administrator","city":"Bremen"},
  {"id":3,"title":"Storage Engineer","city":"Hamburg"}
]
```

No backend image rebuild was needed for the database change.

## 5. Inspect logs and current resources

```bash
kubectl logs -n jobs-demo deployment/backend --tail=50

kubectl get deployments,pods,services -n jobs-demo

kubectl get pvc -n jobs-demo
kubectl get pv postgres-pv
```

Do not use kubectl get secret -o yaml for shared verification output:
it prints encoded credentials.

## Problems encountered in this lab

### Internal Server Error at the backend root route

The backend's / route attempts to serve frontend/index.html.
The backend Dockerfile does not copy that file.

Load the page through Nginx's frontend Service.
The /api/jobs route works independently.

### Local port already in use

An earlier port-forward occupied 8081.
We used 8082 for the frontend instead.

Stop an earlier forward with Ctrl+C or select another local port.

### Port-forward ended after replacing a Pod

Restart the forwarding command.
A session attaches to a selected Pod and does not automatically
follow every Pod replacement.

### Docker Desktop was stopped

docker ps on the Mac could not contact its engine.
The existing Kubernetes Pods continued using containerd in the VMs.

### docker compose could not find its configuration

The terminal was in 04-storage.
The Compose file is in ../03-networking/demo-app.

Compose is separate from the running Kubernetes application.
Its database configuration remains pending.

## Verified conclusions

- PostgreSQL uses a Bound PVC and local PV.
- A test database record survived PostgreSQL Pod replacement.
- The PostgreSQL Service selects the database Pod.
- Backend v2 reads jobs from PostgreSQL.
- Nginx forwards API requests successfully.
- A database-only addition appears without rebuilding the application.
- Secret manifests are excluded from Git.

## Still pending

StorageClasses, dynamic provisioning, NFS, StatefulSets,
and the final module review have not yet been exercised.

## Review

1. Why was returning the original two jobs insufficient proof?
2. Which change required rebuilding the image?
3. Which change only required SQL?
4. Is opening localhost through port-forward a local application deployment?

---

[← Previous](08-build-and-deploy-v2.md) ·
[← Chapter index](README.md)
