# 06 — Restore snapshot files

## Scope of this exercise

Completed: reconstruct etcd data files in a separate directory.
Pending: start etcd on restored data and validate recovery through the Kubernetes API.
Do not describe file restoration alone as a completed cluster recovery test.

| Path | Purpose |
|---|---|
| /var/lib/etcd | Running server's original data |
| /var/backups/etcd/ch05-snapshot.db | Snapshot input |
| /var/lib/etcd-restore-practice | Practice output |

Inside control-plane:

```bash
sudo etcdutl snapshot restore \
  /var/backups/etcd/ch05-snapshot.db \
  --data-dir=/var/lib/etcd-restore-practice \
  --name=control-plane \
  --initial-cluster=control-plane=https://192.168.252.2:2380 \
  --initial-advertise-peer-urls=https://192.168.252.2:2380
sudo ls -lh /var/lib/etcd-restore-practice/member/snap/
```

Let restore create the destination. If it already exists, investigate rather than deleting
it blindly. Observed output directory contained an approximately 11 MB db and a .snap file.
etcdutl works on local files, so endpoint and TLS flags are unnecessary for this operation.

## The shorter documentation example

```text
etcdutl --data-dir <directory> snapshot restore snapshot.db
```

The data-dir flag may precede or follow the subcommand.
Omitted membership options use defaults. We supplied member name and peer settings
explicitly to match the intended single-member configuration.
Restore rebuilds membership identity; it is not merely copying the snapshot file.

## What a full recovery additionally requires

This is a conceptual checklist, not an instruction to switch this healthy cluster now:

1. Preserve a recent backup, manifests, credentials and a recovery path.
2. Stop API-server access to etcd and stop the old etcd process using the supported
   static-Pod recovery procedure.
3. Restore to a fresh directory with correct membership settings.
4. For Kubernetes recovery, use an adequate revision bump and mark the old revisions
   compacted, following the version-specific etcd recovery guide. This prevents clients
   from retaining invalid watch/cache state after going back in time.
5. Point the etcd static Pod's hostPath at the restored directory, with correct permissions.
   The container can keep /var/lib/etcd as its mountPath and --data-dir value.
6. Start restored etcd and API-server components, then verify health and Kubernetes resources.

Keep backup copies of static Pod manifests outside /etc/kubernetes/manifests:
kubelet watches that directory. Never restore into data currently used by a running etcd.
Our practice restore did not apply a revision bump because it was not activated;
prepare a new recovery restore with the appropriate options before live use.

Reference: https://etcd.io/docs/v3.7/op-guide/recovery/
