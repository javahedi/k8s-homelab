# 10 · Scheduling: selectors, affinity and taints

[← Chapter index](README.md)

## Node selector

```bash
kubectl get nodes -L kubernetes.io/hostname
kubectl run placement-demo -n workloads --image=nginx:stable --dry-run=client -o yaml > 02-workloads/manifests/placement-demo.yaml
```

Add under Pod spec alongside containers:

```yaml
  nodeSelector:
    kubernetes.io/hostname: worker2
```

Apply and inspect `kubectl get pod placement-demo -n workloads -o wide`: expect worker2. Change worker2 to worker99, delete/recreate practice Pod. Expect Pending, no IP/node. Describe Events: workers don't match selector, control-plane has an untolerated taint. Preemption cannot fix nonexistent label matches by deleting other workloads.

## Required node affinity
Remove nodeSelector entirely and use this full healthy manifest:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: placement-demo
  namespace: workloads
  labels:
    run: placement-demo
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: kubernetes.io/hostname
                operator: In
                values:
                  - worker2
  containers:
    - name: placement-demo
      image: nginx:stable
```

Affinity and containers must align under spec. Validate with apply --dry-run=client, then delete/recreate placement-demo. It returns to worker2. Required means mandatory at scheduling; IgnoredDuringExecution means a later node label change alone doesn't evict it. Preferred affinity adds a scheduling preference, not a guarantee; it was discussed as an extension, not tested. Terms are OR alternatives; expressions within a term are AND requirements.

## Taints

```bash
kubectl get nodes -o custom-columns='NODE:.metadata.name,TAINTS:.spec.taints'
kubectl describe node worker2
kubectl taint node worker2 training=reserved:NoSchedule
```

Ready is node health; taints are placement restrictions. A Ready node can be tainted.

| Effect | Without a matching toleration |
|---|---|
| NoSchedule | Block new scheduling, leave existing Pods running |
| PreferNoSchedule | Try to avoid new placement |
| NoExecute | Also evict existing non-tolerating Pods |

NoSchedule is not network isolation. Confirm existing placement-demo remains running; delete/recreate it without toleration: expect Pending because affinity requires the tainted worker2.

## Toleration
Add to Pod spec, alongside affinity/containers:

```yaml
  tolerations:
    - key: training
      operator: Equal
      value: reserved
      effect: NoSchedule
```

```bash
kubectl delete pod placement-demo -n workloads
kubectl apply -f 02-workloads/manifests/placement-demo.yaml
kubectl wait -n workloads --for=condition=Ready pod/placement-demo --timeout=120s
kubectl get pod placement-demo -n workloads -o wide
kubectl taint node worker2 training=reserved:NoSchedule-
```

Expect Running on worker2 while tainted, then remove practice taint. Toleration grants permission; affinity requires worker2. Toleration alone doesn't force a Pod there. A trailing minus removes a taint, just as label removal uses a trailing minus. Remove only the practice taint, not system taints. If Pending solely due to a removed taint, a Pod can schedule without recreation.

[Official taints and tolerations reference](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)

---

[← Chapter index](README.md)
