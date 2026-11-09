# 00 · Storage Overview and Lab Architecture

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Understand where application code runs, where database files live,
and how Kubernetes connects a Pod to persistent storage.

This lesson explains the architecture. It does not change the cluster.

## Starting point

Javad Jobs was deployed during Module 03 in namespace jobs-demo:

- Nginx serves the HTML and JavaScript frontend.
- FastAPI provides the backend API.
- Backend v1 returned a hardcoded Python list from /api/jobs.
- Traefik Ingress was tested during the networking exercises.

Module 04 adds PostgreSQL and changes the backend to read database rows.

Gateway API remains a separate networking lesson.

## 1. Mac, virtual machines, and cluster

Our Mac runs:
- The Git repository and source editor.
- kubectl.
- Multipass.
- Docker Desktop for building application images.

Multipass runs three Ubuntu ARM64 VMs:

| VM | Purpose |
|---|---|
| control-plane | Runs Kubernetes control-plane components |
| worker1 | Runs application Pods and holds our local database storage |
| worker2 | Runs application Pods |

The Kubernetes nodes use containerd as their container runtime.

Docker Desktop on the Mac and containerd inside each VM have
separate image stores.

Stopping Docker Desktop does not automatically stop the
existing Kubernetes containers inside the Multipass VMs.

## 2. Namespace versus node

A namespace groups Kubernetes resources logically.
A node is a machine where Pods can run.

The jobs-demo namespace is not restricted to one worker.
Its frontend and backend Pods can be scheduled on eligible workers.

Our PostgreSQL Pod is restricted to worker1 by the local PV's
node affinity, because its database files are stored there.

PV and StorageClass objects are cluster-scoped.
PVCs, Secrets, Deployments, Services, and Pods are namespaced.

## 3. Why persistent storage?

A container's writable filesystem is temporary.
Replacing a container or Pod must not destroy our database records.

We therefore store PostgreSQL's database files on storage
whose lifecycle is independent of the Pod.

Persistent storage does not automatically provide replication,
backups, or protection from disk failure.

## 4. Storage vocabulary

| Term | Meaning | Our example |
|---|---|---|
| PV | PersistentVolume: represents available storage | postgres-pv |
| PVC | PersistentVolumeClaim: requests and claims storage | postgres-data |
| StorageClass | Describes storage provisioning and settings | None in the first exercise |
| Volume | Storage declared in a Pod specification | postgres-storage |
| Volume mount | Path where a container accesses a volume | /var/lib/postgresql/data |
| Local volume | Storage available on a particular node | Directory on worker1 |

We use static provisioning first:
prepare storage, create the PV, then create a matching PVC.

Dynamic provisioning is covered later.

## 5. Our storage connection

The PostgreSQL Pod references PVC postgres-data.

That PVC is bound to PV postgres-pv.

The PV represents this directory inside worker1:

```text
/mnt/javad-jobs/postgres
```

Inside the PostgreSQL container, the volume is mounted at:

```text
/var/lib/postgresql/data
```

PGDATA selects a subdirectory:

```text
/var/lib/postgresql/data/pgdata
```

The actual database files therefore reside on worker1 at:

```text
/mnt/javad-jobs/postgres/pgdata
```

The PVC and PV are Kubernetes objects.
The directory contains the actual database files.

## 6. Application request flow

After deploying backend v2:

1. The browser loads HTML and JavaScript from Nginx.
2. JavaScript requests /api/jobs.
3. Nginx forwards the API request to FastAPI.
4. FastAPI connects to Service postgres on port 5432.
5. PostgreSQL reads the jobs table from its database.
6. FastAPI returns JSON and the frontend displays it.

The backend does not mount PostgreSQL's PVC.
It communicates with PostgreSQL over the network.

## 7. Source code versus image versus container

These are separate things:

