# 06 — Basic node health checks

## Enter worker1 from the Mac

```bash
multipass shell worker1
```

## Run inside Ubuntu worker1

```bash
sudo systemctl status kubelet containerd --no-pager
sudo systemctl is-active kubelet containerd
sudo journalctl -u kubelet -n 20 --no-pager
sudo journalctl -u containerd -n 20 --no-pager
```

Our output showed both services `active (running)`.

| Component | Role |
|---|---|
| kubelet | Reconciles assigned Pods and reports their status |
| containerd | Pulls images and runs containers through the runtime interface |

Messages such as RemoveContainer, CreateContainer, and StartContainer can occur during normal lifecycle operations. An informational message alone does not establish a fault. If a line is truncated, add `-l` to `systemctl status`.

An active process is only a basic health check; it does not prove every Pod or network route works. For a real node failure, correlate service logs with node conditions and events.

## Return to the Mac

```bash
exit
kubectl get nodes
kubectl describe node worker1
```

In `describe`, inspect Ready, MemoryPressure, DiskPressure, PIDPressure, Taints, and Events. Restart a node service only when the diagnosis supports it. We did not stop or restart kubelet/containerd during this exercise.
