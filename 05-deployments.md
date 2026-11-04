# 05 · Deployments, rolling updates and rollback

[← Chapter index](README.md)

## Which resource and why?

| Manifest kind | apiVersion | What you ask Kubernetes to create |
|---|---|---|
| Pod | v1 | One Pod directly |
| ReplicaSet | apps/v1 | A manager maintaining a chosen number of Pods |
| Deployment | apps/v1 | A manager handling ReplicaSets, updates and rollback |

v1 is the core API version; apps/v1 is version v1 of the apps group, not a more advanced kind of Pod.

| Your resource | Management relationship |
|---|---|
| nginx | Standalone Pod |
| nginx-pair | Standalone Pod containing two containers |
| nginx-rs | ReplicaSet → Pods |
| nginx-deploy | Deployment → ReplicaSet → Pods |

Deployment is the usual choice for interchangeable web/API replicas; Jobs, DaemonSets and StatefulSets serve different needs. A Deployment can have multiple containers in each Pod template.

## Generate a blueprint

```bash
kubectl create deployment nginx-deploy -n workloads --image=nginx:stable --replicas=2 --dry-run=client -o yaml > 02-workloads/manifests/nginx-deployment.yaml
kubectl apply -f 02-workloads/manifests/nginx-deployment.yaml
kubectl rollout status deployment/nginx-deploy -n workloads --timeout=120s
kubectl get deployment nginx-deploy -n workloads -o wide
kubectl get rs,pods -n workloads -l app=nginx-deploy
```

Generated templates normally use app=nginx-deploy. Check the file. One Deployment controls one active ReplicaSet with two Pods initially. READY, UP-TO-DATE, AVAILABLE describe different aspects; read rollout status for progress.

## Change the Pod template
Choose ONE of these methods:

```bash
kubectl set image deployment/nginx-deploy nginx=nginx:stable-alpine -n workloads
```

Or `kubectl edit deployment nginx-deploy -n workloads`, changing only the nginx container image under spec.template.spec.containers. In Vim, Esc then :wq saves. Editing local YAML and applying is the Git-friendly alternative. Live edit/set does not change local YAML.

```bash
kubectl rollout status deployment/nginx-deploy -n workloads --timeout=120s
kubectl get rs -n workloads -l app=nginx-deploy
```

The default RollingUpdate strategy gradually replaces replicas. With two desired replicas and default 25% settings, maxSurge rounds up to one and maxUnavailable rounds down to zero: three Pods temporarily is expected. Old ReplicaSet ends at zero; new reaches two. A changed Pod template creates a new revision; merely scaling doesn't.

## History and rollback

```bash
kubectl rollout history deployment/nginx-deploy -n workloads
kubectl rollout undo deployment/nginx-deploy -n workloads
kubectl rollout status deployment/nginx-deploy -n workloads --timeout=120s
kubectl get deployment nginx-deploy -n workloads -o wide
kubectl get rs -n workloads -l app=nginx-deploy
```

Expected image nginx:stable and two ready replicas. Rollback restores a previous Pod template, not deleted Pod identities; repeated undo can reverse another revision, so inspect before repeating. CHANGE-CAUSE may be <none>; this does not indicate failure. The warning about last-applied-configuration concerns apply bookkeeping, not rollback failure. Ensure local YAML matches your intended final image and reconcile deliberately.

[Official Deployment reference](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

[← Chapter index](README.md)
