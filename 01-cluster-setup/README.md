# 01 — Cluster setup

Follow [the main tutorial](../README.md) for creation, Linux preparation, containerd, kubeadm, Calico, and worker joining.

- `calico-installation.yaml` defines the lab Pod IP pool `10.244.0.0/16`.
- Replace the host IPs and CIDRs in the tutorial if your VM networking differs.
- Do not commit admin kubeconfigs or join tokens.
