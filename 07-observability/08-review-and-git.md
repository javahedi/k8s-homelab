# 08 — Review, final checks and Git

## What was completed

- Cluster health, events and application request checks.
- Current, live and previous container logs.
- Container restart versus Pod replacement terminology.
- Metrics Server attempt and removal.
- Helm defaults versus explicit overrides.
- Prometheus/Grafana installation and recovery.
- Node, Namespace and per-container dashboard interpretation.
- Browser-specific panel error diagnosis.

## Boundaries

Metrics Server remains removed. We did not add backend health probes, implement a Rust observer, configure persistent monitoring storage, or verify direct Prometheus query exercises. Alert delivery was deferred. These are follow-up tasks, not completed claims.

## Final checks

```bash
kubectl get nodes
kubectl get pods -n jobs-demo -o wide
kubectl get pods -n monitoring -o wide
helm status monitoring -n monitoring
multipass info worker1 worker2
```

Expected: Nodes Ready, all required containers ready, release deployed, no recurring recent restarts or severe Node resource pressure. If worker1 is still intentionally cordoned from recovery and checks are healthy:

```bash
kubectl uncordon worker1
```

Verify `/api/jobs` again using the port-forward exercise. A successful check was recorded before the monitoring incident; after recovery it should be tested again rather than assumed.

## Install these tutorial files into your repository

Extract this archive outside the repository first. Copy the Markdown files from its `07-observability/` folder into the existing repository chapter directory. Keep `manifests/` intact. Review any existing README before replacing it.

Intended chapter layout:

```text
07-observability/
  README.md
  00-start-here.md
  01-cluster-health-and-events.md
  02-logs-and-restarts.md
  03-metrics-and-metrics-server.md
  04-helm-and-monitoring-stack.md
  05-troubleshooting-and-recovery.md
  06-grafana-dashboards.md
  07-prometheus-queries.md
  08-review-and-git.md
  manifests/
    metrics-server.yaml
    monitoring-defaults.yaml
    monitoring-values.yaml
```

Do not put chapter Markdown files at the repository root. The archive deliberately contains no replacement manifests.

## Review before committing

From `07-observability`:

```bash
git status --short
git diff -- manifests/monitoring-values.yaml
```

Untracked files do not appear in ordinary git diff; read them before staging. Check that no decoded credentials, token dumps or generated Secrets are included. The removed Metrics Server manifest is a retained exercise reference, not part of the active stack.

Stage the chapter only:

```bash
git add README.md [0-9][0-9]-*.md manifests/
git diff --cached --stat
git diff --cached --check
```

Inspect the staged content if necessary. Then:

```bash
git commit -m "Add chapter 07 observability tutorials and monitoring setup"
git push
```

The assistant has not run Git on your Mac; these are commands for your local checkout.

## Review questions

1. Why can a Pod be Running but only 2/3 ready?
2. What does --previous select, and what can it not retrieve?
3. Why is usage above requests allowed?
4. Why does exit code 137 alone not prove OOMKilled?
5. Why can Grafana work while kubectl top does not?
6. What is the difference between a chart, a values file and a rendered manifest?
7. Why did a failed Helm revision coexist with running resources?
8. What does uncordon do to Pods already running?
9. Why is up=1 not a complete application health test?
10. Why should a Pod memory total not be compared with one container's limit?
