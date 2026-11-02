# 03 · Install and Configure containerd

[← Chapter index](README.md) · [← Project overview](../README.md)

`containerd` is a **container runtime**, not a collection of installed application containers. Docker is a broader developer platform; Kubernetes uses the CRI interface to ask containerd to run containers in Pods.

```bash
for node in control-plane worker1 worker2; do
  multipass exec "$node" -- sudo apt-get update
  multipass exec "$node" -- sudo apt-get install -y containerd
  multipass exec "$node" -- containerd --version
done
```

For the recorded **containerd 2.2.1** setup, create a default config on each VM and enable the systemd cgroup driver:

```bash
for node in control-plane worker1 worker2; do
  multipass exec "$node" -- sudo bash -c '
    mkdir -p /etc/containerd
    if [ -f /etc/containerd/config.toml ]; then
      cp /etc/containerd/config.toml /etc/containerd/config.toml.bak
    fi
    containerd config default > /etc/containerd/config.toml
    sed -i "s/SystemdCgroup = false/SystemdCgroup = true/" /etc/containerd/config.toml
    systemctl restart containerd
  '
done
```

In containerd 2.x the setting is under `[plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]`. **Do not blindly replace configs on existing configured systems.** Validate each node:

```bash
for node in control-plane worker1 worker2; do
  echo "===== $node ====="
  multipass exec "$node" -- grep SystemdCgroup /etc/containerd/config.toml
  multipass exec "$node" -- systemctl is-active containerd
  multipass exec "$node" -- sudo ctr plugins ls | grep cri.v1
done
```

Expected: `SystemdCgroup = true`, `active`, and CRI plugin status `ok`.

---

[← All cluster-setup chapters](README.md)
