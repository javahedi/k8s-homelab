# 00 — Start here

## Lab topology

| Machine | Node IP | Role |
|---|---|---|
| control-plane | 192.168.252.2 | API server, scheduler, controllers, etcd |
| worker1 | 192.168.252.3 | Runs application Pods |
| worker2 | 192.168.252.4 | Runs application Pods |

## Before troubleshooting

```bash
multipass list
kubectl get nodes
kubectl get pods -A
```

At the start of our session, nodes were Ready but several Pods were Unknown or not ready. Recent restart timestamps suggested a fresh startup. We watched recovery and all Pods recovered without intervention:

```bash
kubectl get pods -A -w
```

Press Ctrl+C to stop watching. It does not stop Pods. If the cluster does not recover, inspect events and node health rather than repeatedly waiting.

## Diagnostic workflow

1. Locate the affected namespace and resource.
2. Read status, readiness, and restart count.
3. Use `describe` for scheduling, image, probe, and container termination details.
4. Read current and previous container logs.
5. Compare desired configuration with the observed failure.
6. Make one targeted correction and verify actual behavior.

```bash
kubectl get pods -n troubleshooting -o wide
kubectl describe pod POD_NAME -n troubleshooting
kubectl logs POD_NAME -n troubleshooting
kubectl logs POD_NAME -n troubleshooting --previous
kubectl get events -n troubleshooting --sort-by=.metadata.creationTimestamp
```

`Running` alone does not prove an application works. Check readiness and make an application request.

## Exercise namespace

For a new lab only:

```bash
kubectl create namespace troubleshooting
```

Our namespace and repaired Pods already exist. Do not recreate them unless deliberately repeating the exercises.
