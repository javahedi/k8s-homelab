# Cluster architecture

[← Project overview](../README.md)

## Topology

```mermaid
flowchart TB
    Mac["Apple Silicon Mac<br/>8 CPU / 8 GB RAM<br/>kubectl client"]
    MP["Multipass virtual network<br/>192.168.252.0/24"]
    CP["control-plane<br/>192.168.252.2<br/>2 vCPU / 2 GiB RAM<br/>API server · etcd · scheduler · controllers"]
    W1["worker1<br/>192.168.252.3<br/>1 vCPU / 1.5 GiB RAM"]
    W2["worker2<br/>192.168.252.4<br/>1 vCPU / 1.5 GiB RAM"]
    Mac -->|HTTPS 6443| CP
    MP --- CP
    MP --- W1
    MP --- W2
    CP -.->|cluster coordination| W1
    CP -.->|cluster coordination| W2
```

## Container execution

```mermaid
flowchart LR
    User["kubectl"] --> API["kube-apiserver"]
    API --> Schedule["Scheduler / controllers"]
    Schedule --> K["kubelet on node"]
    K -->|CRI| C["containerd"]
    C --> R["runc"]
    R --> P["Pod containers"]
```

## Verified configuration

| Component | Version or setting |
|---|---|
| Host | Apple Silicon, ARM64, 8 GB RAM |
| Virtualization | Multipass 1.17.0 + Ubuntu 24.04 |
| Kubernetes | v1.37.2, kubeadm |
| Runtime | containerd 2.2.1, systemd cgroups |
| CNI | Calico v3.33.0 via Tigera Operator |
| Pod CIDR | `10.244.0.0/16` |
| Service CIDR | `10.96.0.0/12` |
| Worker disks | 15 GB virtual disk, approximately 14 GB root filesystem |

These are the *recorded* lab addresses. New Multipass deployments may use different addresses. The Mac has limited RAM, so heavyweight monitoring stacks should not be installed without sizing adjustments.
