# 05 — etcd backup

## What is protected?

etcd stores Kubernetes API state, including Deployments, Services, Secrets, RBAC rules,
and PV/PVC definitions. It does not contain your PostgreSQL tables or other volume contents.
Application data requires its own backup. An etcd snapshot contains sensitive information;
do not commit it to Git.

## Discover the configuration

On the Mac:

```bash
kubectl get pods -n kube-system -l component=etcd -o wide
multipass shell control-plane
```

Inside control-plane:

```bash
sudo cat /etc/kubernetes/manifests/etcd.yaml
command -v etcdctl
command -v etcdutl
uname -m
```

Observed configuration:

| Item | Value |
|---|---|
| Image | registry.k8s.io/etcd:3.7.0-0 |
| Client address | https://127.0.0.1:2379 |
| Peer address | https://192.168.252.2:2380 |
| Member name | control-plane |
| Live data | /var/lib/etcd |
| Certificates | /etc/kubernetes/pki/etcd |
| Architecture | aarch64, meaning ARM64 |

This is a static Pod: kubelet manages it from the local manifest.
Port 2379 serves clients; 2380 serves member-to-member communication.

## Tools installed in this exercise

Run inside control-plane only if the tools are absent:

```bash
curl -fL https://github.com/etcd-io/etcd/releases/download/v3.7.0/etcd-v3.7.0-linux-arm64.tar.gz -o /tmp/etcd-v3.7.0-linux-arm64.tar.gz
tar -xzf /tmp/etcd-v3.7.0-linux-arm64.tar.gz -C /tmp
sudo install -m 0755 /tmp/etcd-v3.7.0-linux-arm64/etcdctl /tmp/etcd-v3.7.0-linux-arm64/etcdutl /usr/local/bin/
etcdctl version
etcdutl version
```

curl downloads, tar extracts, install copies executable utilities.
This installs tools; it does not replace the running etcd server.
Both tools reported 3.7.0.

## Health and snapshot

Inside control-plane:

```bash
sudo etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  endpoint health
```

| Flag | Question answered |
|---|---|
| endpoints | Where is etcd? |
| cacert | Which CA verifies the server? |
| cert | Which certificate identifies this client? |
| key | Which private key proves that identity? |

127.0.0.1 refers to the machine where the command executes.
sudo is needed to read protected key files.

```bash
sudo mkdir -p /var/backups/etcd
sudo chmod 700 /var/backups/etcd
sudo etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  snapshot save /var/backups/etcd/ch05-snapshot.db
sudo etcdutl snapshot status /var/backups/etcd/ch05-snapshot.db --write-out=table
```

The mkdir/chmod pair is an alternative to install -d -m 0700.
A newly created directory under sudo belongs to root; chmod changes permissions, not ownership.
Do not overwrite an existing backup unintentionally; choose another filename for later backups.

## Recorded result

| Hash | Revision | Keys | Size | Version |
|---|---:|---:|---|---|
| c579efda | 337548 | 615 | 11 MB | 3.7.0 |

Snapshot status inspection is not proof of successful live cluster recovery.
The backup is still on the same VM: losing the VM may lose it too.
For durable recovery, retain a protected off-machine copy and the required cluster
certificates/configuration through an appropriate secure backup process.

/var/backups/etcd is our chosen location, not an etcd requirement.
.db is descriptive: .txt would still contain a binary snapshot.
Learn the flags' meanings; discover paths for each cluster and follow the task's destination.

References:
- https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
- https://etcd.io/docs/v3.7/install/
