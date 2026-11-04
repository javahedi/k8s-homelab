# 09 · Requests, limits and probes

[← Chapter index](README.md)

```bash
kubectl run health-demo -n workloads --image=nginx:stable --dry-run=client -o yaml > 02-workloads/manifests/health-demo.yaml
```

Replace resources: {} in its container with:

```yaml
      resources:
        requests:
          cpu: 50m
          memory: 32Mi
        limits:
          cpu: 200m
          memory: 128Mi
```

| Setting | Behavior |
|---|---|
| Requests | Scheduler accounts for these when fitting Pods; CPU also influences relative allocation under contention |
| CPU limit | CPU usage can be throttled |
| Memory limit | Exceeding the enforced limit can result in OOM termination |

50m = 0.05 CPU core; 200m = 0.2; Mi = mebibytes. Requests aren't a measurement of current consumption. This unequal request/limit setup is normally Burstable QoS; empty resources were BestEffort. Check rather than infer availability from live usage alone.

Add under the same container:

```yaml
      readinessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 2
        periodSeconds: 5
      livenessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 10
        periodSeconds: 5
```

Apply for a fresh Pod; if it exists, delete only health-demo before reapplying. Then wait/describe:

```bash
kubectl apply -f 02-workloads/manifests/health-demo.yaml
kubectl wait -n workloads --for=condition=Ready pod/health-demo --timeout=120s
kubectl describe pod health-demo -n workloads
```

| Probe | Failure consequence |
|---|---|
| Readiness | Container marked unready; normally excluded from Service traffic, no restart solely for readiness |
| Liveness | Kubelet restarts container after failure threshold |
| Startup | Allows startup time; gates readiness/liveness until success, restarts on exhausted failure allowance |

HTTP probes target Pod port directly; no Service needed. HTTP 200–399 is successful. Defaults observed: timeout 1s and failure threshold 3. Probes should check meaningful application health, not just any process.

## Deliberately fail readiness
Change ONLY readiness path to /not-found; keep liveness /. Recreate Pod and watch:

```bash
kubectl delete pod health-demo -n workloads
kubectl apply -f 02-workloads/manifests/health-demo.yaml
kubectl get pod health-demo -n workloads -w
```

Expect Running but 0/1 Ready, no restarts from readiness failures. Ctrl+C, describe: Events report HTTP 404. Restore readiness `/`, recreate and wait Ready. Preserve healthy paths in committed YAML.

Startup probes were explained, not exercised. Optional extension for a slow starter: use startupProbe with a suitable failureThreshold × periodSeconds startup allowance, then observe that liveness/readiness wait for its success. Don't mark optional extensions as previously verified.

---

[← Chapter index](README.md)
