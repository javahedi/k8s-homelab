# 06 · Services, blue-green and canary

[← Chapter index](README.md)

## Why different release strategies?

| Approach | Behavior |
|---|---|
| Rolling update | Gradually replace old Pods |
| Blue-green | Run separate releases; switch traffic after testing |
| Canary | Give a limited share of traffic to a new release before promotion |

Deployment has built-in RollingUpdate and Recreate strategies. Blue-green/canary here combine separate Deployments and Service selection. BLUE/GREEN text represents different real code releases; we change routing, not names of running Pods.

## Create two releases
Save `web-blue.yaml` in manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-blue
  namespace: workloads
spec:
  replicas: 1
  selector:
    matchLabels:
      app: release-demo
      version: blue
  template:
    metadata:
      labels:
        app: release-demo
        version: blue
    spec:
      containers:
        - name: nginx
          image: nginx:stable
          command: ["/bin/sh", "-c"]
          args:
            - |
              echo '<h1>BLUE — current version</h1>' > /usr/share/nginx/html/index.html
              exec nginx -g 'daemon off;'
```

```bash
kubectl apply -f 02-workloads/manifests/web-blue.yaml
kubectl rollout status deployment/web-blue -n workloads --timeout=120s
cp 02-workloads/manifests/web-blue.yaml 02-workloads/manifests/web-green.yaml
```

In web-green.yaml change metadata.name to web-green, BOTH version labels/selectors to green and page text to GREEN — new version. Keep app=release-demo. Apply/wait for web-green using the corresponding commands. Without command/args Nginx uses the image's default startup and welcome page. Overriding it means our script must start Nginx; echo alone exits. `exec` makes Nginx the main process.

## A Service is a stable destination
Save `web-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: workloads
spec:
  type: ClusterIP
  selector:
    app: release-demo
    version: blue
  ports:
    - port: 80
      targetPort: 80
```

```bash
kubectl apply -f 02-workloads/manifests/web-service.yaml
kubectl get service web -n workloads
kubectl exec -n workloads nginx-pair -c observer -- wget -q -O - http://web
```

Expect BLUE even while GREEN is running. Service doesn't create Pods: it routes to matching endpoints. port is the Service port; targetPort is the application's Pod port. 8080→80 would require http://web:8080. HTTP defaults to 80. The short DNS name web works from this namespace; web.workloads.svc.cluster.local is the typical full name when cluster domain is cluster.local. ClusterIP is not automatically reachable from the Mac.

| Request INSIDE observer | Destination |
|---|---|
| http://localhost:80 | Nginx beside observer in nginx-pair |
| http://web | Service web → selected BLUE/GREEN Pods, possibly on another worker |

`exec ... -c observer` selects WHERE the client command runs; the URL selects WHERE it sends traffic. Observer is only a reusable test client, not part of the blue Deployment.

```bash
kubectl get pods -n workloads -o custom-columns='POD:.metadata.name,NODE:.spec.nodeName,CONTAINERS:.spec.containers[*].name'
kubectl get endpointslices -n workloads -l kubernetes.io/service-name=web
```

## Switch and switch back
Edit the Service YAML selector version to green, apply it, and request http://web again. Expect GREEN after endpoint/network updates propagate. BLUE remains running. Switch version back to blue and apply/test to demonstrate traffic rollback. This differs from rollout undo, which restores a Deployment template. Existing connections are not forcibly migrated by a selector change.

## Canary and promotion
Change blue's replicas to 3 in its YAML and apply/wait. Keep green at 1. Remove ONLY version from the Service selector, so app=release-demo matches all four Pods. Apply:

```bash
kubectl exec -n workloads nginx-pair -c observer -- sh -c 'for i in $(seq 1 20); do wget -q -O - http://web; done'
```

Expect a mixture, usually more BLUE. The recorded sample was 14 BLUE/6 GREEN. Replica proportions approximate new connection distribution; they do not enforce percentages or guarantee user-level weights. Persistent connections/session affinity can skew results. Weighted routing needs additional traffic-management capabilities.

Promote by restoring version: green in the Service selector and applying. Repeat ten requests: expect GREEN after propagation. Final lab state: blue has 3 replicas, green 1, Service selects green. Consider scaling idle releases down after exercises if memory is tight; record intentional changes in YAML.

---

[← Chapter index](README.md)
