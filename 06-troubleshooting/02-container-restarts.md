# 02 — CrashLoopBackOff

## What we actually observed

Our BusyBox Pod had empty current and previous logs. Its `describe` output contained:

```text
State: Waiting
  Reason: CrashLoopBackOff
Last State: Terminated
  Reason: Completed
  Exit Code: 0
```

No custom command appeared in the container description. The intended failing command had not reached the Pod configuration. BusyBox's default shell exited immediately without interactive input. With the default `restartPolicy: Always`, kubelet repeatedly restarted it.

**CrashLoopBackOff does not always mean a nonzero exit code.** A repeatedly exiting process can trigger restart backoff even after successful completion.

## Inspect

```bash
kubectl logs broken-command -n troubleshooting
kubectl logs broken-command -n troubleshooting --previous
kubectl describe pod broken-command -n troubleshooting
```

Check Command, Args, State, Last State, Exit Code, Restart Count, and Events. Empty logs are evidence to investigate, not proof that the container is healthy.

## Repaired manifest

The essential configuration in `manifests/broken-command.yaml` is:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: broken-command
  namespace: troubleshooting
spec:
  containers:
    - name: broken-command
      image: busybox:1.37
      command:
        - sh
        - -c
        - 'echo "Application running"; sleep 3600'
```

Pod commands cannot be changed directly on an existing Pod. For this disposable exercise Pod, we recreated it:

```bash
kubectl replace --force -f manifests/broken-command.yaml
kubectl get pod broken-command -n troubleshooting
kubectl logs broken-command -n troubleshooting
```

`replace --force` deletes and recreates the resource; it can interrupt service and changes the Pod's identity and potentially its IP. Our result was `1/1 Running` and `Application running`.

`sleep 3600` is a lab placeholder. It exits after an hour, and the Always policy restarts it. A real server should run its long-lived application process.

## Optional: reproduce an explicit failure

Use a different Pod name so the repaired Pod remains available:

```bash
kubectl run explicit-failure -n troubleshooting --image=busybox:1.37 --command -- sh -c 'echo "ERROR: startup failed"; exit 1'
kubectl logs explicit-failure -n troubleshooting
kubectl describe pod explicit-failure -n troubleshooting
```

This example deliberately exits with code 1. Remove it afterward:

```bash
kubectl delete pod explicit-failure -n troubleshooting
```
