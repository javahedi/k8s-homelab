# 08 — Review, cleanup, and Git

## What we completed

| Symptom | Evidence | Correction |
|---|---|---|
| ImagePullBackOff | Image tag not found in Events | Correct image tag |
| CrashLoopBackOff | Exit 0, no custom command, empty logs | Recreate with a long-running command |
| Pending | Node selector mismatch in Events | Select an existing worker label |
| Service inaccessible | Selector mismatch and empty endpoints | Match the nginx Pod label |
| NXDOMAIN | Wrong namespace in queried name | Use correct Service name |

We also inspected healthy node services and verified the jobs application. Advanced runtime failures, CNI failures, resource exhaustion, and control-plane repair remain future practice.

## Final checks on the Mac

```bash
kubectl get nodes
kubectl get pods -n troubleshooting -o wide
kubectl get services -n troubleshooting
kubectl get pods -n jobs-demo
```

Remember that our BusyBox sleep command can restart after one hour; this does not undo the earlier repair.

## Keep manifests clean

If a YAML file was exported from a live resource, remove server-generated fields such as `status`, `metadata.uid`, `resourceVersion`, `creationTimestamp`, and `managedFields`. Keep intentional configuration. For this chapter, hand-written minimal Pod manifests are easier to read than raw exports.

Confirm your four local YAML files contain the repaired configuration before applying them elsewhere. Do not blindly use forced replacement on production resources.

## Optional lab cleanup

To remove every resource in the dedicated exercise namespace:

```bash
kubectl delete namespace troubleshooting
```

Only do this when you no longer need the exercises. It does not delete your local YAML files or the separate `jobs-demo` namespace.

## Commit the chapter

After copying the Markdown files into your existing chapter folder, run from `06-troubleshooting`:

```bash
git status
git diff --check
git add README.md 00-start-here.md 01-image-pull-failures.md 02-container-restarts.md 03-scheduling.md 04-services.md 05-networking-explained.md 06-node-health.md 07-jobs-demo.md 08-review-and-git.md manifests/
git diff --cached --stat
git diff --cached
git commit -m "Add chapter 06 troubleshooting tutorials and manifests"
git push origin main
```

Review the staged changes before committing. These commands are for your local repository; the tutorial archive does not perform a commit or push.

## Self-check

Explain each answer in your own words:

1. Why can exit code 0 still lead to CrashLoopBackOff?
2. Where do you find an invalid image tag error?
3. Why does preemption not solve a node selector mismatch?
4. What connects a Service to its backend Pods?
5. Does normal Service DNS return a node IP, Pod IP, or ClusterIP?
6. Why does NXDOMAIN for a wrong namespace not imply broken DNS?
7. What does a port-forward test prove, and what does it bypass?
