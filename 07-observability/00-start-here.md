# 00 — Start here

## Goal

Learn to investigate availability and resource consumption using Kubernetes commands and monitoring dashboards. Prometheus and Grafana extend the command-line checks with measurements over time.

## Homelab used in this chapter

| Node | Address | CPUs | Reported RAM |
|---|---|---:|---:|
| control-plane | 192.168.252.2 | 2 | 1.9 GiB |
| worker1 | 192.168.252.3 | 1 | 1.4 GiB |
| worker2 | 192.168.252.4 | 1 | 1.4 GiB |

Kubernetes reported v1.37.2; Helm reported v4.3.1. These are session observations, not a general compatibility guarantee. The host Mac has limited resources, so this is a small learning installation.

Existing application Namespace: `jobs-demo`, with frontend, backend and PostgreSQL. PostgreSQL uses persistent storage previously prepared on worker1.

## Vocabulary

| Term | Meaning |
|---|---|
| Image | Packaged program and its dependencies |
| Container | A running execution created from an image |
| Pod | Kubernetes object containing one or more containers |
| Deployment | Controller managing replacement and rollout of application Pods |
| DaemonSet | Controller running a Pod on each eligible Node |
| Metric | Numeric measurement with labels and a timestamp |
| Target | Endpoint Prometheus attempts to collect metrics from |
| Helm chart | Templates, defaults and metadata used to install Kubernetes resources |
| Helm release | A named installation of a chart |

## Start in the correct directory

On your Mac, from the repository root:

```bash
mkdir -p 07-observability/manifests
cd 07-observability
kubectl config current-context
```

Check that the context is your homelab before applying changes.

## Monitoring components

| Component | Responsibility |
|---|---|
| Node Exporter | Expose Linux host measurements |
| kube-state-metrics | Expose information about Kubernetes objects |
| kubelet metrics | Supply container and Node measurements collected by Prometheus |
| Prometheus | Collect and store time-series measurements; evaluate rules |
| Grafana | Query a data source and render dashboards |
| Prometheus Operator | Reconcile Prometheus-related custom resources |

Metrics Server is a separate component serving Kubernetes resource metrics for clients such as `kubectl top`. This monitoring stack does not require it.
