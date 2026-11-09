# 01 · Prepare Local Storage on worker1

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Prepare a directory inside worker1 to hold PostgreSQL database files.

**Working directory on the Mac:** `k8s-homelab-github/04-storage`.

These commands document the completed exercise. There is no need to
repeat the setup on the existing lab.

## Concept: local storage

A local volume uses storage on a specific Kubernetes node.

Our directory is inside the worker1 Multipass VM. It is not a directory
inside the application container and is not directly in the Mac repository.

A replacement PostgreSQL Pod can reuse this directory.
If worker1's disk is lost, this local volume does not recover the data.

## Inspect the cluster

```bash
kubectl get nodes -o wide
multipass list
```

All three nodes should be Ready.

## Prepare and inspect the directory

```bash
mkdir -p manifests

multipass exec worker1 -- \
  sudo mkdir -p /mnt/javad-jobs/postgres

multipass exec worker1 -- \
  sudo ls -ld /mnt/javad-jobs/postgres
```

`multipass exec worker1 --` executes the following command inside worker1.

`sudo mkdir -p` creates the directory and any missing parent directories.

## Inspect the hostname label

```bash
kubectl get node worker1 --show-labels
```

Verified label:

```text
kubernetes.io/hostname=worker1
```

The PV uses this label to identify the node holding its storage.
Do not assume the label matches another lab without checking.

## Verified outcome

- Directory exists on worker1.
- worker1 is Ready.
- Its hostname label is worker1.

Preparing a directory does not create a PV, PVC, or PostgreSQL Pod.

## Review

1. Is this directory on the Mac or inside worker1?
2. Why must a Pod using this local storage run on worker1?
3. Does local persistence protect against loss of the VM disk?

---

[← Previous](00-storage-overview.md) ·
[Next: PersistentVolumes →](02-persistentvolumes.md)
