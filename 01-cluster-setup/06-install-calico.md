# 06 · Install Calico Networking

[← Chapter index](README.md) · [← Project overview](../README.md)

For Kubernetes v1.37, the official [Calico v3.33 operator guide](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises) uses its newer CRDs and the Tigera Operator.

```bash
multipass exec control-plane -- kubectl create -f \
  https://raw.githubusercontent.com/projectcalico/calico/v3.33.0/manifests/v3_projectcalico_org.yaml
multipass exec control-plane -- kubectl create -f \
  https://raw.githubusercontent.com/projectcalico/calico/v3.33.0/manifests/tigera-operator.yaml
```

A CRD defines an API resource type. The operator continuously reconciles resources. Our custom `Installation` is in [`01-cluster-setup/calico-installation.yaml`](calico-installation.yaml), with Pod CIDR **10.244.0.0/16**. Do **not** apply the upstream default custom-resources manifest as well; this tutorial uses its own `Installation` resource.

```bash
multipass transfer 01-cluster-setup/calico-installation.yaml control-plane:/tmp/calico-installation.yaml
multipass exec control-plane -- kubectl apply -f /tmp/calico-installation.yaml
multipass exec control-plane -- kubectl get tigerastatus
multipass exec control-plane -- kubectl get pods -n calico-system
multipass exec control-plane -- kubectl get pods -n kube-system
multipass exec control-plane -- kubectl get nodes
```

Wait for Calico status `AVAILABLE=True`, `PROGRESSING=False`, `DEGRADED=False`, both CoreDNS Pods Running, and the control-plane node Ready. The operator may take time to settle.

---

[← All cluster-setup chapters](README.md)
