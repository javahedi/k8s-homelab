# 03 — SecurityContext

RBAC governs Kubernetes API actions. SecurityContext governs execution inside Linux containers.
Linux UID 0 is root; it is independent of Kubernetes API identity.

## Manifest

`manifests/06-security-context.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-demo
  namespace: security-lab
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    runAsNonRoot: true
  containers:
    - name: busybox
      image: busybox:1.37
      command: ["sh", "-c", "sleep 3600"]
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
```

| Setting | Purpose |
|---|---|
| runAsUser / runAsGroup | Select Linux user/group IDs |
| runAsNonRoot | Require a non-root user |
| allowPrivilegeEscalation: false | Prevent gaining privileges through execution mechanisms such as setuid |
| readOnlyRootFilesystem | Make the container root filesystem read-only |
| capabilities.drop | Remove Linux capabilities |
| automountServiceAccountToken: false | Avoid mounting unnecessary API credentials |

Pod-level settings establish defaults; container settings can override supported overlapping fields.
Not all fields are valid at both levels. Token mounting is a Pod setting outside securityContext.

## Verify

```bash
kubectl apply -f manifests/06-security-context.yaml
kubectl wait --for=condition=Ready pod/secure-demo -n security-lab --timeout=120s
kubectl exec -n security-lab secure-demo -- id
kubectl exec -n security-lab secure-demo -- touch /tmp/test
kubectl exec -n security-lab identity-demo -- id
kubectl exec -n security-lab identity-demo -- touch /tmp/test
```

Observed: secure-demo ran as UID/GID 1000 and touch failed with a read-only filesystem error.
identity-demo ran as root and touch succeeded silently.
Non-root and read-only are separate restrictions.
Writable volume mounts can still provide writable directories with a read-only root filesystem.
The sleep exits after an hour; the default restart policy restarts the container.

Reference: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