| Item | Location | What changes it |
|---|---|---|
| main.py source | Git working directory on the Mac | Editing the file |
| Backend image | Docker or containerd image store | Building/importing an image |
| Running backend container | Kubernetes worker | Deployment creates a Pod from an image |
| Database records | PostgreSQL persistent storage | Executing SQL |

Editing main.py does not update a running container.

Our deployment process is:

1. Edit main.py and requirements.txt.
2. Build javad-jobs-backend:v2 on the Mac.
3. Export the image to an archive.
4. Copy and import it into both workers.
5. Update the backend Deployment image and environment settings.
6. Apply the manifest and verify the rollout.

Database changes are different: SQL executes against the running
database and updates its stored records without rebuilding an image.

## 8. What Pod replacement proved

We inserted a record into storage_test.

We deleted the PostgreSQL Pod normally.

The Deployment's ReplicaSet created a replacement Pod.
The replacement used the same PVC and read the original record.

Verified outcome:
- Pod name changed.
- Pod IP changed.
- The record survived.
- PostgreSQL remained on worker1 because its storage is local.

This proves persistence across Pod replacement.
It does not prove recovery from losing the worker VM or disk.

## 9. Working directory and resource scope

Commands in this module assume the terminal is in:

```text
k8s-homelab-github/04-storage
```

The working directory affects relative file paths.

It does not select the Kubernetes namespace.
Use -n jobs-demo explicitly for namespaced resources.

The kubeconfig context selects the cluster.

