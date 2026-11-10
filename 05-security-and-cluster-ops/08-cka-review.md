# 08 — Final practice and completion checklist

Status: supplied for practice; not yet completed in this session.
These are hands-on recall tasks, not a claim about exact current exam questions.

## Tasks

1. In security-lab, create a ServiceAccount named review-sa.
2. Create a Role named review-config-reader allowing get/list/watch on ConfigMaps.
3. Bind it only to review-sa in security-lab.
4. Demonstrate that it can list ConfigMaps there, cannot delete them, and cannot list
   them in jobs-demo.
5. Explain why the test requires --as when you use your administrator kubeconfig.
6. Inspect secure-demo and identify its Linux UID, root filesystem restriction and
   ServiceAccount token mounting choice.
7. Explain what remains on a drained node and why. Identify why Traefik blocked our
   first drain and what permitting emptyDir deletion meant.
8. On control-plane, inspect the existing snapshot's status. Identify the four connection
   options needed for a new online snapshot and why offline restore does not use them.
9. Explain why restoring files did not roll the running cluster back.
10. Explain why upgrading kubeadm is different from upgrading kubelet.

## Hints and checks

Run the API commands on the Mac:

```bash
kubectl create serviceaccount review-sa -n security-lab
kubectl create role review-config-reader --verb=get,list,watch --resource=configmaps -n security-lab
kubectl create rolebinding review-config-reader --role=review-config-reader --serviceaccount=security-lab:review-sa -n security-lab
kubectl auth can-i list configmaps -n security-lab --as=system:serviceaccount:security-lab:review-sa
kubectl auth can-i delete configmaps -n security-lab --as=system:serviceaccount:security-lab:review-sa
kubectl auth can-i list configmaps -n jobs-demo --as=system:serviceaccount:security-lab:review-sa
kubectl get pod secure-demo -n security-lab -o yaml
kubectl get daemonsets -A
kubectl get nodes
```

Expected authorization answers: yes, no, no.
Create commands are intended for first use; AlreadyExists means inspect/reuse the resource.

Inside control-plane:

```bash
sudo etcdutl snapshot status /var/backups/etcd/ch05-snapshot.db --write-out=table
```

## Clean up only review resources

```bash
kubectl delete rolebinding review-config-reader -n security-lab
kubectl delete role review-config-reader -n security-lab
kubectl delete serviceaccount review-sa -n security-lab
```

## Finish the chapter honestly

- [x] ServiceAccount assigned to a Pod.
- [x] RoleBinding changes authorization.
- [x] ClusterRole exercise reported completed.
- [x] Non-root and read-only restrictions demonstrated.
- [x] worker2 cordoned, drained and uncordoned.
- [x] Snapshot saved and status inspected.
- [x] Restore files created separately.
- [x] Upgrade plan inspected.
- [ ] Confirm Traefik's post-drain rollout if not already checked.
- [ ] Complete the review tasks above.
- [ ] Future lab: activate restored etcd and validate cluster recovery.
- [ ] Future lab: upgrade to a newer available compatible version.

Full recovery and actual upgrade remain follow-up labs. Do not mark them completed
solely because the file restore and upgrade plan succeeded.
