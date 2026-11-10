# 07 — kubeadm upgrade assessment

## Separate components

| Component | Job |
|---|---|
| kubeadm | Installation/upgrade tool |
| API server, scheduler, controller manager | Control-plane services |
| kubelet | Node agent |
| kubectl | API client |

Installing kubeadm alone does not upgrade the cluster.
Upgrade the first control-plane, remaining control-planes if any, then workers.
Do not skip minor releases; check the target version's guide and version-skew rules.

## Assessment completed

Inside control-plane:

```bash
kubeadm version -o short
kubelet --version
kubectl version --client
sudo kubeadm upgrade plan
apt-cache madison kubeadm
```

kubectl uses a version subcommand, not --version.
apt-cache lists versions known to configured local package indexes; stale indexes may
omit newer packages. We did not receive its output in this exercise.

The reported plan:

| Item | Version |
|---|---|
| Cluster | 1.37.2 |
| kubeadm | 1.37.2 |
| Target | 1.37.2 |
| Latest in series reported by plan | 1.37.2 |

No upgrade was performed. This plan result is historical evidence, not a claim
that 1.37.2 will always be the newest available version.

## Workflow to study for a future upgrade

This is a procedure outline, not a ready-to-run package script. A target and exact
package versions must be selected after checking availability and compatibility.

1. Read release notes and check CNI compatibility, cluster health, backups and capacity.
2. Select the intended repository minor series and exact package versions.
3. On the first control-plane, upgrade kubeadm (and kubectl where the target guide
   places it), then inspect upgrade plan.
4. Run kubeadm upgrade apply with the selected Kubernetes version.
5. Drain the control-plane before a minor kubelet upgrade, accounting for hosted workloads.
6. Upgrade kubelet/client packages as the guide specifies; reload systemd and restart kubelet.
7. Uncordon and verify the node.
8. On each worker, install target kubeadm and run kubeadm upgrade node. Drain,
   upgrade kubelet and applicable client packages, restart kubelet, uncordon and verify.
9. Confirm nodes, API version, system Pods, rollout health, and application behavior.

Package holds may need to be temporarily removed and restored. Follow the target guide's
ordering rather than substituting a general OS upgrade.
The VERSION column in kubectl get nodes reports kubelet versions, not every component.
worker1's local PostgreSQL storage and standalone Pods need an explicit maintenance plan.

Reference: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/
