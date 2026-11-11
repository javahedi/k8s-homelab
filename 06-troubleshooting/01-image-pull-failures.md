# 01 — ImagePullBackOff

## Reproduce in a fresh lab

```bash
kubectl run broken-image -n troubleshooting --image=nginx:cka-invalid-tag
kubectl describe pod broken-image -n troubleshooting
```

The events showed the image tag was not found:

```text
nginx:cka-invalid-tag: not found
ErrImagePull
ImagePullBackOff
```

`ErrImagePull` indicates a failed image pull. `ImagePullBackOff` means Kubernetes is delaying retries. An invalid tag was our cause; authentication, registry connectivity, and rate limits can also cause image pull failures. Read the specific event message.

## Fix using kubectl edit

```bash
kubectl edit pod broken-image -n troubleshooting
```

Change the container image to:

```yaml
image: nginx:stable
```

In Vim: press `i`, edit, press Esc, type `:wq`, and press Enter. Container image changes are allowed on an existing Pod.

```bash
kubectl get pod broken-image -n troubleshooting -w
```

Our result: `1/1 Running`, zero restarts.

## Keep the local manifest consistent

A live `kubectl edit` does not change `manifests/broken-image.yaml`. Open the local file and ensure its image is also `nginx:stable` if you want to save the repaired configuration.

The `stable` tag can change over time; this tutorial records the lab's chosen tag rather than a pinned image version.
