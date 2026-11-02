# 08 · Control Kubernetes from macOS

[← Chapter index](README.md) · [← Project overview](../README.md)

Our Mac already had kubectl v1.36.1, compatible with the v1.37 server (within one minor version). Don't overwrite your existing `~/.kube/config`.

```bash
mkdir -p ~/.kube
chmod 700 ~/.kube
multipass exec control-plane -- sudo cp /etc/kubernetes/admin.conf /home/ubuntu/k8s-homelab.yaml
multipass exec control-plane -- sudo chown ubuntu:ubuntu /home/ubuntu/k8s-homelab.yaml
multipass exec control-plane -- chmod 600 /home/ubuntu/k8s-homelab.yaml
multipass transfer control-plane:/home/ubuntu/k8s-homelab.yaml ~/.kube/k8s-homelab.yaml
chmod 600 ~/.kube/k8s-homelab.yaml
multipass exec control-plane -- rm /home/ubuntu/k8s-homelab.yaml
```

Now verify:

```bash
kubectl --kubeconfig ~/.kube/k8s-homelab.yaml get nodes
```

**To avoid typing `--kubeconfig` each time**, for the *current zsh session*:

```bash
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
kubectl get nodes
```

To make that choice persistent, add exactly this line to `~/.zshrc` if you only want to use this lab context:

```bash
export KUBECONFIG="$HOME/.kube/k8s-homelab.yaml"
```

Then `source ~/.zshrc`. **If you already use other clusters**, setting `KUBECONFIG` this way hides the default kubeconfig; consider a merged config or explicit context switching instead. For CKA practice, add to `~/.zshrc`:

```bash
source <(kubectl completion zsh)
alias k=kubectl
compdef k=kubectl
```

The kubeconfig contains powerful admin credentials. Do not store it in the repo, screenshots, or chat.

---

[← All cluster-setup chapters](README.md)
