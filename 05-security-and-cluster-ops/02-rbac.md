# 02 — RBAC

## Identity, permission, assignment

| Object | Purpose |
|---|---|
| ServiceAccount | Application identity |
| Role | Permission rules for a namespace |
| RoleBinding | Assign a Role or ClusterRole within one namespace |
| ClusterRole | Reusable permission rules, including cluster-scoped resources |
| ClusterRoleBinding | Assign a ClusterRole across the cluster |

Permissions are additive. A ClusterRole used through a RoleBinding grants only
applicable namespaced permissions in the binding's namespace; it does not grant node access.

## Read Pods in security-lab

`manifests/02-pod-reader-role.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: security-lab
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

The empty API group means core resources. get reads one object, list reads a collection,
and watch follows changes. These rules do not grant Pod logs or exec access.

`manifests/03-pod-reader-binding.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-sa-pod-reader
  namespace: security-lab
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: security-lab
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
```

```bash
kubectl apply -f manifests/02-pod-reader-role.yaml
kubectl apply -f manifests/03-pod-reader-binding.yaml
kubectl auth can-i list pods -n security-lab --as=system:serviceaccount:security-lab:app-sa
kubectl auth can-i delete pods -n security-lab --as=system:serviceaccount:security-lab:app-sa
kubectl auth can-i list pods -n jobs-demo --as=system:serviceaccount:security-lab:app-sa
```

Expected: yes, no, no. Creating the Role alone still produced no; applying the binding
changed listing to yes.

## Why --as?

Without --as, kubectl uses your kubeconfig user. With --as, your administrator requests
impersonation of the supplied identity. Both identities may see the same Pods when
both are allowed. This does not mean they have identical permissions.

Format: `system:serviceaccount:<namespace>:<account-name>`.
Permission checks do not establish whether a named ServiceAccount exists; spelling matters.
Impersonation itself requires authorization.
A Pod using its own ServiceAccount token does not need --as.

## Read nodes

`manifests/04-node-reader-clusterrole.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: lab-node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
```

`manifests/05-node-reader-binding.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: lab-app-sa-node-reader
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: security-lab
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: lab-node-reader
```

```bash
kubectl apply -f manifests/04-node-reader-clusterrole.yaml
kubectl apply -f manifests/05-node-reader-binding.yaml
kubectl get nodes --as=system:serviceaccount:security-lab:app-sa
kubectl auth can-i delete nodes --as=system:serviceaccount:security-lab:app-sa
```

Expected: node listing succeeds; delete check says no.
Neither ClusterRole nor ClusterRoleBinding has metadata.namespace.
The subject still has a namespace because ServiceAccounts are namespaced.

Reference: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
