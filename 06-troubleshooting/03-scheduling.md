# 03 — Pending: node selector mismatch

The broken Pod required:

```yaml
nodeSelector:
  disktype: nonexistent
```

No node had that label. Events showed:

```text
0/3 nodes are available:
1 node(s) had untolerated taint(s),
2 node(s) didn't match Pod's node affinity/selector.
Preemption is not helpful for scheduling.
```

The control-plane had an untolerated taint, and the workers did not match the selector. Evicting other Pods cannot create matching labels or tolerations.

## Diagnose

```bash
kubectl describe pod broken-scheduling -n troubleshooting
kubectl get nodes --show-labels
kubectl describe node control-plane
```

Read the node's Taints field to verify the specific taint; do not remove control-plane taints to solve a worker selector mistake.

## Repair

Edit `manifests/broken-scheduling.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: broken-scheduling
  namespace: troubleshooting
spec:
  nodeSelector:
    kubernetes.io/hostname: worker1
  containers:
    - name: nginx
      image: nginx:stable
```

Recreate the disposable Pod because its nodeSelector cannot be changed in place:

```bash
kubectl replace --force -f manifests/broken-scheduling.yaml
kubectl get pod broken-scheduling -n troubleshooting -o wide
```

Expected: ready and assigned to worker1. Our posted status confirmed `1/1 Running`; `-o wide` also verifies placement.

Other Pending causes include insufficient requested resources and unbound PVCs. The Events section distinguishes them.
