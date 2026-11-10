# Chapter 05 — Security and Cluster Operations

Hands-on notes for JAVAD_CKA, recorded 10 November 2026.

## Reading order

1. [Overview](00-security-and-cluster-ops-overview.md)
2. [ServiceAccounts](01-serviceaccounts.md)
3. [RBAC](02-rbac.md)
4. [SecurityContext](03-security-context.md)
5. [Node maintenance](04-node-maintenance.md)
6. [etcd backup](05-etcd-backup.md)
7. [etcd restore](06-etcd-restore.md)
8. [kubeadm upgrades](07-kubeadm-upgrades.md)
9. [CKA review](08-cka-review.md)

## Completion record

| Topic | Evidence | Status |
|---|---|---|
| Namespaces and ServiceAccounts | identity-demo uses app-sa | Practised |
| RBAC | Pod listing changed from no to yes after binding | Practised; ClusterRole exercise reported done |
| SecurityContext | UID 1000; write to /tmp denied | Practised |
| Maintenance | worker2 drained and uncordoned; all nodes Ready | Practised |
| etcd backup | Snapshot saved and status inspected | Practised |
| etcd restore | Data files rebuilt in separate directory | File restore practised; live recovery pending |
| kubeadm upgrades | Plan reported current and target version 1.37.2 | Assessment practised; actual upgrade pending |
| Final review | Exercises provided below | Pending |

These notes document what was learned; they do not certify readiness for the whole CKA exam.

## Using these files

Copy the Markdown files into your existing repository's
`05-security-and-cluster-ops/` directory, alongside `manifests/`.
The existing six YAML manifests are not included or overwritten in this tutorial pack.

From the repository root, review and commit:

```bash
git status
git diff --check
git add 05-security-and-cluster-ops/
git diff --cached --stat
git commit -m "Document chapter 5 security and cluster operations labs"
```

Before committing, inspect the staged content. Never commit etcd snapshots, private keys,
kubeconfig credentials, or Secret manifests containing real credentials.
Do not copy VM data directories into this repository.
