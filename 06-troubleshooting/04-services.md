# 04 — Service selector mismatch

A running Pod can still be unreachable through a misconfigured Service.

## Evidence from our lab

| Resource | Label or selector |
|---|---|
| nginx Pod `broken-image` | `run=broken-image` |
| Broken Service selector | `run=wrong-app` |

The Service existed at `10.102.46.10`, but its Endpoints field was empty.

```bash
kubectl get pods -n troubleshooting --show-labels
kubectl describe service broken-service -n troubleshooting
kubectl get endpointslices -n troubleshooting -l kubernetes.io/service-name=broken-service
```

The EndpointSlice may exist with no addresses; what matters is whether usable backend addresses are present.

## Repair the selector

Save this repaired configuration in `manifests/broken-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: broken-service
  namespace: troubleshooting
spec:
  selector:
    run: broken-image
  ports:
    - port: 80
      targetPort: 80
```

```bash
kubectl apply -f manifests/broken-service.yaml
kubectl describe service broken-service -n troubleshooting
kubectl get endpointslices -n troubleshooting -l kubernetes.io/service-name=broken-service
```

Service selectors can be updated in place. No forced replacement is needed.

## Verify actual HTTP traffic

```bash
kubectl exec -n troubleshooting broken-command -- wget -qO- -T 5 http://broken-service
```

Our test succeeded and returned nginx HTML. This verifies name resolution and an HTTP request through the Service.

`port: 80` is the Service's port. `targetPort: 80` is the destination port on the selected Pod. A selector must match Pod labels in the Service's namespace.
