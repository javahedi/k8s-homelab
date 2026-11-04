# 11 · Build and deploy your own image

[← Chapter index](README.md)

## Docker in five ideas

| Term | Meaning |
|---|---|
| Dockerfile | Build instructions |
| Image | Packaged application and filesystem layers |
| Container | Running instance of an image |
| Registry | Image distribution service |
| Build context | Directory of files available to the build |

Docker Desktop builds/tests on the Mac. Kubernetes workers run containers using containerd, not your Mac's Docker engine. An image built on the Mac does not automatically appear on workers.

```bash
docker version
docker buildx version
kubectl get nodes -o custom-columns='NODE:.metadata.name,ARCH:.status.nodeInfo.architecture'
```

Expected lab architecture arm64. If docker version shows Client only and cannot connect to docker.sock, start Docker Desktop and wait for docker ps to succeed. Don't alter unrelated DoppleJa containers during this exercise.

## Create the IT company website

```bash
mkdir -p 02-workloads/custom-app
```

Save as custom-app/index.html (or retain the richer Javad IT page built in the session):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Javad IT | Cloud & Infrastructure</title>
  <style>
    body { margin:0; background:#0b1120; color:#e2e8f0; font-family:system-ui,sans-serif; line-height:1.6; }
    main { max-width:960px; margin:auto; padding:60px 24px; }
    h1 { font-size:clamp(36px,7vw,68px); line-height:1.1; }
    h2,nav { color:#38bdf8; }
    section { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; }
    article { background:#162033; padding:24px; border-radius:16px; }
    footer { margin-top:48px; color:#94a3b8; }
  </style>
</head>
<body><main>
  <nav>Javad IT.</nav>
  <p>Cloud · Linux · Kubernetes</p>
  <h1>Your infrastructure.<br>Our expertise.</h1>
  <p>Reliable IT systems so you can focus on your business.</p>
  <section aria-label="Services">
    <article><h2>Cloud Infrastructure</h2><p>Scalable application environments.</p></article>
    <article><h2>Kubernetes & Containers</h2><p>Deployments and application operations.</p></article>
    <article><h2>Linux & Automation</h2><p>Reliable servers and repeatable workflows.</p></article>
  </section>
  <footer>Javad IT · Homelab demonstration · Version 1.0</footer>
</main></body>
</html>
```

Save custom-app/Dockerfile:

```dockerfile
FROM nginx:stable-alpine
COPY index.html /usr/share/nginx/html/index.html
```

FROM reuses an existing image; COPY builds our page into the new image. Default Nginx startup is inherited. No custom startup script is needed.

```bash
docker build -t javad-it:1.0 02-workloads/custom-app
docker run -d --name javad-it-preview -p 8088:80 javad-it:1.0
docker ps
docker logs javad-it-preview
```

Open http://localhost:8088. -d backgrounds the container; -p maps Mac:container port. If the name already exists inspect with docker ps -a; remove only this disposable preview with docker rm -f javad-it-preview before rerunning. Building doesn't start a container. Editing HTML after building doesn't alter the image; rebuild and recreate to include changes. Use distinct tags for later releases.

## Transfer to both workers

```bash
docker save -o /tmp/javad-it-1.0.tar javad-it:1.0
for node in worker1 worker2; do
  multipass transfer /tmp/javad-it-1.0.tar "$node":/tmp/javad-it-1.0.tar
  multipass exec "$node" -- sudo ctr -n k8s.io images import /tmp/javad-it-1.0.tar
done
multipass exec worker1 -- sudo ctr -n k8s.io images ls -q
multipass exec worker2 -- sudo ctr -n k8s.io images ls -q
```

Both should list docker.io/library/javad-it:1.0. containerd namespace k8s.io is NOT Kubernetes namespace workloads. Import on both eligible workers because scheduling can choose either. Our lab lacked crictl; `command not found` meant verification tool absent, not import failure. If available, correct global-flag form is `sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock images`.

If terminal appears frozen, Ctrl+Q resumes output paused by Ctrl+S; Ctrl+C interrupts. An unfinished shell prompt needs quote/continuation correction. If unresponsive, open a new tab and check multipass list and kubectl get nodes. The exact cause of our stuck tab wasn't established; all nodes later reported Ready. Do not assume a frozen client means cluster failure.

## Generate Deployment and Service

```bash
kubectl create deployment javad-it -n workloads --image=javad-it:1.0 --replicas=2 --dry-run=client -o yaml > 02-workloads/manifests/javad-it-deployment.yaml
```

Add imagePullPolicy: Never alongside image/name in its container. Apply:

```bash
kubectl apply -f 02-workloads/manifests/javad-it-deployment.yaml
kubectl rollout status deployment/javad-it -n workloads --timeout=120s
kubectl get pods -n workloads -l app=javad-it -o wide
kubectl expose deployment javad-it -n workloads --name=javad-it --port=80 --target-port=80 --type=ClusterIP --dry-run=client -o yaml > 02-workloads/manifests/javad-it-service.yaml
kubectl apply -f 02-workloads/manifests/javad-it-service.yaml
kubectl exec -n workloads nginx-pair -c observer -- wget -q -O - http://javad-it
kubectl port-forward -n workloads service/javad-it 8089:80
```

Open http://localhost:8089. This is Kubernetes, while 8088 was the local Docker preview. Port-forward to a Service selects a backing Pod; it is not a test of Service VIP load balancing. The observer request tests the in-cluster Service path. Never requires a locally present image: ErrImageNeverPull means check name/tag/import on assigned node. For normal distribution use a registry and suitable imagePullPolicy; manual import is a lab technique, not a scalable production delivery method.

Ctrl+C stops forwarding. Optional archive cleanup after successful import/deployment:

```bash
rm /tmp/javad-it-1.0.tar
multipass exec worker1 -- rm /tmp/javad-it-1.0.tar
multipass exec worker2 -- rm /tmp/javad-it-1.0.tar
```

Removing archives does not remove imported images. Keep source, Dockerfile and manifests in Git, not image tar archives.

---

[← Chapter index](README.md)
