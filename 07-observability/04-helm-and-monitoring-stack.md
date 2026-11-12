# 04 — Helm and the monitoring stack

## Chart, values and manifest

A chart is a package of templates. Values configure those templates. Rendering produces Kubernetes manifests. Helm installs and tracks the resources as a release.

```bash
helm version --short
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm search repo prometheus-community
```

Search output lists available packages, not installed software. Chart version and application version are different fields.

## Defaults are reference material

```bash
helm show values prometheus-community/kube-prometheus-stack \
  --version 93.2.2 > manifests/monitoring-defaults.yaml
```

Leave that file unchanged. The chart already contains defaults; Helm does not automatically read this downloaded copy. Our separate `monitoring-values.yaml` holds deliberate overrides passed with `--values`.

Search a specific section instead of memorizing the file:

```bash
rg -n -A 12 '^alertmanager:' manifests/monitoring-defaults.yaml
```

Dependency chart documentation may contain options not fully expanded in the parent chart's values file.

## Final intended overrides

The following reconstructs the settings used during the successful lab recovery. Compare with your existing file before changing anything. Resource numbers are lab starting budgets, not universal recommendations.

```yaml
alertmanager:
  enabled: false

grafana:
  enabled: true
  nodeSelector:
    kubernetes.io/hostname: worker2
  deploymentStrategy:
    type: Recreate
    rollingUpdate: null
  persistence:
    enabled: false
  livenessProbe:
    initialDelaySeconds: 300
  readinessProbe:
    timeoutSeconds: 5
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      memory: 512Mi

prometheus:
  prometheusSpec:
    replicas: 1
    retention: 6h
    scrapeInterval: 30s
    evaluationInterval: 30s
    resources:
      requests:
        cpu: 100m
        memory: 256Mi
      limits:
        memory: 512Mi

prometheusOperator:
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      memory: 192Mi

kube-state-metrics:
  resources:
    requests:
      cpu: 20m
      memory: 32Mi
    limits:
      memory: 128Mi

prometheus-node-exporter:
  resources:
    requests:
      cpu: 20m
      memory: 32Mi
    limits:
      memory: 64Mi
```

Alertmanager was deferred. Default recording/alert rules may still exist. No Prometheus persistent volume was configured; its local history is temporary. Grafana persistence is disabled. Node affinity to worker2 is a homelab placement choice that reduces scheduling flexibility.

## Installation and updates

For a new release only:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --version 93.2.2 --namespace monitoring --create-namespace \
  --values manifests/monitoring-values.yaml --wait --timeout 10m
```

For this existing release:

```bash
helm upgrade monitoring prometheus-community/kube-prometheus-stack \
  --version 93.2.2 --namespace monitoring \
  --values manifests/monitoring-values.yaml --wait --timeout 10m
```

`--wait` can remain silent while waiting. A timeout/failure can leave resources installed. Inspect rather than immediately repeating installation. The admission setup Job is temporary; Completed is expected.

```bash
helm status monitoring -n monitoring
kubectl get pods -n monitoring -o wide
```

A label filter such as `-l release=monitoring` may omit Grafana and operator-managed Pods. Namespace-wide listing is more complete.
