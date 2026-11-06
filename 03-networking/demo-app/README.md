# Javad Jobs: From Local Application to Kubernetes Ingress

This lab builds a small job website step by step:
local Python → Docker → Docker Compose → Kubernetes → Ingress.

The frontend uses HTML, CSS, and JavaScript.
FastAPI returns two example jobs.
There is no database or real authentication in this version.

## 1. Understand the tools

| Tool | Purpose |
|---|---|
| Multipass | Runs our three Ubuntu VMs |
| Docker | Builds images and runs containers on the Mac |
| Docker Compose | Runs frontend and backend containers together |
| containerd | Runs containers inside our Kubernetes nodes |
| kubectl | Manages Kubernetes using our kubeconfig |
| Helm | Installs packaged Kubernetes applications |
| Traefik | Implements our Ingress routing rules |

kubectl and Helm run on the Mac.
The Kubernetes control plane and application Pods run inside the VMs.

## 2. Project files

| File | Purpose |
|---|---|
| backend/main.py | FastAPI application |
| backend/requirements.txt | Python dependencies |
| frontend/index.html | Page, styling, and browser JavaScript |
| Dockerfile | Original combined application image |
| backend/Dockerfile | Separate backend image |
| frontend/Dockerfile | Separate Nginx frontend image |
| frontend/nginx.conf | Nginx page serving and API proxy rules |
| compose.yaml | Runs the two containers together |
| k8s/backend.yaml | Backend Deployment |
| k8s/backend-service.yaml | Backend ClusterIP Service |
| k8s/frontend.yaml | Frontend Deployment |
| k8s/frontend-service.yaml | Frontend NodePort Service |
| k8s/jobs-ingress.yaml | Website hostname and path routing |
| k8s/traefik-values.yaml | Our Helm configuration overrides |
| k8s/traefik-default-values.yaml | Reference copy of chart defaults |
| k8s/traefik-rendered.yaml | Generated YAML used for inspection |

## 3. Local application

From this directory, activate the Python environment and start FastAPI:

```bash
source .venv/bin/activate
python -m uvicorn backend.main:app --reload --port 8000
```

The initial local setup lets FastAPI serve both the HTML page and API.

- `/` returns the page.
- `/api/health` returns health information.
- `/api/jobs` returns job data.
- `/docs` provides interactive API documentation.

Clicking “Load jobs” makes browser JavaScript request `/api/jobs`.
The browser receives JSON and displays the jobs.

## 4. One Docker container

Stop local Uvicorn before using the same host port.

```bash
docker build -t javad-jobs:v1 .
docker run --name javad-jobs --rm -p 8000:8000 javad-jobs:v1
```

Open http://localhost:8000.

The root Dockerfile packages the frontend and backend together.
Uvicorn listens on `0.0.0.0` so it accepts traffic through the
container network interface.

Stop the container with Ctrl+C.

## 5. Two containers with Docker Compose

```bash
docker compose up -d --build
docker compose ps
```

Open http://localhost:8080.

| Request | What happens |
|---|---|
| `/` | Nginx serves index.html |
| `/api/jobs` | Nginx proxies to backend:8000/api/jobs |

Compose builds each image using its folder's Dockerfile.
The original root Dockerfile is not used by this Compose configuration.

The service name `backend` resolves through Docker's internal DNS.
Inside the frontend container, `localhost` means the frontend container itself.

Test communication from inside the frontend:

```bash
docker compose exec frontend wget -qO- http://backend:8000/api/jobs
```

Stop the Compose application:

```bash
docker compose down
```

## 6. Make images available to Kubernetes workers

The Mac's Docker image store is separate from each worker's containerd store.

Tag and export the images:

```bash
docker tag demo-app-backend javad-jobs-backend:v1
docker tag demo-app-frontend javad-jobs-frontend:v1

docker save -o /tmp/javad-jobs-v1.tar \
  javad-jobs-backend:v1 \
  javad-jobs-frontend:v1
```

Copy and import on both workers:

