# 07 — Prometheus queries (follow-up exercise)

The direct Prometheus exercise was proposed but not verified during the recorded session. Treat the following as an optional continuation.

## Open the query interface

```bash
kubectl port-forward -n monitoring service/monitoring-kube-prometheus-prometheus 9090:9090
```

Open http://localhost:9090. Prometheus collects and stores measurements; Grafana queries them to draw dashboards.

## Query 1: collection health

```promql
up
```

Execute and inspect Table view. Each label set identifies a target. Value 1 means the last scrape succeeded; 0 means it failed. It does not prove application business functionality.

## Query 2: Node Exporters

```promql
up{job="node-exporter"}
```

Inspect the labels returned by `up` first. Job names depend on configuration; use the actual label if different. The intended result is a successful target for each of the three Nodes.

## Query 3: failed scrapes

```promql
up == 0
```

Open the Targets page through the interface and inspect a failed target's last error. kubeadm control-plane components may listen only locally or need additional access/TLS configuration. Do not disable security or assume every default target is reachable. The original session did not audit every target.

## Query 4: Grafana container memory

```promql
container_memory_working_set_bytes{namespace="monitoring", container="grafana", image!=""} / 1024 / 1024
```

The result is MiB. Inspect labels if multiple series appear; do not sum duplicates blindly. Dashboard queries may use recording rules and filters, so inspect a panel's query to understand its exact calculation.

## Outcome to record

Which targets are up? Which are down, and why? Can you relate one raw metric to a Grafana panel? These are more meaningful checks than merely seeing that the Prometheus Pod is Running.
