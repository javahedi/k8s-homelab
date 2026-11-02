# 07 · Join Worker Nodes

[← Chapter index](README.md) · [← Project overview](../README.md)

Generate a fresh worker join command on the control plane:

```bash
multipass exec control-plane -- sudo kubeadm token create --print-join-command
```

**Never commit the bootstrap token.** Run the generated command on **worker1**, then on **worker2**, using the real token and CA hash. In the examples below placeholders are deliberate:

```bash
multipass exec worker1 -- sudo kubeadm join 192.168.252.2:6443 \
  --token '<TOKEN>' \
  --discovery-token-ca-cert-hash 'sha256:<CA-HASH>' \
  --cri-socket unix:///run/containerd/containerd.sock

# Once worker1 is Ready, repeat with worker2:
multipass exec worker2 -- sudo kubeadm join 192.168.252.2:6443 \
  --token '<TOKEN>' \
  --discovery-token-ca-cert-hash 'sha256:<CA-HASH>' \
  --cri-socket unix:///run/containerd/containerd.sock
```

Validate on the control plane:

```bash
multipass exec control-plane -- kubectl get nodes -o wide
multipass exec control-plane -- kubectl get pods -n calico-system -o wide
```

**The actual lab finished with three `Ready` nodes.** A joined worker can be temporarily `NotReady` while Calico starts. If it stays there, see the [disk pressure case study](../06-troubleshooting/worker-disk-pressure.md).

---

[← All cluster-setup chapters](README.md)
