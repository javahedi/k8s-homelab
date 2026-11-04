# 12 · Review, troubleshooting and publish

[← Chapter index](README.md)

## What was completed?
All eleven core topics were practiced in the live learning session. Startup probes, preferred affinity and ConfigMap file mounts were explanations/extensions rather than completed experiments. This tutorial is a reusable reconstruction, not evidence of a new automated test run.

| Symptom | Check / explanation |
|---|---|
| localhost:8080 refused from kubectl | Kubeconfig missing or wrong endpoint; export correct file |
| Namespace typo | Inspect namespaces; run doesn't create one |
| Running but 0/1 | Describe probes/events; Running differs from Ready |
| curl not found in observer | BusyBox has wget; select correct tool/container |
| Job completed despite data error | Last shell command exited 0; use && for dependency chains |
| Pending with worker99 | No matching node; preemption doesn't repair labels |
| Pending on tainted required node | Add matching toleration or remove intended practice taint |
| YAML parse error | Align siblings; spaces, not tabs |
| ConfigMap changed but environment old | Recreate containers to reload environment |
| crictl missing | Verify with installed ctr; imports may already be valid |
| ErrImageNeverPull | Verify image exact name/tag on assigned worker |
| Port already allocated | Use an unused local port or stop your own old forward/preview |

## Inspect the whole lab

```bash
kubectl get nodes
kubectl get deployment,rs,ds,job,cronjob,service -n workloads
kubectl get pods -n workloads -o wide
kubectl get pods -n workloads -o custom-columns='POD:.metadata.name,NODE:.spec.nodeName,CONTAINERS:.spec.containers[*].name'
kubectl get nodes -o custom-columns='NODE:.metadata.name,TAINTS:.spec.taints'
```

Final checks: hello-cron suspended; worker2 training taint removed; readiness path restored; placement affinity valid; Deployment rollback image nginx:stable; custom image imported on both workers. Some lab resources intentionally remain running. The 8 GB Mac has finite capacity: scale down chosen Deployments or delete only named disposable resources if needed. Do not delete workloads namespace unless intentionally discarding every exercise in it. Do not remove Calico/CoreDNS/kube-proxy to save space.

## Publish the learning work
Review actual files before staging. This documentation pack does not replace your existing manifests or custom website.

```bash
git status --short
git diff -- 02-workloads
```

Only the deliberately fake practice Secret belongs in a public teaching example. Do not stage actual credentials, kubeconfigs, private keys, SMTP passwords or image archives. If app-credentials.yaml contains anything other than fake example values, exclude it.

```bash
git add 02-workloads
git diff --cached --stat
git diff --cached -- 02-workloads
git commit -m "Document Chapter 02 Kubernetes workloads and lab exercises"
git push origin main
```

Your earlier status showed main ahead of origin/main by two commits; push will publish those along with the new commit. Don't force push if rejected; inspect fetch/status and resolve divergence. In the ROOT README learning-path table change only Workloads status from Planned to core labs completed/documented. Leave unrelated chapters and historical configuration untouched.

## Return later
Open this chapter index, load kubeconfig, verify nodes, then inspect current resources before rerunning creation. Generated names/IPs aren't persistent references. Use unique selectors to scope experiments. Keep desired settings in YAML; don't bulk-apply experimental files without reading their effects.

## Self-check questions
1. Why can observer reach its local Nginx using localhost but BLUE using web?
2. Which controller replaces a deleted Deployment Pod?
3. Does a toleration force placement onto a particular node?
4. Why can Completed show 0/1 and still be successful?
5. Why won't a Mac-built image automatically exist on a worker?
6. Why do three BLUE replicas plus one GREEN only approximate a traffic ratio?
7. What survives a container restart but not Pod deletion in our shared-volume exercise?

Answers: same-Pod network versus Service/DNS; ReplicaSet under Deployment; no; successful process exit, no running container; separate image stores; connection routing isn't weighted release control; emptyDir.

## Official references
- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [ReplicaSets](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Resources](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Node assignment](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Taints](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Docker build](https://docs.docker.com/build/concepts/overview/)

---

[← Chapter index](README.md)
