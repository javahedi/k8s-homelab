# 04 · Install Kubernetes Tools

[← Chapter index](README.md) · [← Project overview](../README.md)

Version-specific APT repository: **v1.37**. Use the [Kubernetes official instructions](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) for updated versions.

```bash
for node in control-plane worker1 worker2; do
  multipass exec "$node" -- sudo apt-get update
  multipass exec "$node" -- sudo apt-get install -y ca-certificates curl gpg
  multipass exec "$node" -- sudo bash -c '
    mkdir -p -m 755 /etc/apt/keyrings
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.37/deb/Release.key \
      | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.37/deb/ /" \
      > /etc/apt/sources.list.d/kubernetes.list
  '
  multipass exec "$node" -- sudo apt-get update
  multipass exec "$node" -- sudo apt-get install -y kubelet kubeadm kubectl
  multipass exec "$node" -- sudo apt-mark hold kubelet kubeadm kubectl
done
```

Verify `kubeadm version -o short`, `kubelet --version`, and `kubectl version --client` on each VM. In our lab: `v1.37.2` throughout. `kubeadm` bootstraps/joins nodes; `kubelet` runs on nodes; `kubectl` is the CLI client.

---

[← All cluster-setup chapters](README.md)
