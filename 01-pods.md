# 01 · Pods: imperative and declarative

[← Chapter index](README.md)

## Understand
A Pod is the smallest deployable unit, containing one or more containers. The scheduler selects a node, then its kubelet asks containerd to run the containers. Placement is not guaranteed to alternate between workers.

```bash
kubectl run nginx --image=nginx:stable -n workloads
kubectl get pods -n workloads -o wide
kubectl describe pod nginx -n workloads
```

If nginx already exists, inspect it instead of repeating creation. `READY 1/1` means one ready container out of one; Running does not necessarily mean Ready. RESTARTS counts container restarts, not replacements with new Pod identities.

| Address from our lab | Meaning |
|---|---|
| 192.168.252.3 | worker1's node address |
| 10.244.235.196 | Example Pod address, assigned through Calico |
| localhost inside a Pod | That Pod's shared network namespace |
| localhost in the Mac browser | Your Mac |

Pod IPs may change after recreation. A `/32` annotation identifies a single IPv4 address; it does not change the lab's overall `10.244.0.0/16` Pod pool.

## Inspect and access

```bash
kubectl exec -n workloads nginx -- curl -s http://localhost:80
kubectl logs nginx -n workloads --tail=20
kubectl port-forward -n workloads pod/nginx 8080:80
```

Keep port-forward running and open http://localhost:8080. Ctrl+C stops the tunnel, not the Pod. Mapping is LOCAL:REMOTE: 9090:80 also works if 9090 is available, but 8080:90 fails unless an application listens on 90. `containerPort` being absent in describe does not mean Nginx isn't listening.

Describe shows Kubernetes configuration/events; logs show container output. Events normally show Scheduled, image Pulled/already present, Created, Started. HTTP 200 indicates success. Missing favicon.ico or service-worker.js can produce 404 without breaking `/`; a browser can request these independently.

## Generate and save the blueprint

```bash
kubectl run nginx --image=nginx:stable -n workloads --dry-run=client -o yaml > 02-workloads/manifests/nginx-pod.yaml
```

Minimal equivalent:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  namespace: workloads
  labels:
    run: nginx
spec:
  containers:
    - name: nginx
      image: nginx:stable
```

Generated `status: {}` and empty resources can be omitted. Defaults such as restartPolicy Always and dnsPolicy ClusterFirst need not be repeated. The Pod name and container name are independent of image name/tag.

Stop port-forward first, then recreate only the practice Pod:

```bash
kubectl delete pod nginx -n workloads
kubectl apply -f 02-workloads/manifests/nginx-pod.yaml
kubectl apply -f 02-workloads/manifests/nginx-pod.yaml
```

The second apply should report unchanged, not create a duplicate. New Pod IP/node may differ.

## Troubleshooting and recall
`kubectl run` does not create a missing namespace. A typo such as workeloads normally produces NotFound; if creation succeeds, that namespace already existed. Inspect `kubectl get pods -A` and `kubectl get namespaces` before deleting a mistaken namespace: namespace deletion removes all its namespaced resources. Don't delete system namespaces.

Explain: why does a browser on the Mac need port-forward while curl executed inside the Pod does not?

---

[← Chapter index](README.md)
