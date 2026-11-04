# Module 02 — Kubernetes Workloads

[← Project overview](../README.md)

> **Core labs completed in the learning session, 3–4 November 2026.** A step-by-step learning journal for the three-node ARM64 homelab. Read in order. Commands run on the Mac from the repository root. Resource names/IPs are examples; inspect live state before rerunning.

## Learning chapters

- [00 · Start here](00-start-here.md)
- [01 · Pods: imperative and declarative](01-pods.md)
- [02 · Multi-container Pods](02-multi-container-pods.md)
- [03 · Labels and selectors](03-labels-and-selectors.md)
- [04 · ReplicaSets and scaling](04-replicasets.md)
- [05 · Deployments, rolling updates and rollback](05-deployments.md)
- [06 · Services, blue-green and canary](06-release-strategies.md)
- [07 · DaemonSets, Jobs and CronJobs](07-daemonsets-jobs-cronjobs.md)
- [08 · ConfigMaps and Secrets](08-configmaps-and-secrets.md)
- [09 · Requests, limits and probes](09-resources-and-probes.md)
- [10 · Scheduling: selectors, affinity and taints](10-scheduling.md)
- [11 · Build and deploy your own image](11-custom-image.md)
- [12 · Review, troubleshooting and publish](12-review-and-git.md)

## How to use this chapter

Start with 00 for terminal setup and conventions. Lessons include blueprint generation, YAML edits, verification, deliberate failures, recovery and explanations of why each resource exists. Manifest snippets are copied into `02-workloads/manifests/`; your existing files remain the working source. The documentation package intentionally contains no replacement manifests or Docker source files.

## Progress

- [x] Pods: imperative and declarative
- [x] Multi-container Pods and shared emptyDir
- [x] Labels and selectors
- [x] ReplicaSets and scaling
- [x] Deployments, rolling update and rollback
- [x] Services, blue-green and canary
- [x] DaemonSets, Jobs and CronJobs
- [x] ConfigMaps and Secrets through environment variables
- [x] Requests, limits, readiness and liveness
- [x] Node selectors, required affinity, taints and tolerations
- [x] Build, import and deploy a custom image

See review chapter for extensions not exercised, troubleshooting and Git publishing.
