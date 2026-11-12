# 05 — Troubleshooting and recovery: the actual incident

This is a case study, not a script to rerun on a healthy cluster.

## 1. Installation did not become ready

Most monitoring components were ready, but Grafana stayed 2/3 ready. Its main container was not serving `/api/health` on port 3000. Liveness failures restarted it.

```bash
kubectl logs -n monitoring deployment/monitoring-grafana -c grafana --tail=60
kubectl logs -n monitoring deployment/monitoring-grafana -c grafana --previous --tail=60
kubectl describe pod -n monitoring <grafana-pod>
```

We initially extended the liveness delay to test slow startup. Later OOMKilled evidence showed memory was also a real problem. More waiting alone could not solve the overloaded Node.

## 2. Memory and placement

worker1 reached all reported memory and a load average of 47.61 on one CPU. Load measures runnable/uninterruptible tasks, not CPU percentage; this was severe contention. worker2 had substantially more room.

The original 256Mi Grafana limit was too tight. We increased it to 512Mi and selected worker2. We used Recreate to avoid overlapping old/new Grafana Pods during updates. Requests influence placement; actual memory consumption can exceed them.

## 3. Strategy validation conflict

Changing a live Deployment from RollingUpdate to Recreate left an incompatible rollingUpdate field. Helm upgrades were rejected. Adding null to values did not remove the live conflict in that attempt.

The one-time correction was:

```bash
kubectl patch deployment monitoring-grafana -n monitoring \
  --type=json \
  -p='[{"op":"remove","path":"/spec/strategy/rollingUpdate"},{"op":"replace","path":"/spec/strategy/type","value":"Recreate"}]'
```

This exact remove operation requires that field to exist. Do not repeat blindly. Inspect `kubectl get deployment monitoring-grafana -n monitoring -o yaml` first if facing a similar issue.

The saved override retained Recreate and rollingUpdate: null; then Helm was rerun.

## 4. Node recovery

Old Pods remained Terminating and events included NodeNotReady and TaintManagerEviction. Kubernetes briefly reporting Ready did not establish resource recovery.

We cordoned and restarted worker1:

```bash
kubectl cordon worker1
multipass restart worker1 --timeout 120
```

This interrupted application/database service on that Node. It did not delete the VM disk. The PostgreSQL host-path data remained tied to worker1. We did not force-delete terminating Pods.

```bash
multipass list
kubectl get nodes
kubectl get pods -n jobs-demo -o wide
kubectl get pods -n monitoring -o wide
multipass info worker1 worker2
```

Eventually Grafana started on worker2, all three containers became ready, and worker1 recovered. Once stable, restore scheduling:

```bash
kubectl uncordon worker1
```

Uncordon does not rebalance existing Pods. Cordon prevents ordinary new scheduling; it does not stop existing containers. DaemonSets and already-bound Pods require separate consideration.

## 5. Reconcile Helm

The interrupted operation left Helm revision 5 marked failed: context canceled, even after workloads recovered. A subsequent upgrade using the saved values succeeded: revision 6, deployed.

## Lessons

- Inspect logs, termination reasons, events and Node resources together.
- A failed Helm operation is not a rollback guarantee.
- Avoid many overlapping retries or manual mutations.
- Pod-level memory and container-level limits are different scopes.
- Keep the final intended configuration in the values file.
- Temporary storage means Pod replacement can lose monitoring history and manual dashboard changes.
