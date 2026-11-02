# 00 · Prerequisites

[← Chapter index](README.md) · [← Project overview](../README.md)

- An Apple Silicon Mac, Multipass, and a terminal; Homebrew is useful for local `kubectl`.
- Internet for Ubuntu APT packages and container images.
- At least ~45 GiB of free host disk is preferable for three 15–20 GiB virtual disks (actual host use can be sparse).
- `multipass version`, `uname -m`, `sysctl -n hw.memsize` to examine your Mac.

**All `multipass` commands below run on the Mac**, unless clearly marked otherwise. This is a fresh-cluster tutorial; don't rerun `kubeadm init` against an existing initialized control plane.

---

[← All cluster-setup chapters](README.md)
