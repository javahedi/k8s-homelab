# 00 · Start here

[← Chapter index](README.md)

## Learning method and prerequisites
Understand → execute → inspect → troubleshoot → document in Git. This chapter records the exercises performed on 3–4 November 2026; the packaged instructions have been reviewed, but have not been rerun against a cluster by the authoring assistant. IPs, generated names and placement vary. Examples use the existing three-node Multipass lab from Module 01: control-plane, worker1, worker2, Ubuntu ARM64, containerd and Calico. All commands run in your Mac terminal from the repository root unless stated otherwise. kubectl sends requests to Kubernetes; it does not run the workloads on your Mac.

```bash
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
kubectl get nodes
mkdir -p 02-workloads/manifests
kubectl create namespace workloads --dry-run=client -o yaml | kubectl apply -f -
```

To persist kubeconfig selection for new interactive zsh sessions, add the following line ONCE to `~/.zshrc`, save, then run `source ~/.zshrc`:

```bash
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
```

`source` executes saved file contents; it does not save an export previously typed in a terminal. Test `kubectl get nodes` in a new tab. This choice selects only this kubeconfig; use explicit contexts/configs if managing other clusters. Never commit kubeconfigs or actual credentials.

## YAML and command conventions

| Field | Question answered |
|---|---|
| apiVersion | Which API group/version defines this type? |
| kind | What resource is being defined? |
| metadata | What name, namespace and labels? |
| spec | What desired behavior? |
| spec.template | Blueprint for Pods created by a controller |

Use spaces, consistent indentation, no tabs. Sibling keys align. `containers` is a list; each item begins with `-`. `--` separates kubectl arguments from the container command. A backslash must be the final character on a continued shell line. A `>` continuation prompt usually means an unfinished quote/command; Ctrl+C cancels it.

```bash
kubectl explain pod.spec
kubectl explain deployment.spec.template
kubectl apply --dry-run=client -f PATH.yaml
kubectl diff -f PATH.yaml
```

Replace PATH.yaml with a real filename. Dry-run checks are useful but do not prove the application will work. `-o yaml` prints YAML; `> file.yaml` writes it on your Mac and overwrites an existing file. `--dry-run=client` does not create the resource. Apply exercises in lesson order, not the whole manifests directory: several lessons deliberately change configuration and placement.

## Desired state versus saved state
`kubectl edit`, `label`, `scale` and `set image` change live resources, not local files. Keep YAML synchronized with the intended final state. `apply` is repeatable but is not a universal repair/reset operation; it manages declared fields using its apply bookkeeping. Standalone Pod fields are often immutable: recreate only the named practice Pod when instructed. Deleting a Pod loses its writable layer and emptyDir data.

---

[← Chapter index](README.md)
