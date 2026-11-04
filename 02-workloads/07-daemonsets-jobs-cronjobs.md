# 07 · DaemonSets, Jobs and CronJobs

[← Chapter index](README.md)

| Resource | Purpose | API |
|---|---|---|
| DaemonSet | One Pod per eligible node | apps/v1 |
| Job | Run a task to completion | batch/v1 |
| CronJob | Create Jobs on a schedule | batch/v1 |

## DaemonSets

```bash
kubectl get ds -A
```

In our lab calico-node, csi-node-driver and kube-proxy each had three ready Pods. System components tolerate the control-plane restrictions; our reporter normally runs on two workers. DaemonSets are used for node agents, not fixed website replica counts.

Save `node-reporter.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-reporter
  namespace: workloads
spec:
  selector:
    matchLabels:
      app: node-reporter
  template:
    metadata:
      labels:
        app: node-reporter
    spec:
      containers:
        - name: reporter
          image: busybox:1.37
          command: [sh, -c]
          args:
            - |
              while true; do
                echo "Reporter running in Pod: $HOSTNAME"
                sleep 30
              done
```

```bash
kubectl apply -f 02-workloads/manifests/node-reporter.yaml
kubectl get ds node-reporter -n workloads
kubectl get pods -n workloads -l app=node-reporter -o wide
kubectl logs -n workloads -l app=node-reporter --prefix --tail=3
```

No replicas field: eligibility determines count. HOSTNAME normally identifies the Pod, not physical node name.

## Jobs and exit status

```bash
kubectl create job hello-job -n workloads --image=busybox:1.37 --dry-run=client -o yaml -- sh -c 'echo "Job started" && date && echo "Task finished"' > 02-workloads/manifests/hello-job.yaml
kubectl apply -f 02-workloads/manifests/hello-job.yaml
kubectl wait -n workloads --for=condition=Complete job/hello-job --timeout=120s
kubectl logs -n workloads job/hello-job
kubectl get jobs,pods -n workloads
```

Completed with 0/1 ready is normal: the process exited. Generated restartPolicy Never prevents restarting that container inside its Pod; the Job controller may create retries as allowed by backoffLimit.

Our typo `data` instead of `date` failed, but semicolon-separated commands continued to a successful final echo. The shell returned 0, so Kubernetes marked the Job complete. Kubernetes judges exit status, not whether logs contain the word error. `&&` stops that chain on failure. To correct a completed Job's generally immutable Pod template, delete only hello-job and reapply the corrected manifest. Applying an unchanged completed Job doesn't rerun it.

## CronJobs

```bash
kubectl create cronjob hello-cron -n workloads --image=busybox:1.37 --schedule='* * * * *' --dry-run=client -o yaml -- sh -c 'date && echo "Scheduled task finished"' > 02-workloads/manifests/hello-cron.yaml
kubectl apply -f 02-workloads/manifests/hello-cron.yaml
kubectl get jobs -n workloads -w
```

Wait for a new hello-cron-... Job, then Ctrl+C stops WATCHING only. Read its logs with `kubectl logs -n workloads job/ACTUAL_JOB_NAME`.

| Position | Field |
|---|---|
| 1 | Minute |
| 2 | Hour |
| 3 | Day of month |
| 4 | Month |
| 5 | Day of week |

Five stars means every minute, not every second. Controller timezone applies unless spec.timeZone is explicitly configured; the Mac timezone does not choose it. Scheduling is not a substitute for designing tasks safe to retry.

After the exercise add `suspend: true` under top-level spec alongside schedule, apply, then check:

```bash
kubectl get cronjob hello-cron -n workloads
```

Expect SUSPEND True; ACTIVE 0 once any existing run finishes. Suspension stops future scheduled starts, not existing Jobs. Keep the saved manifest suspended to avoid re-enabling it accidentally. History limits can retain only a chosen number of successful/failed Jobs.

---

[← Chapter index](README.md)
