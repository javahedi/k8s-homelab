# Architecture and learning notes

| VM | IP in verified lab | Role | vCPU | RAM | Disk |
|---|---|---|---:|---:|---:|
| control-plane | 192.168.252.2 | API, scheduler, controllers, etcd | 2 | 2 GiB | 20 GiB planned |
| worker1 | 192.168.252.3 | Workloads | 1 | 1.5 GiB | 15 GiB (corrected from 5 GiB) |
| worker2 | 192.168.252.4 | Workloads | 1 | 1.5 GiB | 15 GiB |

Pod IP pool: `10.244.0.0/16`; standard kubeadm Service CIDR: `10.96.0.0/12`.

## Control flow

```text
Mac kubectl -> API server (control-plane) -> cluster state / etcd
                             |
                        scheduler
                             |
                      kubelet (node)
                             |
                      containerd / CRI
                             |
                           runc
                             |
                           Pod
```

`/etc/hosts` helps VM hostname resolution. CoreDNS resolves names inside the Kubernetes cluster. Calico handles Pod network interfaces/routing and network policies.

See the main README for commands and the disk-pressure case study for debugging.
