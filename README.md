# Benny's Flask App - Docker, Jenkins & Helm

A small Flask web app that is containerized with Docker, built and pushed to Docker Hub by a Jenkins pipeline, and deployed to Kubernetes with a Helm chart.

## Project structure

```text
.
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Image definition
├── Jenkinsfile         # CI pipeline (checkout, build, push)
└── chart/              # Helm chart
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── _helpers.tpl
        ├── configmap.yaml
        ├── deployment.yaml
        ├── service.yaml
        └── ingress.yaml
```

## The application

`app.py` serves a greeting on `/`. The port comes from the `PORT` environment variable and defaults to `8000`.

## Run with Docker

```bash
docker build -t mileag0/mydevopsproject .
docker run --rm -p 8000:8000 mileag0/mydevopsproject
```

Then open http://localhost:8000. To use another port:

```bash
docker run --rm -e PORT=9000 -p 9000:9000 mileag0/mydevopsproject
```

## Jenkins pipeline

The `Jenkinsfile` has these stages:

1. **Checkout** - gets the code from the repository.
2. **Build** - builds the image and tags it with the build number and `latest`.
3. **Security Scan** - scans the image with Trivy (run as a Docker container). The build fails on HIGH or CRITICAL vulnerabilities that have a fix available; unfixed ones in the base image are ignored.
4. **Push** - logs in to Docker Hub and pushes both tags.
5. **Update GitOps** - writes the new image tag to the GitOps repo so Argo CD deploys it.

Setup needed in Jenkins:

- Docker installed on the Jenkins machine.
- A "Username with password" credential with the ID `dockerhub-creds` (Docker Hub username + access token).
- A Pipeline job pointing at this repository ("Pipeline script from SCM").

The pipeline uses `bat` steps because Jenkins runs on Windows here. On a Linux agent they would need to be changed to `sh`.

## Deploy with Helm

The chart's default image is `mileag0/mydevopsproject:latest`, which is the image Jenkins pushes.

```bash
helm lint chart
helm install benny chart
```

To deploy a specific Jenkins build instead of `latest`:

```bash
helm upgrade --install benny chart --set image.tag=<BUILD_NUMBER>
```

Check that it is running:

```bash
kubectl get pods
kubectl get svc
```

Access the app locally (works on any cluster, e.g. Docker Desktop or Minikube):

```bash
kubectl port-forward svc/benny-benny-app 8080:80
```

and open http://localhost:8080.

### What the chart creates

- **Deployment** - 2 replicas by default, with readiness/liveness probes and CPU/memory limits.
- **ConfigMap** - holds the values under `env` in `values.yaml` (currently `PORT`) and passes them to the container as environment variables.
- **Service** - type `LoadBalancer`, port 80 forwarding to container port 8000.
- **Ingress** - optional, disabled by default. Enable with `--set ingress.enabled=true` (host is `benny.local`) if an ingress controller is installed.

### Main values

| Value | Default | Description |
|---|---|---|
| `replicaCount` | `2` | Number of pods |
| `image.repository` | `mileag0/mydevopsproject` | Docker Hub image |
| `image.tag` | `latest` | Image tag |
| `service.type` | `LoadBalancer` | Service type |
| `service.port` / `service.targetPort` | `80` / `8000` | Service and container ports |
| `env.PORT` | `"8000"` | Port the app listens on |

## Clean up

```bash
helm uninstall benny
```
