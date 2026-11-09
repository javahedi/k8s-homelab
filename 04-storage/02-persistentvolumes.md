# 02 · Create a PersistentVolume

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Represent the directory on worker1 as a Kubernetes PersistentVolume.

**Working directory:** `k8s-homelab-github/04-storage`.

## Concept: PersistentVolume

A PV represents storage available to the cluster.
It is cluster-scoped and has no namespace.

For static provisioning, an administrator prepares storage and creates
the PV before an application claims it.

## Save the manifest

kubectl has no dedicated local-PV generator, so write the YAML directly:

```bash
cat > manifests/postgres-pv.yaml <<'YAML'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
  local:
    path: /mnt/javad-jobs/postgres
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
                - worker1
YAML
```

## Understand the fields

| Field | Purpose |
|---|---|
| kind | Creates a PersistentVolume |
| capacity.storage | Advertises 5 GiB for claim matching |
| volumeMode | Makes storage available as a filesystem |
| ReadWriteOnce | Read/write mounting by a single node |
| Retain | Keeps storage for manual handling after claim release |
| storageClassName: "" | Uses no StorageClass |
| local.path | Identifies the existing storage directory |
| nodeAffinity | Restricts consumers to the node labeled worker1 |

The 5Gi capacity does not impose a quota on this directory.

ReadWriteOnce is a node-level access mode, not a one-Pod guarantee.
Multiple Pods on one node may be able to access the same volume.

## Inspect and validate

```bash
cat manifests/postgres-pv.yaml

kubectl apply --dry-run=server -f manifests/postgres-pv.yaml
```

A server dry run processes the request without saving the object.
It does not verify whether a container can use the directory.

For comparison, a client dry run prepares an object without sending
a write request. It is useful for generating manifests:

```bash
kubectl run example --image=nginx \
  --dry-run=client -o yaml
```

That example prints YAML; it creates no Pod.

## Apply and inspect

```bash
kubectl apply -f manifests/postgres-pv.yaml

kubectl get pv postgres-pv
kubectl describe pv postgres-pv
```

Before a PVC claims it, the expected status is Available.
In our completed lab, it is now Bound.

## Verified outcome

PV postgres-pv exists and represents storage on worker1.

## Review

1. Why does this manifest have no namespace?
2. Does capacity.storage enforce a directory quota?
3. What does nodeAffinity describe?
4. Why is Retain different from a backup?

---

[← Previous](01-prepare-local-storage.md) ·
[Next: PersistentVolumeClaims →](03-persistentvolumeclaims.md)
