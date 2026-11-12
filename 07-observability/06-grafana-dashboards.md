# 06 — Read Grafana dashboards

## Open Grafana

```bash
kubectl port-forward -n monitoring service/monitoring-grafana 3000:80
```

Open http://localhost:3000 in an up-to-date browser. Keep the forwarding terminal running.

Retrieve credentials locally; do not commit them or paste them into a chat:

```bash
kubectl get secret monitoring-grafana -n monitoring -o jsonpath='{.data.admin-user}' | base64 --decode
kubectl get secret monitoring-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 --decode
```

The output may have no trailing newline. Starred may be empty simply because no dashboards are starred. Use Dashboards and clear the Starred filter.

## Browse from broad to specific

| Dashboard | Question |
|---|---|
| Kubernetes / Compute Resources / Nodes Overview | Which Node needs attention? |
| Kubernetes / Compute Resources / Namespace (Pods) | Which workload consumes resources? |
| Kubernetes / Compute Resources / Pod | Which container consumes resources? |

Choose Last 15 minutes, then select the intended Namespace and Pod. Names can change when Pods are replaced. The calico-system Namespace shows networking components; monitoring shows our monitoring stack; jobs-demo shows the application.

## Requests, limits and measurements

- Allocatable: Node capacity exposed for workload scheduling.
- Requests: declared resource budgets used for scheduling; not ceilings.
- Limits: configured ceilings; memory exhaustion can cause OOM termination.
- Usage: measured consumption represented by the panel's query.

CPU: 1 core = 1000m. Usage of 0.056 cores is about 56m, not 56 percent of the entire cluster.

A memory request utilization of 130% is allowed. Aggregate utilization from limits does not prove every container has headroom. Missing CPU limits can produce No data for limit-based ratios.

## Recorded Grafana example

| Container | Memory working set at the screenshot |
|---|---:|
| grafana | 332 MiB |
| grafana-sc-dashboard | 76.1 MiB |
| grafana-sc-datasources | 77.1 MiB |

The main container's request was 256Mi and limit 512Mi. A roughly 500Mi Pod total includes helper containers and cannot be directly compared with the main container's 512Mi limit. Working set is useful but is not identical to every byte charged against a cgroup memory limit.

These are historical readings, not current resource guarantees. CPU/memory graphs should be interpreted with restarts, health checks and user-facing tests.

## Panel errors

Safari displayed `TypeError: ...toArray is not a function` in quota panels. The same panels worked in Chrome. That isolated the observed display failure to a browser-specific issue; no cluster change was needed.

- No data: query has no usable result, not necessarily zero usage.
- Red unexpected error: expand Details and inspect the error.
- Gaps: may reflect restart, unavailable collection, retention or query behavior.

Ctrl+C stops forwarding but does not stop Grafana or Prometheus.