```bash
multipass transfer /tmp/javad-jobs-v1.tar worker1:/tmp/javad-jobs-v1.tar
multipass transfer /tmp/javad-jobs-v1.tar worker2:/tmp/javad-jobs-v1.tar

multipass exec worker1 -- sudo ctr -n k8s.io images import /tmp/javad-jobs-v1.tar
multipass exec worker2 -- sudo ctr -n k8s.io images import /tmp/javad-jobs-v1.tar
```

Verify:

```bash
multipass exec worker1 -- sudo ctr -n k8s.io images ls -q
multipass exec worker2 -- sudo ctr -n k8s.io images ls -q
```

`k8s.io` is a containerd namespace, not a Kubernetes namespace.
It does not appear in `kubectl get namespaces`.

The Deployments use `imagePullPolicy: Never` to use imported images.
Every node eligible to run these Pods needs those images.

In a typical company setup, nodes download application images from a registry.

## 7. Kubernetes Deployments and Services

Create the application namespace if it does not already exist:

```bash
kubectl create namespace jobs-demo --dry-run=client -o yaml | kubectl apply -f -
```

Apply these resources individually:

```bash
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Check:

```bash
kubectl get pods -n jobs-demo -o wide
kubectl get services -n jobs-demo
kubectl get endpointslices -n jobs-demo
```

A Deployment maintains the desired Pods through a ReplicaSet.
Its selector must match the labels in its Pod template.

A Service selects destination Pods using labels and gives them
a stable address and DNS name.

| Service | Type | Purpose |
|---|---|---|
| backend | ClusterIP | Internal access to FastAPI on port 8000 |
| frontend | NodePort | Access to Nginx through a node IP and exposed port |

ClusterIP works across the cluster, including between different nodes.
NodePort adds access through a reachable node IP.

The existing Nginx destination `backend:8000` now resolves to the
Kubernetes backend Service in the same namespace.

During this lab, the frontend NodePort was `31554`:

http://192.168.252.3:31554

Check the actual port after recreating the Service; it may change.

## 8. Our blueprint-first workflow

Generate YAML before creating resources:

```bash
kubectl expose deployment backend \
  -n jobs-demo \
  --name=backend \
  --type=ClusterIP \
  --port=8000 \
  --target-port=8000 \
  --dry-run=client -o yaml
```

`--dry-run=client -o yaml` prints the resource without creating it.
Redirect output to a file, inspect it, edit it, then apply it.

When using multiline shell commands, the backslash must be the final
character on its line: do not put spaces after it.

## 9. Install the Traefik controller using Helm

Helm uses kubeconfig to reach the cluster, like kubectl.
A chart is an installation package; a release is one installation of it.

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm search repo traefik/traefik
```

Adding a repository only tells Helm where to find charts.

Our lab used chart version `42.3.0`, installing Traefik `v3.7.17`.

Our override file, `k8s/traefik-values.yaml`:

```yaml
service:
  spec:
    type: NodePort
```

We used NodePort because this homelab has no external load balancer configured.

Generate an inspection copy:

```bash
helm template traefik traefik/traefik \
  --version 42.3.0 \
  --namespace traefik \
  -f k8s/traefik-values.yaml \
  > k8s/traefik-rendered.yaml
```

Install through Helm:

```bash
helm install traefik traefik/traefik \
  --version 42.3.0 \
  --namespace traefik \
  --create-namespace \
  -f k8s/traefik-values.yaml
```

Run `helm install` once for this release.
Do not separately apply the rendered inspection copy.

Verify:

```bash
helm list -n traefik
kubectl get pods,services -n traefik
kubectl get ingressclasses
```

## 10. Ingress routing

Ingress contains instructions.
Traefik reads those instructions and handles HTTP traffic.

Our Ingress belongs to namespace `jobs-demo` and uses class `traefik`.

| Host | Path prefix | Destination |
|---|---|---|
| jobs.lab | / | frontend:80 |
| jobs.lab | /api | backend:8000 |

The more specific `/api` prefix wins over `/`.
The request path is preserved, matching FastAPI's `/api/jobs` endpoint.

Apply and inspect:

```bash
kubectl apply -f k8s/jobs-ingress.yaml
kubectl get ingress -n jobs-demo
```

