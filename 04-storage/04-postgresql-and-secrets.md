# 04 · Deploy PostgreSQL with a Secret

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Run one PostgreSQL container with credentials from a Secret and
database files on the existing PVC.

**Working directory:** `k8s-homelab-github/04-storage`.

## Concept: Secret

A Secret holds configuration such as database credentials separately
from the Deployment manifest.

Our Secret contains:
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

Base64 encoding in Secret YAML is reversible.
It is not encryption.

## Exclude credentials from Git

The root .gitignore must contain:

```text
/04-storage/secrets/
```

Verify before staging:

```bash
git check-ignore -v secrets/postgres-secret.yaml
```

## Generate credentials for a fresh installation

Do not repeat this generation against the existing database:
it produces a different password.

```bash
mkdir -p secrets

kubectl create secret generic postgres-secret \
  --namespace=jobs-demo \
  --from-literal=POSTGRES_DB=javad_jobs \
  --from-literal=POSTGRES_USER=javad \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -hex 24)" \
  --dry-run=client -o yaml > secrets/postgres-secret.yaml

chmod 600 secrets/postgres-secret.yaml
```

Inspect the file locally without sharing its contents:

```bash
cat secrets/postgres-secret.yaml
```

Validate and apply:

```bash
kubectl apply --dry-run=server -f secrets/postgres-secret.yaml
kubectl apply -f secrets/postgres-secret.yaml
kubectl get secret postgres-secret -n jobs-demo
```

Expected: Opaque, DATA 3.

The PostgreSQL image uses these initialization settings when the data
directory is empty. Updating the Secret later does not automatically
change the password in an existing database.

## Concept: Deployment and Pod template

The object below is a Deployment.

Its outer spec configures the Deployment.
Its template describes the Pod the Deployment creates through a ReplicaSet.

A saved manifest or dry run does not create the Pod.
Applying the manifest does.

## Save the PostgreSQL Deployment

```bash
cat > manifests/postgres.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: jobs-demo
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: postgres-secret
          env:
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-data
YAML
```

## Understand the connection

- replicas: 1 requests one database Pod.
- Recreate stops the old Pod before its replacement during template updates.
- selector matches the Pod template's app: postgres label.
- envFrom loads the Secret as environment variables.
- PGDATA selects the database directory inside the mounted filesystem.
- volumes references PVC postgres-data.
- volumeMounts exposes that volume inside the container.

The matching name postgres-storage connects the mount to the Pod volume.
It does not create another PVC or PV.

containerPort documents the listening port; it does not create a Service.

Do not scale this Deployment to multiple database Pods sharing one
database directory.

## Inspect, validate, and apply

```bash
cat manifests/postgres.yaml

kubectl apply --dry-run=server -f manifests/postgres.yaml
kubectl apply -f manifests/postgres.yaml

kubectl get pods -n jobs-demo -l app=postgres -o wide
```

## Verify PostgreSQL readiness

Running is a container status. This manifest has no readiness probe,
so also check PostgreSQL itself:

```bash
kubectl exec -n jobs-demo deployment/postgres -- \
  pg_isready -U javad -d javad_jobs
```

## Troubleshooting

```bash
kubectl describe pod -n jobs-demo -l app=postgres
kubectl logs -n jobs-demo deployment/postgres --tail=50
```

Events explain image pulls, scheduling problems, and mount failures.

## Verified outcome

PostgreSQL ran on worker1 and used the existing PVC.

The local directory containing database files is:

```text
/mnt/javad-jobs/postgres/pgdata
```

## Review

1. What distinguishes this object from a standalone Pod?
2. Why must selector and template labels match?
3. What is the difference between volumes and volumeMounts?
4. Why did we choose one replica and Recreate?

---

[← Previous](03-persistentvolumeclaims.md) ·
[Next: Test Persistence →](05-test-persistence.md)
