# 01 — Cluster health and events

## Check infrastructure, then workloads

```bash
kubectl get nodes
kubectl get pods -n jobs-demo -o wide
kubectl get events -n jobs-demo --sort-by=.metadata.creationTimestamp
```

- `Ready` indicates the Node reports readiness; it is not a capacity guarantee.
- `Running` is a Pod phase, not proof that all containers or application operations are healthy.
- `1/1` means one of one counted containers is ready; `2/3` means one is not ready.
- `RESTARTS` counts container restarts; inspect reasons and trends.
- `-o wide` adds placement and network information.
- Events describe actions such as scheduling, image pulls, probe failures and evictions.

`No resources found` for events means no events are currently retained in that Namespace. Events expire; it does not prove nothing ever failed.

## Prove a real operation works

In terminal A:

```bash
kubectl port-forward -n jobs-demo service/frontend 8082:80
```

In terminal B:

```bash
curl -i http://localhost:8082/api/jobs
```

The recorded response was HTTP 200 with three job records. This proves that request succeeded at that moment, not that every operation always succeeds.

Press Ctrl+C in terminal A to stop forwarding. It does not stop the application.

## Describe a Pod

First obtain its current name:

```bash
kubectl get pods -n jobs-demo
kubectl describe pod -n jobs-demo <pod-name>
```

Replace angle-bracket placeholders; do not paste them literally. Inspect State, Last State, Reason, Exit Code, Restart Count, resource settings, probes and Events.

## Probes

- Readiness: should this container's Pod receive Service traffic?
- Liveness: should Kubernetes restart this container after repeated failures?
- Startup: has startup completed before ordinary liveness/readiness checks begin?

The backend output in this session did not show configured readiness or liveness probes. We discussed them but did not add them. A successful API request provided stronger evidence of functionality than `Ready: True` alone.
