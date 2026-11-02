# 02 · Prepare Linux Nodes

[← Chapter index](README.md) · [← Project overview](../README.md)

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

---

[← All cluster-setup chapters](README.md)
