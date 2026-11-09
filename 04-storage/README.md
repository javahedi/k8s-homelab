# Module 04 — Storage

[← Project overview](../README.md)

> **Status: partially completed and verified on 9 November 2026.**
> PostgreSQL persistence and FastAPI integration are verified.
> StorageClasses, NFS, and StatefulSets remain pending.
> Read chapters in order; setup commands describe the original lab
> and should not all be rerun against an existing database.

## Learning chapters

The numbered lesson files are being written from our verified exercises.

- 00 · Storage Overview and Lab Architecture
- 01 · Prepare Local Storage on worker1
- 02 · Create a PersistentVolume
- 03 · Bind a PersistentVolumeClaim
- 04 · Deploy PostgreSQL with a Secret
- 05 · Verify Persistence after Pod Replacement
- 06 · Create the PostgreSQL Service
- 07 · Connect FastAPI to PostgreSQL
- 08 · Build, Import, and Deploy Backend v2
- 09 · Verify Database Integration
- 10 · StorageClasses and Dynamic Provisioning — pending
- 11 · NFS Storage — pending
- 12 · StatefulSets — pending
- 13 · Review and Troubleshooting — pending

## Supporting materials

- [PostgreSQL PV](manifests/postgres-pv.yaml)
- [PostgreSQL PVC](manifests/postgres-pvc.yaml)
- [PostgreSQL Deployment](manifests/postgres.yaml)
- [PostgreSQL Service](manifests/postgres-service.yaml)
- [Initial jobs table and records](sql/01-jobs.sql)
- [Application source](../03-networking/demo-app/backend/main.py)
- [Backend Deployment](../03-networking/demo-app/k8s/backend.yaml)

## Verification checklist

- [x] Storage directory prepared on worker1
- [x] Local PV created with node affinity and Retain policy
- [x] PVC in jobs-demo bound to the PV
- [x] PostgreSQL credentials stored in a Secret
- [x] Secret manifest excluded from Git
- [x] PostgreSQL running on worker1 using persistent storage
- [x] Database record survived Pod replacement
- [x] PostgreSQL Service selected the database Pod
- [x] Backend v2 image imported into both workers
- [x] FastAPI queried PostgreSQL through its Service
- [x] New database row appeared through Nginx without rebuilding
- [ ] StorageClasses and dynamic provisioning exercised
- [ ] NFS exercised
- [ ] StatefulSets exercised
- [ ] Chapter review completed

## Important limits

The database uses local storage tied to worker1.
Pod replacement preserves data, but loss of worker1's disk can lose it.
Retain is not a backup.

The local Docker Compose configuration has not been updated for
the database-backed application.

**Safety:** Never commit Secret manifests, passwords, kubeconfigs,
or database files. The directory secrets/ is excluded through
the repository's root .gitignore.