During this lab, Traefik's HTTP NodePort was `32118`.

```bash
curl -H 'Host: jobs.lab' http://192.168.252.3:32118/
curl -H 'Host: jobs.lab' http://192.168.252.3:32118/api/jobs
```

The Host header matches the Ingress hostname without changing local DNS.

Expected API response:

```json
[
  {"id":1,"title":"Python Developer","city":"Berlin"},
  {"id":2,"title":"Kubernetes Administrator","city":"Bremen"}
]
```

Check the actual Traefik NodePort after reinstalling it; it may change.
HTTPS was not configured in this lab.

## 11. Compare our two entrances

| Entrance during this lab | Routing decision |
|---|---|
| Node IP port 31554 | Frontend Nginx uses nginx.conf |
| Node IP port 32118, Host jobs.lab | Traefik uses the Ingress resource |

Through the original frontend entrance, Nginx proxies API requests.

Through the Traefik entrance:
- `/` goes to the frontend Service.
- `/api/jobs` goes directly to the backend Service.

Helm installs the controller; it does not process website requests.
NodePort still provides access to Traefik in this homelab.
Ingress adds hostname and path routing.

## 12. Troubleshooting checklist

```bash
kubectl get nodes
kubectl get pods,services -n jobs-demo
kubectl get endpointslices -n jobs-demo
kubectl get ingress -n jobs-demo
kubectl describe ingress jobs -n jobs-demo
kubectl logs -n jobs-demo deployment/backend
kubectl logs -n jobs-demo deployment/frontend
kubectl logs -n traefik deployment/traefik
```

- Missing imported image: check the image store on the Pod's assigned node.
- Service has no endpoints: compare its selector with Pod labels.
- Traefik returns 404: check the Host header, path, and Ingress class.
- Backend request fails: check the Service port, endpoints, and backend logs.

## Chapter completed

We successfully ran the same application locally, in Docker, in Compose,
and in Kubernetes, then routed requests through an Ingress controller.

Gateway API remains a separate future lesson.
EOFcat > README.md <<'EOF'
# Javad Jobs: From Local Application to Kubernetes Ingress

This lab builds a small job website step by step:
local Python → Docker → Docker Compose → Kubernetes → Ingress.

The frontend uses HTML, CSS, and JavaScript.
FastAPI returns two example jobs.
There is no database or real authentication in this version.

## 1. Understand the tools

| Tool | Purpose |
|---|---|
| Multipass | Runs our three Ubuntu VMs |
| Docker | Builds images and runs containers on the Mac |
| Docker Compose | Runs frontend and backend containers together |
| containerd | Runs containers inside our Kubernetes nodes |
| kubectl | Manages Kubernetes using our kubeconfig |
| Helm | Installs packaged Kubernetes applications |
| Traefik | Implements our Ingress routing rules |

kubectl and Helm run on the Mac.
The Kubernetes control plane and application Pods run inside the VMs.

## 2. Project files

| File | Purpose |
|---|---|
| backend/main.py | FastAPI application |
| backend/requirements.txt | Python dependencies |
| frontend/index.html | Page, styling, and browser JavaScript |
| Dockerfile | Original combined application image |
| backend/Dockerfile | Separate backend image |
| frontend/Dockerfile | Separate Nginx frontend image |
| frontend/nginx.conf | Nginx page serving and API proxy rules |
| compose.yaml | Runs the two containers together |
| k8s/backend.yaml | Backend Deployment |
| k8s/backend-service.yaml | Backend ClusterIP Service |
| k8s/frontend.yaml | Frontend Deployment |
| k8s/frontend-service.yaml | Frontend NodePort Service |
| k8s/jobs-ingress.yaml | Website hostname and path routing |
| k8s/traefik-values.yaml | Our Helm configuration overrides |
| k8s/traefik-default-values.yaml | Reference copy of chart defaults |
| k8s/traefik-rendered.yaml | Generated YAML used for inspection |

## 3. Local application

From this directory, activate the Python environment and start FastAPI:

