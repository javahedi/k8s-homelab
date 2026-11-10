# 00 — Overview

## Goal

Understand application identity, API permissions, container restrictions, node maintenance,
cluster-state backups, and the kubeadm upgrade workflow.

## Lab environment

| Machine | Address | Role |
|---|---|---|
| control-plane | 192.168.252.2 | API server, scheduler, controllers, etcd |
| worker1 | 192.168.252.3 | Workloads, including PostgreSQL host storage |
| worker2 | 192.168.252.4 | Workloads; maintenance exercise target |

Observed Kubernetes version: v1.37.2. Observed etcd image:
`registry.k8s.io/etcd:3.7.0-0`. VM architecture: ARM64 (`aarch64`).

## Where commands run

- Mac: kubectl using your homelab kubeconfig.
- control-plane VM: etcd tools, protected local files, kubeadm upgrade assessment.
- A kubectl exec command is typed on the Mac but executes its trailing command inside a container.

```bash
# Mac
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
kubectl get nodes
multipass shell control-plane
```

`exit` leaves the VM shell. Changing local directories does not change kubectl's namespace.
Creating a namespace does not select it. Use `-n security-lab` explicitly.

## Three distinct kinds of access

| Connection | Credentials |
|---|---|
| Your kubectl to Kubernetes API | kubeconfig user credentials |
| Application to Kubernetes API | ServiceAccount token |
| Backend to PostgreSQL | PostgreSQL username/password |

RBAC controls API actions. SecurityContext controls Linux execution restrictions.
A Service is a network abstraction; a ServiceAccount is an identity.

## Suggested four-hour study budget

| Topic | Minutes |
|---|---:|
| Namespaces and ServiceAccounts | 25 |
| RBAC | 40 |
| SecurityContext | 25 |
| Break | 10 |
| Maintenance | 30 |
| etcd backup and restore | 40 |
| Break | 10 |
| Upgrade workflow | 30 |
| Review | 30 |

This is a study budget, not a record of elapsed time.
