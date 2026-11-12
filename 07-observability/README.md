# Chapter 07 — Observability

Monitoring, logs, resource usage, Prometheus and Grafana in the JAVAD_CKA homelab.

## What this chapter answers

Is the application working? If not, which layer needs investigation? Observability provides evidence; a green dashboard alone does not guarantee every user operation succeeds.

## Read in order

1. [Start here](00-start-here.md)
2. [Cluster health and events](01-cluster-health-and-events.md)
3. [Logs, containers and restarts](02-logs-and-restarts.md)
4. [Metrics and Metrics Server](03-metrics-and-metrics-server.md)
5. [Helm and monitoring installation](04-helm-and-monitoring-stack.md)
6. [Troubleshooting and worker recovery](05-troubleshooting-and-recovery.md)
7. [Reading Grafana dashboards](06-grafana-dashboards.md)
8. [Prometheus queries](07-prometheus-queries.md)
9. [Review, final checks and Git](08-review-and-git.md)

## Recorded outcome — 12 November 2026

- Metrics Server was attempted, failed, and was removed.
- kube-prometheus-stack chart 93.2.2 was deployed as release `monitoring`, Namespace `monitoring`.
- Helm revision 6 reported `deployed`.
- Grafana became ready on worker2 after a memory adjustment and worker1 recovery.
- Node, Namespace and Pod dashboards displayed metrics.
- Quota panels failed in Safari but worked in Chrome.
- The direct Prometheus `up` query was proposed but not yet verified in this session.
- worker1 was cordoned during recovery; verify and uncordon if still necessary.

## Existing files

Keep your existing `manifests/` directory. This tutorial archive contains documentation only: it does not replace your working manifests or override file. Do not execute every historical recovery command as a setup script.

## References

- https://github.com/kubernetes-sigs/metrics-server
- https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack
- https://prometheus.io/docs/introduction/overview/
- https://grafana.com/docs/grafana/latest/
- https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
