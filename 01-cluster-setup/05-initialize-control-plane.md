# 05 · Initialize the Control Plane

[← Chapter index](README.md) · [← Project overview](../README.md)

Choose **nonoverlapping** VM, Pod, and Service CIDRs. Our Multipass network is `192.168.252.0/24`; Pod CIDR is `10.244.0.0/16`.

```bash
multipass exec control-plane -- sudo kubeadm init \
  --kubernetes-version=v1.37.2 \
  --apiserver-advertise-address=192.168.252.2 \
  --pod-network-cidr=10.244.0.0/16 \
  --cri-socket=unix:///run/containerd/containerd.sock
```

**Run `kubeadm init` only on the control-plane node.** Then configure the regular `ubuntu` user:

```bash
multipass exec control-plane -- bash -c '
  mkdir -p "$HOME/.kube"
  sudo cp /etc/kubernetes/admin.conf "$HOME/.kube/config"
  sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"
  chmod 600 "$HOME/.kube/config"
'
multipass exec control-plane -- kubectl get nodes
```

Initially `NotReady` is normal without a Pod CNI. CoreDNS may be `Pending`.

---

[← All cluster-setup chapters](README.md)
