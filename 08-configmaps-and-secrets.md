# 08 · ConfigMaps and Secrets

[← Chapter index](README.md)

| Resource | Purpose |
|---|---|
| ConfigMap | Non-confidential configuration |
| Secret | Sensitive configuration; access must be controlled |

```bash
kubectl create configmap app-settings -n workloads --from-literal=APP_NAME=Homelab --from-literal=APP_LANGUAGE=en --dry-run=client -o yaml > 02-workloads/manifests/app-settings.yaml
kubectl apply -f 02-workloads/manifests/app-settings.yaml
kubectl describe configmap app-settings -n workloads
kubectl run config-demo -n workloads --image=busybox:1.37 --dry-run=client -o yaml --command -- sleep 3600 > 02-workloads/manifests/config-demo.yaml
```

Add envFrom to the generated container, alongside image/name/command:

```yaml
      envFrom:
        - configMapRef:
            name: app-settings
```

```bash
kubectl apply -f 02-workloads/manifests/config-demo.yaml
kubectl wait -n workloads --for=condition=Ready pod/config-demo --timeout=120s
kubectl exec -n workloads config-demo -- printenv APP_NAME APP_LANGUAGE
```

Expect Homelab and en. The ConfigMap alone doesn't configure containers: the reference connects them. Referenced resources must exist in the Pod's namespace.

## Updates
Change APP_LANGUAGE to de in app-settings.yaml and apply. Existing container still prints en: environment variables are loaded at container startup. Recreate config-demo using its manifest, wait, and read again: expect de. For Deployment-managed applications a controlled rollout restart can recreate Pods. A ConfigMap mounted as a volume is different: files normally update eventually, excluding subPath mounts, and applications must reload them as needed. We practiced environment injection, not volume updates.

## Fake credentials only

```bash
kubectl create secret generic app-credentials -n workloads --from-literal=APP_PASSWORD=practice-only-123 --dry-run=client -o yaml > 02-workloads/manifests/app-credentials.yaml
kubectl apply -f 02-workloads/manifests/app-credentials.yaml
```

Base64 data is encoding, NOT encryption. Do not commit real Secret manifests or real credentials; shell literal commands may also remain in history. This example is deliberately fake. Encryption at rest, RBAC and external secret management require separate configuration.

Add a second source under the same envFrom list:

```yaml
      envFrom:
        - configMapRef:
            name: app-settings
        - secretRef:
            name: app-credentials
```

```bash
kubectl delete pod config-demo -n workloads
kubectl apply -f 02-workloads/manifests/config-demo.yaml
kubectl wait -n workloads --for=condition=Ready pod/config-demo --timeout=120s
kubectl exec -n workloads config-demo -- printenv APP_PASSWORD
```

Expected fake value. Avoid printing actual secrets during real operations. `env` plus valueFrom.configMapKeyRef/secretKeyRef selects individual keys instead of importing all keys with envFrom.

If wait appears stuck, inspect get/describe. Missing references can produce CreateContainerConfigError. `--for=condition=Ready` needs the equals sign; `condition-Ready` is invalid. Ctrl+C stops waiting, not the Pod.

[Official ConfigMap reference](https://kubernetes.io/docs/concepts/configuration/configmap/)

---

[← Chapter index](README.md)
