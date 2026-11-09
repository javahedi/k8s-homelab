# 08 · Build, Import, and Deploy Backend v2

[← Chapter index](README.md) · [← Project overview](../README.md)

## Goal

Package the edited backend and run it in Kubernetes.

**Working directory:** `k8s-homelab-github/04-storage`.

## 1. Inspect before building

```bash
cat ../03-networking/demo-app/backend/main.py
cat ../03-networking/demo-app/backend/requirements.txt
cat ../03-networking/demo-app/backend/Dockerfile
```

The Dockerfile installs requirements and copies main.py.
The build context must therefore be the backend directory.

Start Docker Desktop and verify:

```bash
docker info --format '{{.OSType}}/{{.Architecture}}'
```

Our workers are Linux ARM64.

## 2. Build the image

```bash
docker build \
  --platform linux/arm64 \
  -t javad-jobs-backend:v2 \
  ../03-networking/demo-app/backend

docker image inspect javad-jobs-backend:v2 \
  --format '{{.RepoTags}} {{.Os}}/{{.Architecture}}'
```

The resulting image is a snapshot of source and installed dependencies.
The cluster is still running v1 at this point.

## 3. Export and copy

```bash
docker save -o /tmp/javad-jobs-backend-v2.tar \
  javad-jobs-backend:v2

multipass transfer /tmp/javad-jobs-backend-v2.tar \
  worker1:/tmp/javad-jobs-backend-v2.tar

multipass transfer /tmp/javad-jobs-backend-v2.tar \
  worker2:/tmp/javad-jobs-backend-v2.tar
```

The archive is temporary build output, not repository content.

## 4. Import into both workers

```bash
multipass exec worker1 -- sudo ctr -n k8s.io images import \
  /tmp/javad-jobs-backend-v2.tar

multipass exec worker2 -- sudo ctr -n k8s.io images import \
  /tmp/javad-jobs-backend-v2.tar
```

k8s.io is containerd's namespace used for Kubernetes images.
It is not Kubernetes namespace jobs-demo.

Verify:

```bash
multipass exec worker1 -- sudo ctr -n k8s.io images ls \
  | grep javad-jobs-backend

multipass exec worker2 -- sudo ctr -n k8s.io images ls \
  | grep javad-jobs-backend
```

Verified: both workers contained the same ARM64 v2 image digest.

## 5. Update the existing Deployment manifest

```bash
cat > ../03-networking/demo-app/k8s/backend.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: jobs-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jobs-backend
  template:
    metadata:
      labels:
        app: jobs-backend
    spec:
      containers:
        - name: backend
          image: docker.io/library/javad-jobs-backend:v2
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: postgres-secret
          env:
            - name: POSTGRES_HOST
              value: postgres
            - name: POSTGRES_PORT
              value: "5432"
YAML
```

envFrom supplies the database name, user, and password.
env supplies the Service hostname and port.

imagePullPolicy: Never requires the image to exist on the selected node.

The backend does not need the PostgreSQL PVC.
It connects to the database over the network.

## 6. Inspect and validate

```bash
cat ../03-networking/demo-app/k8s/backend.yaml

git diff -- ../03-networking/demo-app/k8s/backend.yaml

kubectl apply --dry-run=server \
  -f ../03-networking/demo-app/k8s/backend.yaml
```

## 7. Apply and verify

```bash
kubectl apply \
  -f ../03-networking/demo-app/k8s/backend.yaml

kubectl rollout status deployment/backend \
  -n jobs-demo --timeout=120s

kubectl get pods -n jobs-demo -l app=jobs-backend -o wide

kubectl logs -n jobs-demo deployment/backend --tail=50
```

Changing the Pod template causes a rollout.
The replacement container runs the code packaged in v2.

## Troubleshooting

- ErrImageNeverPull: verify image name and import on the assigned node.
- Missing module: verify requirements and rebuild under a new image tag.
- Missing environment variable: inspect the Deployment's env configuration.
- Database connection failure: inspect Service endpoints and database logs.

Use:

```bash
kubectl describe pod -n jobs-demo -l app=jobs-backend
kubectl logs -n jobs-demo deployment/backend --tail=50
```

## Review

1. Why import into both workers?
2. Why is building on the Mac insufficient?
3. What triggers the Deployment rollout?
4. Why does the backend not mount the database PVC?

---

[← Previous](07-connect-fastapi.md) ·
[Next: Verify Integration →](09-verify-database-integration.md)
