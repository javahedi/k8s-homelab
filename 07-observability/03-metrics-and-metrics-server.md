# 03 — Metrics and the Metrics Server attempt

## Linux tools versus Kubernetes metrics

| Tool | View |
|---|---|
| top on the Mac | Host processes, including VM processes |
| top inside a worker VM | That Linux Node's processes and resources |
| kubectl top nodes | Kubernetes resource metrics summarized by Node |
| kubectl top pods | Kubernetes resource metrics grouped by Pod |

```bash
multipass shell worker1
top
```

Press `q`, then `exit`. Containers run as processes on the Node; ordinary `top` does not conveniently group them by Kubernetes Namespace and Pod.

## What happened in the lab

```bash
kubectl top nodes
kubectl get deployment -n kube-system
kubectl get apiservice v1beta1.metrics.k8s.io
```

The Metrics API was unavailable and its APIService absent. We downloaded the official manifest into `manifests/metrics-server.yaml` and applied it. That manifest describes a Deployment, Service, identity, permissions and API registration; it is not the executable program itself.

The initial logs reported kubelet certificates without matching IP SANs. We tried `--kubelet-insecure-tls`, a homelab workaround that skips kubelet certificate verification. That attempt still failed: both Metrics Server Pods later showed CrashLoopBackOff. The subsequent crash cause was not established in the session. Do not assume the flag caused or resolved it.

## Cleanup performed

```bash
kubectl delete -f manifests/metrics-server.yaml
kubectl get pods -n kube-system
kubectl get apiservice v1beta1.metrics.k8s.io
```

The APIService returned NotFound. The local YAML remained as an exercise record. Do not apply the entire manifests directory indiscriminately: this would reinstall the removed component.

Prometheus and Grafana operate independently of Metrics Server. Removing Metrics Server means `kubectl top` remains unavailable until a working resource Metrics API is provided.

## Future Rust project

A Rust observer can query Kubernetes status without Metrics Server. A homemade resource collector can read Linux measurements directly; a DaemonSet can distribute it across Nodes. Per-container collection and mapping to Pods add complexity. Making `kubectl top` use it would require implementing and registering the expected Kubernetes Metrics API. This project was designed, not implemented, during Chapter 07.