```bash
source .venv/bin/activate
python -m uvicorn backend.main:app --reload --port 8000
```

The initial local setup lets FastAPI serve both the HTML page and API.

- `/` returns the page.
- `/api/health` returns health information.
- `/api/jobs` returns job data.
- `/docs` provides interactive API documentation.

Clicking “Load jobs” makes browser JavaScript request `/api/jobs`.
The browser receives JSON and displays the jobs.

## 4. One Docker container

Stop local Uvicorn before using the same host port.

```bash
docker build -t javad-jobs:v1 .
docker run --name javad-jobs --rm -p 8000:8000 javad-jobs:v1
```

Open http://localhost:8000.

The root Dockerfile packages the frontend and backend together.
Uvicorn listens on `0.0.0.0` so it accepts traffic through the
container network interface.

Stop the container with Ctrl+C.

## 5. Two containers with Docker Compose

```bash
docker compose up -d --build
docker compose ps
```

Open http://localhost:8080.

| Request | What happens |
|---|---|
| `/` | Nginx serves index.html |
| `/api/jobs` | Nginx proxies to backend:8000/api/jobs |

Compose builds each image using its folder's Dockerfile.
The original root Dockerfile is not used by this Compose configuration.

The service name `backend` resolves through Docker's internal DNS.
Inside the frontend container, `localhost` means the frontend container itself.

Test communication from inside the frontend:

```bash
docker compose exec frontend wget -qO- http://backend:8000/api/jobs
```

Stop the Compose application:

```bash
docker compose down
```

## 6. Make images available to Kubernetes workers

The Mac's Docker image store is separate from each worker's containerd store.

Tag and export the images:

```bash
docker tag demo-app-backend javad-jobs-backend:v1
docker tag demo-app-frontend javad-jobs-frontend:v1

docker save -o /tmp/javad-jobs-v1.tar \
  javad-jobs-backend:v1 \
  javad-jobs-frontend:v1
```

Copy and import on both workers:

```bash
multipass transfer /tmp/javad-jobs-v1.tar worker1:/tmp/javad-jobs-v1.tar
multipass transfer /tmp/javad-jobs-v1.tar worker2:/tmp/javad-jobs-v1.tar

multipass exec worker1 -- sudo ctr -n k8s.io images import /tmp/javad-jobs-v1.tar
multipass exec worker2 -- sudo ctr -n k8s.io images import /tmp/javad-jobs-v1.tar
```

Verify:

```bash
multipass exec worker1 -- sudo ctr -n k8s.io images ls -q
multipass exec worker2 -- sudo ctr -n k8s.io images ls -q
```

`k8s.io` is a containerd namespace, not a Kubernetes namespace.
It does not appear in `kubectl get namespaces`.

The Deployments use `imagePullPolicy: Never` to use imported images.
Every node eligible to run these Pods needs those images.

In a typical company setup, nodes download application images from a registry.

## 7. Kubernetes Deployments and Services

Create the application namespace if it does not already exist:

```bash
kubectl create namespace jobs-demo --dry-run=client -o yaml | kubectl apply -f -
```

Apply these resources individually:

```bash
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Check:

```bash
kubectl get pods -n jobs-demo -o wide
kubectl get services -n jobs-demo
kubectl get endpointslices -n jobs-demo
```

A Deployment maintains the desired Pods through a ReplicaSet.
Its selector must match the labels in its Pod template.

A Service selects destination Pods using labels and gives them
a stable address and DNS name.

| Service | Type | Purpose |
|---|---|---|
| backend | ClusterIP | Internal access to FastAPI on port 8000 |
| frontend | NodePort | Access to Nginx through a node IP and exposed port |

ClusterIP works across the cluster, including between different nodes.
NodePort adds access through a reachable node IP.

The existing Nginx destination `backend:8000` now resolves to the
Kubernetes backend Service in the same namespace.

During this lab, the frontend NodePort was `31554`:

http://192.168.252.3:31554

Check the actual port after recreating the Service; it may change.

## 8. Our blueprint-first workflow

Generate YAML before creating resources:

```bash
kubectl expose deployment backend \
  -n jobs-demo \
  --name=backend \
  --type=ClusterIP \
  --port=8000 \
  --target-port=8000 \
  --dry-run=client -o yaml
