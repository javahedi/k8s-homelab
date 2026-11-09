# 03 · Bind a PersistentVolumeClaim

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Claim postgres-pv for an application in namespace jobs-demo.

**Working directory:** `k8s-homelab-github/04-storage`.

## Concept: PersistentVolumeClaim

A PVC requests storage. Unlike a PV, it belongs to a namespace.

A Pod references a PVC in its own namespace.
The PVC binds to a suitable PV.

Binding reserves the whole PV for that claim.
It does not create a database or start a Pod.

## Save the manifest

```bash
cat > manifests/postgres-pvc.yaml <<'YAML'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: jobs-demo
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 5Gi
  storageClassName: ""
  volumeName: postgres-pv
YAML
```

## Understand the fields

| Field | Purpose |
|---|---|
| namespace | Places the claim in jobs-demo |
| accessModes | Requests ReadWriteOnce access |
| volumeMode | Requests filesystem storage |
| requests.storage | Requests at least 5 GiB |
| storageClassName: "" | Requests storage without a StorageClass |
| volumeName | Explicitly selects postgres-pv |

The access mode, capacity, volume mode, and class must be compatible
with the selected PV.

## Inspect, validate, and apply

```bash
cat manifests/postgres-pvc.yaml

kubectl apply --dry-run=server -f manifests/postgres-pvc.yaml
kubectl apply -f manifests/postgres-pvc.yaml

kubectl get pvc -n jobs-demo
kubectl get pv postgres-pv
```

## Verified outcome

Both objects showed Bound.

The PV's CLAIM field showed:

```text
jobs-demo/postgres-data
```

## Troubleshooting a Pending claim

```bash
kubectl describe pvc postgres-data -n jobs-demo
kubectl describe pv postgres-pv
```

Compare the requested size, access modes, volume mode, class,
volume name, and whether another claim already owns the PV.

Do not delete the working database claim as a troubleshooting shortcut.

## Review

1. Which object requests storage?
2. Which object represents the storage?
3. Why must the PostgreSQL Pod use the same namespace as its PVC?
4. Does a Bound claim mean PostgreSQL is running?

---

[← Previous](02-persistentvolumes.md) ·
[Next: PostgreSQL and Secrets →](04-postgresql-and-secrets.md)
