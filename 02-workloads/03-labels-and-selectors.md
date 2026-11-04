# 03 · Labels and selectors

[← Chapter index](README.md)

Labels are key/value metadata, not resource names. Selectors filter by these labels. Start with nginx labeled run=nginx and nginx-pair labeled app=nginx-pair.

```bash
kubectl get pods -n workloads --show-labels
kubectl get pods -n workloads -l app=nginx-pair
kubectl get pods -n workloads -l app=nginx
kubectl get pods -n workloads -l run=nginx
```

The middle selector app=nginx initially matches nothing: key and value must both match.

```bash
kubectl label pods nginx nginx-pair -n workloads environment=lab
kubectl get pods -n workloads -l environment=lab --show-labels
kubectl get pods -n workloads -l 'environment=lab,app=nginx-pair'
kubectl label pod nginx -n workloads environment=test --overwrite
kubectl get pods -n workloads -l environment=test
kubectl label pod nginx -n workloads environment-
kubectl label pod nginx -n workloads environment=lab
```

Comma means AND. `--overwrite` permits changing a value; trailing minus removes a label. These metadata changes do not restart containers. If rerunning and the label already has a different value, inspect first, then use --overwrite deliberately.

```bash
kubectl get pods -n workloads -l 'environment in (lab,test)'
kubectl get pods -n workloads -l app
kubectl get pods -n workloads -l '!app'
kubectl get pods -n workloads -l '!run'
kubectl get pods -n workloads -L environment,app,run
```

| Syntax | Meaning |
|---|---|
| -l app=nginx-pair | Equality filter |
| -l 'environment in (lab,test)' | Value in a set |
| -l app | Key exists |
| -l '!app' | Key absent |
| -L environment,app,run | Display values in columns, no filtering |

Quote ! so zsh doesn't interpret it. Blank label columns mean the key is absent.

Persist `environment: lab` under metadata.labels in BOTH Pod manifests, preserving their existing labels. Apply each file. Labels on a Deployment itself are separate from spec.template.metadata.labels on its Pods; selectors do not infer one from the other.

---

[← Chapter index](README.md)
