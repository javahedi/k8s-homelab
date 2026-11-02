# 01 · Create the Ubuntu VMs

[← Chapter index](README.md) · [← Project overview](../README.md)

```bash
multipass launch 24.04 --name control-plane --cpus 2 --memory 2G --disk 20G
multipass launch 24.04 --name worker1 --cpus 1 --memory 1536M --disk 15G
multipass launch 24.04 --name worker2 --cpus 1 --memory 1536M --disk 15G
multipass list
```

Record *your actual* IP addresses using `multipass list`. This tutorial uses `192.168.252.2`, `.3`, and `.4`; they are examples from the original lab, **not guaranteed on another Mac**. Update commands and manifests to match your own VMs.

---

[← All cluster-setup chapters](README.md)
