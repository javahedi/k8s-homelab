# 04 — Node maintenance

## Purpose

Prepare a node for maintenance, then return it to service.

| Action | Effect |
|---|---|
| cordon | Stop ordinary new scheduling; existing Pods stay |
| drain | Cordon and evict eligible Pods |
| uncordon | Allow scheduling again |

Run kubectl from the Mac. Inspect before eviction:

```bash
kubectl get pods -A -o wide --field-selector spec.nodeName=worker2
kubectl cordon worker2
kubectl get nodes
```

Observed: Ready,SchedulingDisabled. This is not a node failure.
The inverse command is uncordon, not a trailing hyphen on the node name.

## The emptyDir blocker

```bash
kubectl drain worker2 --ignore-daemonsets --timeout=120s
```

Our first attempt stopped because Traefik had emptyDir volumes mounted at /data and /tmp.
No Pods were evicted in that attempt; names and IPs remained unchanged.
Inspect volumes and their contents before deciding that losing them is acceptable:

```bash
kubectl get deployment traefik -n traefik -o yaml
kubectl exec -n traefik deployment/traefik -- ls -la /data /tmp
```

Both were empty in our lab. We then ran:

```bash
kubectl drain worker2 --ignore-daemonsets --delete-emptydir-data --timeout=120s
```

delete-emptydir-data permits losing emptyDir contents, not deleting PVCs.
Drain can also be blocked by PodDisruptionBudgets or unmanaged Pods. Investigate the specific
blocker rather than automatically adding force or disabling eviction.

## What changed

| Application | Old IP on worker2 | New IP on worker1 |
|---|---|---|
| backend | 10.244.189.109 | 10.244.235.243 |
| nginx | 10.244.189.107 | 10.244.235.242 |

Old Pods were deleted; controllers created new Pods. This is replacement, not live migration.
Pod names/IPs can change; node addresses and Service ClusterIPs do not change because of drain.
Single-replica applications may have an interruption.

## Why DaemonSet Pods remained

DaemonSets maintain one Pod on each eligible node, useful for local networking and monitoring agents.
Deployments request a replica count; multiple replicas may share a node.
On worker2, calico-node, csi-node-driver, and kube-proxy were DaemonSet-managed.
Calico Typha was Deployment-managed and evicted.
ignore-daemonsets leaves DaemonSet Pods running; it does not stop them.

## Finish

```bash
kubectl get pods -A -o wide --field-selector spec.nodeName=worker2
kubectl rollout status deployment/backend -n jobs-demo --timeout=120s
kubectl rollout status deployment/traefik -n traefik --timeout=120s
kubectl get pods -n networking -o wide
kubectl uncordon worker2
kubectl get nodes
```

Observed final node state: all three Ready. Traefik replacement was initially ContainerCreating;
verify its rollout separately. Uncordon does not rebalance existing Pods automatically.
worker1 holds PostgreSQL's host-local data; do not assume that workload can move freely.
The old dns-client Unknown state existed before the drain and is a separate troubleshooting item.

Reference: https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/