## Read-only inspection

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get deployments,pods,services -n jobs-demo
kubectl get pv
kubectl get pvc -n jobs-demo
kubectl get storageclasses
```

## Review questions

1. Why does editing main.py not change the running backend?
2. Which object is namespaced: a PV or a PVC?
3. Where are PostgreSQL's actual database files?
4. Why must our PostgreSQL Pod run on worker1?
5. Does the backend need to mount the database PVC?
6. What survives Pod replacement, and what can change?

---

[← Chapter index](README.md) ·
[Next: Prepare Local Storage →](01-prepare-local-storage.md)
EOFcat > 00-storage-overview.md <<'EOF'
# 00 · Storage Overview and Lab Architecture

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Understand where application code runs, where database files live,
and how Kubernetes connects a Pod to persistent storage.

This lesson explains the architecture. It does not change the cluster.

## Starting point

Javad Jobs was deployed during Module 03 in namespace jobs-demo:

- Nginx serves the HTML and JavaScript frontend.
- FastAPI provides the backend API.
- Backend v1 returned a hardcoded Python list from /api/jobs.
- Traefik Ingress was tested during the networking exercises.

Module 04 adds PostgreSQL and changes the backend to read database rows.

Gateway API remains a separate networking lesson.

## 1. Mac, virtual machines, and cluster

Our Mac runs:
- The Git repository and source editor.
- kubectl.
- Multipass.
- Docker Desktop for building application images.

Multipass runs three Ubuntu ARM64 VMs:

| VM | Purpose |
|---|---|
| control-plane | Runs Kubernetes control-plane components |
| worker1 | Runs application Pods and holds our local database storage |
| worker2 | Runs application Pods |

The Kubernetes nodes use containerd as their container runtime.

Docker Desktop on the Mac and containerd inside each VM have
separate image stores.

Stopping Docker Desktop does not automatically stop the
existing Kubernetes containers inside the Multipass VMs.

## 2. Namespace versus node

A namespace groups Kubernetes resources logically.
A node is a machine where Pods can run.

The jobs-demo namespace is not restricted to one worker.
Its frontend and backend Pods can be scheduled on eligible workers.

Our PostgreSQL Pod is restricted to worker1 by the local PV's
node affinity, because its database files are stored there.

PV and StorageClass objects are cluster-scoped.
PVCs, Secrets, Deployments, Services, and Pods are namespaced.

## 3. Why persistent storage?

A container's writable filesystem is temporary.
Replacing a container or Pod must not destroy our database records.

We therefore store PostgreSQL's database files on storage
whose lifecycle is independent of the Pod.

Persistent storage does not automatically provide replication,
backups, or protection from disk failure.

## 4. Storage vocabulary

| Term | Meaning | Our example |
|---|---|---|
| PV | PersistentVolume: represents available storage | postgres-pv |
| PVC | PersistentVolumeClaim: requests and claims storage | postgres-data |
| StorageClass | Describes storage provisioning and settings | None in the first exercise |
| Volume | Storage declared in a Pod specification | postgres-storage |
| Volume mount | Path where a container accesses a volume | /var/lib/postgresql/data |
| Local volume | Storage available on a particular node | Directory on worker1 |

We use static provisioning first:
prepare storage, create the PV, then create a matching PVC.

Dynamic provisioning is covered later.

## 5. Our storage connection

The PostgreSQL Pod references PVC postgres-data.

That PVC is bound to PV postgres-pv.

The PV represents this directory inside worker1:

```text
/mnt/javad-jobs/postgres
```

Inside the PostgreSQL container, the volume is mounted at:

```text
/var/lib/postgresql/data
```

PGDATA selects a subdirectory:

```text
/var/lib/postgresql/data/pgdata
```

The actual database files therefore reside on worker1 at:

```text
/mnt/javad-jobs/postgres/pgdata
```

The PVC and PV are Kubernetes objects.
The directory contains the actual database files.

## 6. Application request flow

After deploying backend v2:

1. The browser loads HTML and JavaScript from Nginx.
2. JavaScript requests /api/jobs.
3. Nginx forwards the API request to FastAPI.
4. FastAPI connects to Service postgres on port 5432.
5. PostgreSQL reads the jobs table from its database.
6. FastAPI returns JSON and the frontend displays it.

The backend does not mount PostgreSQL's PVC.
It communicates with PostgreSQL over the network.

## 7. Source code versus image versus container

These are separate things:

| Item | Location | What changes it |
|---|---|---|
| main.py source | Git working directory on the Mac | Editing the file |
| Backend image | Docker or containerd image store | Building/importing an image |
| Running backend container | Kubernetes worker | Deployment creates a Pod from an image |
| Database records | PostgreSQL persistent storage | Executing SQL |

Editing main.py does not update a running container.

Our deployment process is:

1. Edit main.py and requirements.txt.
2. Build javad-jobs-backend:v2 on the Mac.
3. Export the image to an archive.
4. Copy and import it into both workers.
5. Update the backend Deployment image and environment settings.
6. Apply the manifest and verify the rollout.

Database changes are different: SQL executes against the running
database and updates its stored records without rebuilding an image.

## 8. What Pod replacement proved

We inserted a record into storage_test.

We deleted the PostgreSQL Pod normally.

The Deployment's ReplicaSet created a replacement Pod.
The replacement used the same PVC and read the original record.

Verified outcome:
- Pod name changed.
- Pod IP changed.
- The record survived.
- PostgreSQL remained on worker1 because its storage is local.

This proves persistence across Pod replacement.
It does not prove recovery from losing the worker VM or disk.

## 9. Working directory and resource scope

Commands in this module assume the terminal is in:

```text
k8s-homelab-github/04-storage
```

The working directory affects relative file paths.

It does not select the Kubernetes namespace.
Use -n jobs-demo explicitly for namespaced resources.

The kubeconfig context selects the cluster.

## Read-only inspection

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get deployments,pods,services -n jobs-demo
kubectl get pv
kubectl get pvc -n jobs-demo
kubectl get storageclasses
```

## Review questions

1. Why does editing main.py not change the running backend?
2. Which object is namespaced: a PV or a PVC?
3. Where are PostgreSQL's actual database files?
4. Why must our PostgreSQL Pod run on worker1?
5. Does the backend need to mount the database PVC?
6. What survives Pod replacement, and what can change?

---

[← Chapter index](README.md) ·
[Next: Prepare Local Storage →](01-prepare-local-storage.md)
