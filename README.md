# k8s-homelab — My CKA Hands-On Lab ☸️

**A reproducible, beginner-friendly, three-node Kubernetes lab on an Apple Silicon Mac.** This tutorial documents a real installation, including a disk-pressure failure and its repair. The objective is to *understand each command*, not just copy and paste it.

> **Lab verified:** 2 November 2026 · macOS ARM64 · Multipass 1.17.0 · Ubuntu 24.04 · Kubernetes v1.37.2 · containerd 2.2.1 · Calico v3.33.0. Versions and networking should be checked before using this on another machine. This is a learning environment, **not** a production security blueprint.

## The result

```text
Mac (kubectl client)
    |
    | HTTPS :6443
    v
control-plane   192.168.252.2   Ready   2 vCPU / 2 GiB
    |
    +--- worker1   192.168.252.3   Ready   1 vCPU / 1.5 GiB
    +--- worker2   192.168.252.4   Ready   1 vCPU / 1.5 GiB

Pod CIDR:     10.244.0.0/16
Service CIDR: 10.96.0.0/12
CNI:          Calico
```

**Important:** This setup uses about 5 GiB of guest RAM on an 8 GiB Mac. Keep other applications light. The 1.5 GiB workers are below Kubernetes' recommended 2 GiB/node and may struggle with heavier workloads. If you have more memory, allocate at least 2 GiB to each worker. We use **15 GiB disks for workers**, not 5 GiB.

## Roadmap

- [x] 3 VMs with Multipass
- [x] Hostname resolution, swap, kernel modules, sysctl, firewall checks
- [x] Install and configure containerd
- [x] Install kubeadm, kubelet and kubectl
- [x] Initialize the control plane
- [x] Install Calico and verify CoreDNS
- [x] Join two workers; verify all nodes Ready
- [x] Access the cluster with kubectl on macOS (using `--kubeconfig`)
- [ ] Set a convenient macOS kubeconfig/context and shell completion
- [ ] Workloads, networking, storage, RBAC, upgrades, and troubleshooting practice

## 0 — Requirements

- An Apple Silicon Mac, Multipass, and a terminal; Homebrew is useful for local `kubectl`.
- Internet for Ubuntu APT packages and container images.
- At least ~45 GiB of free host disk is preferable for three 15–20 GiB virtual disks (actual host use can be sparse).
- `multipass version`, `uname -m`, `sysctl -n hw.memsize` to examine your Mac.

**All `multipass` commands below run on the Mac**, unless clearly marked otherwise. This is a fresh-cluster tutorial; don't rerun `kubeadm init` against an existing initialized control plane.

## 1 — Create Ubuntu VMs

```bash
multipass launch 24.04 --name control-plane --cpus 2 --memory 2G --disk 20G
multipass launch 24.04 --name worker1 --cpus 1 --memory 1536M --disk 15G
multipass launch 24.04 --name worker2 --cpus 1 --memory 1536M --disk 15G
multipass list
```

Record *your actual* IP addresses using `multipass list`. This tutorial uses `192.168.252.2`, `.3`, and `.4`; they are examples from the original lab, **not guaranteed on another Mac**. Update commands and manifests to match your own VMs.

## 2 — Prepare all nodes

### Hosts file

The `/etc/hosts` file is a local mapping of names to addresses, **not a DNS server**. In the original lab, these entries were added on each VM:

```text
192.168.252.2 control-plane
192.168.252.3 worker1
192.168.252.4 worker2
```

To reproduce with your *own* addresses, edit `/etc/hosts` on each VM (for example using `sudo nano /etc/hosts`) and add the three mappings, without duplicating names. Then test:

```bash
multipass exec worker1 -- getent hosts control-plane
multipass exec worker1 -- ping -c 3 worker2
```

`getent` tests name resolution; `ping` also checks basic connectivity. Kubernetes will later use CoreDNS for Service discovery, a separate mechanism.

### Swap

```bash
for node in control-plane worker1 worker2; do
  multipass exec "$node" -- sudo swapoff -a
  multipass exec "$node" -- swapon --show
  multipass exec "$node" -- bash -c "grep -E '^[^#].*[[:space:]]swap[[:space:]]' /etc/fstab || true"
done
```

We use swap-off for this simple kubeadm lab. If `/etc/fstab` contains an active swap entry, disable that entry *carefully* and re-check after reboot. Modern Kubernetes can support configured swap, but that isn't the setup here.

### Kernel modules

```bash
for node in control-plane worker1 worker2; do
  multipass exec "$node" -- sudo bash -c '
    printf "overlay\nbr_netfilter\n" > /etc/modules-load.d/k8s.conf
    modprobe overlay
    modprobe br_netfilter
  '
done
```

`overlay` is commonly used for container filesystem layers; `br_netfilter` allows bridged traffic through netfilter processing. Check with `lsmod | grep -E '^(overlay|br_netfilter)'`.

### sysctl

```bash
for node in control-plane worker1 worker2; do
  multipass exec "$node" -- sudo bash -c '
    cat > /etc/sysctl.d/99-kubernetes.conf <<EOF_SYSCTL
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF_SYSCTL
    sysctl --system >/dev/null
  '
done
```

Check with `sysctl net.ipv4.ip_forward` and `sysctl net.bridge.bridge-nf-call-iptables` on each VM. Forwarding permits packet routing; it doesn't install a CNI.

### Firewall

