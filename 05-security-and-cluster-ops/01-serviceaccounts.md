# 01 — ServiceAccounts

## Why an application needs an identity

An application that lists Pods or manages Deployments must call the Kubernetes API.
A ServiceAccount identifies that application. RBAC separately decides what it may do.
Our earlier frontend and PostgreSQL-backed API did not need Kubernetes API access.

Each namespace has its own default ServiceAccount. Pods use it when
`serviceAccountName` is omitted. A custom account must be in the Pod's namespace.
For a Deployment, configure it under `spec.template.spec.serviceAccountName`.

## Lab manifest

Existing file: `manifests/01-serviceaccount-pod.yaml`.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: security-lab
---
apiVersion: v1
kind: Pod
metadata:
  name: identity-demo
  namespace: security-lab
spec:
  serviceAccountName: app-sa
  containers:
    - name: nginx
      image: nginx:stable
```

On the Mac, create the namespace once, then apply:

```bash
kubectl create namespace security-lab
kubectl apply -f manifests/01-serviceaccount-pod.yaml
kubectl describe pod identity-demo -n security-lab
```

An AlreadyExists response for the namespace means it already exists.
Observed result: `Service Account: app-sa`.

## Identity files

```bash
kubectl wait --for=condition=Ready pod/identity-demo -n security-lab --timeout=120s
kubectl exec -n security-lab identity-demo -- ls /var/run/secrets/kubernetes.io/serviceaccount
```

Wait simply waits for readiness before exec. The mounted directory normally contains:

| File | Purpose |
|---|---|
| ca.crt | Verify the API server |
| namespace | Pod namespace |
| token | Authenticate API requests |

Modern Pods normally use short-lived projected tokens; a ServiceAccount need not
have an automatically created token Secret. Avoid printing tokens.
Set `automountServiceAccountToken: false` when API credentials are unnecessary.

## Initial permission check

```bash
kubectl auth can-i list pods -n security-lab --as=system:serviceaccount:security-lab:app-sa
```

Before RBAC bindings, our result was no. Identity alone did not grant Pod-listing access.

Reference: https://kubernetes.io/docs/concepts/security/service-accounts/
