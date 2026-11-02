# Module 01 — Cluster Setup

> **Status: completed and verified on 2 November 2026.** Three Kubernetes v1.37.2 nodes reached `Ready`. Read chapters in order; the instructions describe a fresh lab, not an idempotent installer.

## Learning chapters

- [00 · Prerequisites](00-prerequisites.md)
- [01 · Create the Ubuntu VMs](01-create-vms.md)
- [02 · Prepare Linux Nodes](02-prepare-nodes.md)
- [03 · Install and Configure containerd](03-install-containerd.md)
- [04 · Install Kubernetes Tools](04-install-kubernetes-tools.md)
- [05 · Initialize the Control Plane](05-initialize-control-plane.md)
- [06 · Install Calico Networking](06-install-calico.md)
- [07 · Join Worker Nodes](07-join-workers.md)
- [08 · Control Kubernetes from macOS](08-macos-kubectl.md)

## Supporting materials

- [Calico Installation manifest](calico-installation.yaml) — example custom resource using Pod CIDR `10.244.0.0/16`
- [Architecture](../docs/architecture.md) — node topology and request flow
- [Troubleshooting: DiskPressure](../06-troubleshooting/worker-disk-pressure.md) — actual worker1 diagnosis and repair

## Verification checklist

- [x] Three Ubuntu ARM64 VMs provisioned
- [x] Linux prerequisites and containerd installed
- [x] kubeadm control plane initialized
- [x] Calico and CoreDNS functioning
- [x] Both workers joined and all nodes Ready
- [x] `kubectl` works from macOS using a dedicated kubeconfig
- [ ] Optional: persistent kubeconfig selection and shell completion
- [ ] Optional: regenerate a join token as a separate practice exercise

**Safety:** Never commit `admin.conf`, private keys, join tokens, or any kubeconfig to the repository.
