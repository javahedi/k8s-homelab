# 04 · ReplicaSets and scaling

[← Chapter index](README.md)

A ReplicaSet maintains a desired number of matching Pods. Standalone Pods stay deleted; controller-managed Pods are replaced when needed. Replicas are copies, not extra containers inside one Pod.

Save `02-workloads/manifests/nginx-replicaset.yaml`:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-rs
  namespace: workloads
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-rs
  template:
    metadata:
      labels:
        app: nginx-rs
        environment: lab
    spec:
      containers:
        - name: nginx
          image: nginx:stable
```

Template labels must satisfy the selector. Use a distinct selector to avoid accidentally adopting matching standalone Pods.

```bash
kubectl apply -f 02-workloads/manifests/nginx-replicaset.yaml
kubectl get rs nginx-rs -n workloads
kubectl get pods -n workloads -l app=nginx-rs -o wide
```

DESIRED is requested count, CURRENT is managed count, READY is ready count. Delete ONE generated Pod using its ACTUAL name from the output:

```bash
kubectl delete pod REPLACE_WITH_ACTUAL_POD_NAME -n workloads
kubectl get pods -n workloads -l app=nginx-rs
```

A new name/age proves replacement, not resurrection. Our lab replaced nginx-rs-8cj9z with nginx-rs-dxhhl; these names are historical, not reusable commands.

```bash
kubectl scale rs nginx-rs -n workloads --replicas=3
kubectl get rs nginx-rs -n workloads
kubectl get pods -n workloads -l app=nginx-rs -o wide
kubectl apply -f 02-workloads/manifests/nginx-replicaset.yaml
```

The local file still declares two, so reapplying returns the live count to two. Multiple replicas provide capacity/availability when traffic is routed appropriately; a Service is introduced in Lesson 06. Scheduling isn't round-robin and equal distribution isn't guaranteed. In ordinary application management, use a Deployment rather than managing ReplicaSets directly.

---

[← Chapter index](README.md)
