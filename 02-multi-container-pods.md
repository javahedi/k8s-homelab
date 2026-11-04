# 02 · Multi-container Pods

[← Chapter index](README.md)

## Understand
Containers in one Pod share network/IP and run on the same node. They have separate root filesystems; volumes can explicitly share directories. This exercise's observer is a regular companion container, not a native restartable init-container sidecar.

Save as `02-workloads/manifests/multi-container-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pair
  namespace: workloads
  labels:
    app: nginx-pair
spec:
  containers:
    - name: nginx
      image: nginx:stable
    - name: observer
      image: busybox:1.37
      command:
        - sh
        - -c
        - |
          while true; do
            date
            wget -q -O - http://localhost:80
            sleep 5
          done
```

```bash
kubectl apply -f 02-workloads/manifests/multi-container-pod.yaml
kubectl wait -n workloads --for=condition=Ready pod/nginx-pair --timeout=120s
kubectl get pods -n workloads -o wide
kubectl logs nginx-pair -n workloads -c observer --tail=15
kubectl logs nginx-pair -n workloads -c nginx --tail=5
kubectl exec -n workloads nginx-pair -c observer -- wget -q -O - http://localhost:80
```

Expect 2/2 ready. The first requests can fail while Nginx starts; the loop retries. `logs` reads existing output; `exec` executes a new command. kubectl `-c observer` selects a container; shell `sh -c` executes a script string. YAML `|` preserves multiline script text; wget `-q` is quiet and `-O -` prints the downloaded body.

BusyBox supplies sh/date/wget/sleep but not curl in this image. An executable-not-found error happens before any network request. Use the tools actually installed in the chosen container.

Images `nginx:stable` and `busybox:1.37` resolve to Docker Hub library images. Tags identify image references and can move; digests pin content. The worker's runtime pulls images as required by pull policy/cache. The Mac does not supply images automatically.

## Separate filesystems

```bash
kubectl exec -n workloads nginx-pair -c observer -- sh -c 'echo "Hello from observer" > /tmp/pod-test.txt'
kubectl exec -n workloads nginx-pair -c observer -- cat /tmp/pod-test.txt
kubectl exec -n workloads nginx-pair -c nginx -- cat /tmp/pod-test.txt
```

Last command should fail: file absent, exit code 1.

## Share an emptyDir
Edit the manifest: add to EACH container, alongside image/name:

```yaml
      volumeMounts:
        - name: shared-data
          mountPath: /shared
```

Add under Pod spec, alongside containers:

```yaml
  volumes:
    - name: shared-data
      emptyDir: {}
```

```bash
kubectl delete pod nginx-pair -n workloads
kubectl apply -f 02-workloads/manifests/multi-container-pod.yaml
kubectl wait -n workloads --for=condition=Ready pod/nginx-pair --timeout=120s
kubectl exec -n workloads nginx-pair -c observer -- sh -c 'echo "Hello through the shared volume" > /shared/test.txt'
kubectl exec -n workloads nginx-pair -c nginx -- cat /shared/test.txt
```

Both containers now see the shared file. emptyDir survives container restarts within the Pod but is lost when the Pod is removed. It is not durable storage across Pod replacement.

---

[← Chapter index](README.md)
