# 06 · Create the PostgreSQL Service

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Give PostgreSQL a stable network address for other Pods.

**Working directory:** `k8s-homelab-github/04-storage`.

## Concept: Service

A Pod IP can change after replacement.

A Service selects matching Pods and provides a stable address.
The Service routes traffic; it does not store database data.

Our Service is ClusterIP, intended for access within the cluster.

## Generate and inspect YAML

```bash
kubectl expose deployment postgres \
  --namespace=jobs-demo \
  --name=postgres \
  --port=5432 \
  --target-port=5432 \
  --type=ClusterIP \
  --dry-run=client -o yaml > manifests/postgres-service.yaml

cat manifests/postgres-service.yaml
```

The selector must match:

```yaml
selector:
  app: postgres
```

port is the Service's listening port.
targetPort is the destination port on the selected Pod.

## Validate and apply

```bash
kubectl apply --dry-run=server -f manifests/postgres-service.yaml
kubectl apply -f manifests/postgres-service.yaml
```

## Verify selection

```bash
kubectl get service postgres -n jobs-demo

kubectl get endpointslices -n jobs-demo \
  -l kubernetes.io/service-name=postgres
```

Verified: the EndpointSlice contained the PostgreSQL Pod IP on port 5432.

IPs are assigned by Kubernetes and may differ on another installation.

## DNS names

From a Pod in jobs-demo:

```text
postgres:5432
```

Full DNS name for our cluster:

```text
postgres.jobs-demo.svc.cluster.local
```

The Mac does not normally resolve these internal Service names directly.

## Review

1. Why use a Service instead of the Pod IP?
2. Which label connects this Service to the database Pod?
3. Does a Service make database files persistent?
4. Why can the backend use the short name postgres?

---

[← Previous](05-test-persistence.md) ·
[Next: Connect FastAPI →](07-connect-fastapi.md)