```bash
for node in control-plane worker1 worker2; do
  echo "===== $node ====="
  multipass exec "$node" -- sudo ufw status
done
```

In the original local lab UFW was inactive. If a firewall is active, configure the necessary Kubernetes and Calico ports rather than blindly disabling it. Don't publicly expose etcd or the API server.

## 3 — Install containerd

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

## 4 — Install kubeadm, kubelet and kubectl

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

## 5 — Initialize control plane (once)

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

## 6 — Install Calico v3.33.0

For Kubernetes v1.37, the official [Calico v3.33 operator guide](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises) uses its newer CRDs and the Tigera Operator.

```bash
multipass exec control-plane -- kubectl create -f \
  https://raw.githubusercontent.com/projectcalico/calico/v3.33.0/manifests/v3_projectcalico_org.yaml
multipass exec control-plane -- kubectl create -f \
  https://raw.githubusercontent.com/projectcalico/calico/v3.33.0/manifests/tigera-operator.yaml
```

A CRD defines an API resource type. The operator continuously reconciles resources. Our custom `Installation` is in [`01-cluster-setup/calico-installation.yaml`](01-cluster-setup/calico-installation.yaml), with Pod CIDR **10.244.0.0/16**. Do **not** apply the upstream default custom-resources manifest as well; this tutorial uses its own `Installation` resource.

```bash
multipass transfer 01-cluster-setup/calico-installation.yaml control-plane:/tmp/calico-installation.yaml
multipass exec control-plane -- kubectl apply -f /tmp/calico-installation.yaml
multipass exec control-plane -- kubectl get tigerastatus
multipass exec control-plane -- kubectl get pods -n calico-system
multipass exec control-plane -- kubectl get pods -n kube-system
multipass exec control-plane -- kubectl get nodes
```

Wait for Calico status `AVAILABLE=True`, `PROGRESSING=False`, `DEGRADED=False`, both CoreDNS Pods Running, and the control-plane node Ready. The operator may take time to settle.

## 7 — Join worker nodes

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

**The actual lab finished with three `Ready` nodes.** A joined worker can be temporarily `NotReady` while Calico starts. If it stays there, see the [disk pressure case study](06-troubleshooting/worker-disk-pressure.md).

## 8 — kubectl directly from the Mac

Our Mac already had kubectl v1.36.1, compatible with the v1.37 server (within one minor version). Don't overwrite your existing `~/.kube/config`.

```bash
mkdir -p ~/.kube
chmod 700 ~/.kube
multipass exec control-plane -- sudo cp /etc/kubernetes/admin.conf /home/ubuntu/k8s-homelab.yaml
multipass exec control-plane -- sudo chown ubuntu:ubuntu /home/ubuntu/k8s-homelab.yaml
multipass exec control-plane -- chmod 600 /home/ubuntu/k8s-homelab.yaml
multipass transfer control-plane:/home/ubuntu/k8s-homelab.yaml ~/.kube/k8s-homelab.yaml
chmod 600 ~/.kube/k8s-homelab.yaml
multipass exec control-plane -- rm /home/ubuntu/k8s-homelab.yaml
```

Now verify:

```bash
kubectl --kubeconfig ~/.kube/k8s-homelab.yaml get nodes
```

**To avoid typing `--kubeconfig` each time**, for the *current zsh session*:

```bash
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
kubectl get nodes
```

To make that choice persistent, add exactly this line to `~/.zshrc` if you only want to use this lab context:

```bash
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
```

Then `source ~/.zshrc`. **If you already use other clusters**, setting `KUBECONFIG` this way hides the default kubeconfig; consider a merged config or explicit context switching instead. For CKA practice, add to `~/.zshrc`:

```bash
source <(kubectl completion zsh)
alias k=kubectl
compdef k=kubectl
```

The kubeconfig contains powerful admin credentials. Do not store it in the repo, screenshots, or chat.

## What I learned

- **VM vs container vs Pod:** A VM includes its own OS kernel. A container typically shares the host's Linux kernel. A Pod is Kubernetes' smallest deployable unit, usually containing one container.
- **kubeadm init vs join:** `init` bootstraps a control plane. `join` securely attaches workers.
- **Control plane components:** API server, scheduler, controller manager, etcd.
- **CNI and DNS:** Calico enables Pod networking; CoreDNS provides Kubernetes Service discovery; `/etc/hosts` is just local hostname mapping.
- **Disk troubleshooting:** `NotReady` requires inspecting **node Conditions** and **events**, not guessing. We fixed a 5 GiB VM disk incorrectly provisioned for worker1.

## Next experiments

1. Create Nginx Pods imperatively and declaratively.
2. Deploy, scale, roll out and roll back a Deployment.
3. Test Services and DNS between Pods.
4. Create ConfigMaps, Secrets, Jobs, CronJobs and NetworkPolicies.
5. Practice `kubectl describe`, logs, events, and disk-pressure troubleshooting.
6. Move into storage, RBAC, kubeadm upgrades, and etcd backup/restore.

## References

- [Kubernetes kubeadm installation](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)
- [Kubernetes container runtime configuration](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)
- [Kubernetes kubeadm init](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-init/)
- [Kubernetes kubeadm join](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/)
- [Calico operator-based installation](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises)
- [Kubernetes kubectl version skew](https://kubernetes.io/releases/version-skew-policy/)

**Disclaimer:** Lab-only guidance. Adjust network ranges, RAM, firewall controls, package versions and certificates for your environment.
