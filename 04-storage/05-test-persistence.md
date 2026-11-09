# 05 · Verify Persistence after Pod Replacement

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Prove database records survive replacement of the PostgreSQL Pod.

**Working directory:** `k8s-homelab-github/04-storage`.

This documents a completed test. The CREATE TABLE command below is
for the original run and will fail if the table already exists.

## Concept: Pod lifetime versus storage lifetime

A Deployment replaces a deleted Pod.

The replacement references the same PVC.
The PVC and PV remain separate objects, so deleting the Pod normally
does not delete the stored files.

## Write a record

kubectl exec runs a command inside the container.
psql is PostgreSQL's command-line client.

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  psql -U javad -d javad_jobs -v ON_ERROR_STOP=1 -c \
  "CREATE TABLE storage_test (
     id integer PRIMARY KEY,
     message text NOT NULL
   );
   INSERT INTO storage_test VALUES
     (1, 'Hello from Javad — persistent data');"
```

Read the record before deleting anything:

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  psql -U javad -d javad_jobs \
  -c "SELECT * FROM storage_test;"
```

## Record the original Pod identity

```bash
kubectl get pods -n jobs-demo -l app=postgres -o wide
```

Observe its name, IP, age, and node.

## Replace only the Pod

This interrupts the database briefly.

```bash
kubectl delete pod -n jobs-demo -l app=postgres

kubectl get pods -n jobs-demo -l app=postgres -o wide -w
```

Press Ctrl+C after the new Pod reaches Running.

Do not delete the Deployment, PVC, PV, or directory for this test.
Do not use force deletion.

Check database readiness:

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  pg_isready -U javad -d javad_jobs
```

Retry after a few seconds if PostgreSQL is still starting.

## Read the original record

Do not recreate the table or reinsert the row:

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  psql -U javad -d javad_jobs \
  -c "SELECT * FROM storage_test;"
```

## Verified outcome

The Pod name and IP changed.
The original record remained.
The replacement ran on worker1.

This proves persistence across Pod replacement, not database replication
or recovery from loss of the worker's disk.

## Review

1. What created the replacement Pod?
2. Why did the database record remain?
3. Why did the new Pod return to worker1?
4. Would deleting and recreating the row prove persistence?

---

[← Previous](04-postgresql-and-secrets.md) ·
[Next: PostgreSQL Service →](06-postgresql-service.md)