```

`--dry-run=client -o yaml` prints the resource without creating it.
Redirect output to a file, inspect it, edit it, then apply it.

When using multiline shell commands, the backslash must be the final
character on its line: do not put spaces after it.

## 9. Install the Traefik controller using Helm

Helm uses kubeconfig to reach the cluster, like kubectl.
A chart is an installation package; a release is one installation of it.

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm search repo traefik/traefik
```

Adding a repository only tells Helm where to find charts.

Our lab used chart version `42.3.0`, installing Traefik `v3.7.17`.

Our override file, `k8s/traefik-values.yaml`:

```yaml
service:
  spec:
    type: NodePort
```

We used NodePort because this homelab has no external load balancer configured.

Generate an inspection copy:

```bash
helm template traefik traefik/traefik \
  --version 42.3.0 \
  --namespace traefik \
  -f k8s/traefik-values.yaml \
  > k8s/traefik-rendered.yaml
```

Install through Helm:

```bash
helm install traefik traefik/traefik \
  --version 42.3.0 \
  --namespace traefik \
  --create-namespace \
  -f k8s/traefik-values.yaml
```

Run `helm install` once for this release.
Do not separately apply the rendered inspection copy.

Verify:

```bash
helm list -n traefik
kubectl get pods,services -n traefik
kubectl get ingressclasses
```

## 10. Ingress routing

Ingress contains instructions.
Traefik reads those instructions and handles HTTP traffic.

Our Ingress belongs to namespace `jobs-demo` and uses class `traefik`.

| Host | Path prefix | Destination |
|---|---|---|
| jobs.lab | / | frontend:80 |
| jobs.lab | /api | backend:8000 |

The more specific `/api` prefix wins over `/`.
The request path is preserved, matching FastAPI's `/api/jobs` endpoint.

Apply and inspect:

```bash
kubectl apply -f k8s/jobs-ingress.yaml
kubectl get ingress -n jobs-demo
```

During this lab, Traefik's HTTP NodePort was `32118`.

```bash
curl -H 'Host: jobs.lab' http://192.168.252.3:32118/
curl -H 'Host: jobs.lab' http://192.168.252.3:32118/api/jobs
```

The Host header matches the Ingress hostname without changing local DNS.

Expected API response:

```json
[
  {"id":1,"title":"Python Developer","city":"Berlin"},
  {"id":2,"title":"Kubernetes Administrator","city":"Bremen"}
]
```

Check the actual Traefik NodePort after reinstalling it; it may change.
HTTPS was not configured in this lab.

## 11. Compare our two entrances

| Entrance during this lab | Routing decision |
|---|---|
| Node IP port 31554 | Frontend Nginx uses nginx.conf |
| Node IP port 32118, Host jobs.lab | Traefik uses the Ingress resource |

Through the original frontend entrance, Nginx proxies API requests.

Through the Traefik entrance:
- `/` goes to the frontend Service.
- `/api/jobs` goes directly to the backend Service.

Helm installs the controller; it does not process website requests.
NodePort still provides access to Traefik in this homelab.
Ingress adds hostname and path routing.

## 12. Troubleshooting checklist

```bash
kubectl get nodes
kubectl get pods,services -n jobs-demo
kubectl get endpointslices -n jobs-demo
kubectl get ingress -n jobs-demo
kubectl describe ingress jobs -n jobs-demo
kubectl logs -n jobs-demo deployment/backend
kubectl logs -n jobs-demo deployment/frontend
kubectl logs -n traefik deployment/traefik
```

- Missing imported image: check the image store on the Pod's assigned node.
- Service has no endpoints: compare its selector with Pod labels.
- Traefik returns 404: check the Host header, path, and Ingress class.
- Backend request fails: check the Service port, endpoints, and backend logs.

## Chapter completed

We successfully ran the same application locally, in Docker, in Compose,
and in Kubernetes, then routed requests through an Ingress controller.

Gateway API remains a separate future lesson.
