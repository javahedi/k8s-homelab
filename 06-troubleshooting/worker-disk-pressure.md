# Case study — Worker `NotReady` due to DiskPressure

## Symptoms

After `kubeadm join`, `worker1` registered but remained `NotReady`. Calico was initializing and `kubectl describe node worker1` showed:

```text
DiskPressure   True    KubeletHasDiskPressure
Ready          False   NetworkPluginNotReady: cni plugin not initialized
Taints: node.kubernetes.io/disk-pressure:NoSchedule
```

The cause was **not simply Calico startup delay**. The filesystem was full:

```text
$ multipass exec worker1 -- df -h /
Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sda1   3.9G  3.8G      0  100%  /
```

`multipass info worker1` and `lsblk` showed only a **5 GiB disk**, mistakenly used instead of 15 GiB.

## Recovery performed

1. Stop the affected worker (not the control plane):

   ```bash
   multipass stop worker1
   multipass set local.worker1.disk=15G
   multipass start worker1
   ```

2. Check if root partition/filesystem automatically expanded:

   ```bash
   multipass exec worker1 -- lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
   multipass exec worker1 -- df -h /
   ```

3. On this worker, `sda` grew to 15 GiB but `sda1` stayed at 4 GiB. `growpart -N` was first used as a **dry run**:

   ```bash
   multipass exec worker1 -- sudo growpart -N /dev/sda 1
   ```

4. After confirming the partition map, the real change and filesystem growth:

   ```bash
   multipass exec worker1 -- sudo growpart /dev/sda 1
   multipass exec worker1 -- sudo resize2fs /dev/sda1
   ```

   **Caution:** Back up anything valuable before partition changes. These exact commands fit an ext4 root filesystem on `/dev/sda1`; do not blindly reuse them with other layouts/filesystems.

5. Confirm disk space and Kubernetes recovery:

   ```bash
   multipass exec worker1 -- df -h /
   multipass exec control-plane -- kubectl get nodes -o wide
   multipass exec control-plane -- kubectl get pods -n calico-system -o wide
   ```

## Verified outcome

```text
/dev/sda1  14G  3.7G  9.9G  28% /
control-plane   Ready
worker1         Ready
```

Calico's `calico-node` on worker1 became `1/1 Running` and the CSI driver `2/2 Running`.

## CKA lesson

Don't confuse **registered** with **Ready**. Investigate `kubectl describe node`, node conditions, taints, CNI Pods, `df -h`, `df -i`, and `lsblk`. A virtual disk resize is not necessarily a partition/filesystem resize. `growpart -N` only previews changes.
