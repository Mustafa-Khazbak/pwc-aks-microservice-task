# PWC Microservice Deployment on AKS

This project deploys a **Python Flask microservice** on **Azure Kubernetes Service (AKS)** using **Azure Portal**. The application features secure ingress via **Nginx Ingress Controller** with TLS termination and integrated monitoring using **Prometheus** , **Grafana** and **AlertManager**.

---

## Architecture

### High-Level Architecture
```
Internet
    |
    | HTTPS (443) / HTTP (80)
    ↓
Azure Load Balancer (20.174.112.243)
    |
    | HTTP Redirect → HTTPS
    ↓
Nginx Ingress Controller
    |
    | TLS Termination (Self-signed certificate)
    ↓
PWC Microservice Service (ClusterIP: 5000)
    |
    ↓
PWC Microservice Pods (2 replicas)
    |
    | Flask Application (Gunicorn)
    ↓
Backend Logic
    |
    ├─→ /users endpoint
    ├─→ /products endpoint
    ├─→ /health endpoint
    └─→ /metrics endpoint (Prometheus)
```

### Infrastructure Components

- **AKS Cluster**: Managed Kubernetes cluster deployed via Azure Portal
- **Azure Load Balancer**: External load balancer with public IP (20.174.112.243)
- **Nginx Ingress Controller**: Handles traffic routing and TLS termination
- **Flask Microservice**: 2 replicas for high availability
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization and dashboards

---
---

## Code Modifications and Extensions

The following modifications and extensions were implemented on the base Flask microservice to enable production-grade capabilities for AKS deployment:

### Added Features

- **Logging**: Structured logging for real-time log access, with architecture designed for future EFK (Elasticsearch, Fluentbit, Kibana) stack integration
- **Metrics**: Prometheus-compatible metrics endpoint for standard application monitoring. Custom application metrics for business-specific KPIs and performance tracking
- **Health Monitoring**: Liveness and readiness probes for Kubernetes automated health checks and self-healing

---

### Technical Implementation

### New Routes (`app/routes/`)
- **`health_routes.py`**: `/health` endpoint for Kubernetes probes
- **`metrics_routes.py`**: `/metrics` endpoint for Prometheus scraping
- - **`user_routes.py` & `product_routes.py`**: Instrumented with custom metrics:
  - `user_requests_total`: Total number of requests to `/users` endpoint
  - `product_processing_seconds`: Processing time for `/products` endpoint requests

### Service Layer (`app/services/`)
- **`logging_service.py`**: Centralized structured logging for all HTTP requests and responses. Captures request method, path, client IP, response status. EFK stack-ready format for seamless integration
- **`metrics_service.py`**: Metric registration and updates

### Application Initialization (`app/__init__.py`)
- **Prometheus Integration**: `PrometheusMetrics(app)` automatically exports Flask metrics
- **Structured Logging**: `setup_logging(app)` initializes JSON logs for easy parsing in centralized log systems
- **Request Lifecycle Hooks**: `before_request` logs request metadata. `after_request` logs response details and status
- **Blueprint Registration**: Registers all app routes (`users`, `products`, `health`, `metrics`) cleanly for modular organization

---
---
## Dockerfile

**Multi-stage build** for optimized image size:

- **Stage 1 (Builder)**: Installs Python dependencies using `requirements.txt`
- **Stage 2 (Runtime)**: Copies only necessary files and dependencies from builder stage

**Security**: Runs application as non-root user (`appuser`)

**Production Setup**: Uses Gunicorn WSGI server on port 5000

### Docker Build and Deployment

### Build Docker Image
```bash
docker build -t pwc-microservice:1.0.0 .
```

### Test Locally
```bash
docker run -d -p 5000:5000 --name pwc-microservice pwc-microservice:1.0.0
```

### Azure Container Registry (ACR) Push

**1. Set Azure Subscription**
```bash
az account list --output table
az account set --subscription "Azure subscription 1 - Personal"
```

**2. Get ACR Access Token**
```bash
az acr login --name pwcregistry --expose-token
```

This command returns a JSON response with `username` and `Token` for Docker login.

**3. Docker Login to ACR**
```bash
docker login pwcregistry-hbfzbwfzd5d9d5dw.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p <TOKEN>
```
![ACR Login](README_images/acr-login.png)
**4. Tag Image**
```bash
docker tag pwc-microservice:1.0.0 pwcregistry-hbfzbwfzd5d9d5dw.azurecr.io/pwc-microservice:1.0.0
```

**5. Push to ACR**
```bash
docker push pwcregistry-hbfzbwfzd5d9d5dw.azurecr.io/pwc-microservice:1.0.0
```

**6. Verify Image in ACR**
```bash
az acr repository list -n pwcregistry --output table
```
![ACR Output](README_images/acr-image-output.png)

---
---

## Infrastructure as Code (Terraform)

### Overview
Terraform configuration provisions AKS cluster and integrates with existing Azure resources.

### Files

**`providers.tf`**  
Configures required providers: `azurerm` and `azapi`  for Azure resource management.

**`variables.tf`**  
Defines infrastructure variables: resource group name, AKS cluster name, node count, VM size, and ACR name.

**`main.tf`**  
- References existing Resource Group and Azure Container Registry (ACR)
- Creates AKS cluster with system-assigned managed identity
- Configures default node pool with Azure CNI networking
- Enables RBAC for access control
- Grants AKS `AcrPull` permission to pull images from ACR

**`ssh.tf`**  
Generates SSH key pair for AKS node access using Azure API.

**`output.tf`**  
Exports AKS cluster name, FQDN, and kubeconfig for cluster access.

## Infrastructure as Code (Terraform)

### Overview
Terraform configuration provisions AKS cluster and integrates with existing Azure resources.

### Files

**`providers.tf`**  
Configures required providers: `azurerm` and `azapi` for Azure resource management.

**`variables.tf`**  
Defines infrastructure variables: resource group name, AKS cluster name, node count, VM size, and ACR name.

**`main.tf`**  
- References existing Resource Group and Azure Container Registry (ACR)
- Creates AKS cluster with system-assigned managed identity
- Configures default node pool with Azure CNI networking
- Enables RBAC for access control
- Grants AKS `AcrPull` permission to pull images from ACR

**`ssh.tf`**  
Generates SSH key pair for AKS node access using Azure API.

**`output.tf`**  
Exports AKS cluster name, FQDN, and kubeconfig for cluster access.

---

### Execution

**1. Initialize Terraform**
```bash
terraform init
```

**2. Validate Configuration**
```bash
terraform validate
```

**3. Preview Changes**
```bash
terraform plan -out=tfplan
```

**4. Apply Infrastructure**
```bash
terraform apply tfplan
```
![Terraform Apply Output](README_images/apply-terraform.png)

**5. Verify AKS Cluster**
```bash
az aks list --output table
```

**6. Get AKS Credentials**
```bash
az aks get-credentials --resource-group Pwc-DevOps-Task --name pwc-aks
```

**7. Verify Cluster Access**
```bash
kubectl get nodes
```
![Terraform Output](README_images/Terraform-Output.png)
---
---
## Kubernetes Deployment

### Deploys the Flask microservice with high availability and health monitoring

**Key Configuration**:
- **Replicas**: 2 pods for high availability
- **Image**: `pwcregistry-hbfzbwfzd5d9d5dw.azurecr.io/pwc-microservice:1.0.0`

**Container Configuration**:
- **Port**: 5000 (HTTP)
- **Environment Variables**:
  - `FLASK_ENV=production`
  - `PORT=5000`

**Health Probes**:
- **Liveness Probe**: `/health` 
- **Readiness Probe**: `/health` 
 
Both **liveness** and **readiness** probes use the same `/health` endpoint.

**Why?**

This Flask microservice is stateless and doesn't depend on external services (databases, message queues, etc.). If the `/health` endpoint returns `200 OK`, it means:
- The application process is alive and responsive
- The Flask server is ready to handle requests

Since the application has no external dependencies, a single health check is sufficient for both probes. This approach is simpler, cleaner, and fully compatible with Kubernetes best practices.

---

**Apply Deployment**:
```bash
kubectl create namespace pwc-microservice
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```
![pwc-microserice namespace](README_images/pwc-microserice-namespace.png)
---
---

## Ingress Configuration (HTTPS/TLS)

### Overview

Secure ingress implementation using **Nginx Ingress Controller** with TLS termination and automatic HTTP to HTTPS redirection.

**External Access**: `https://20.174.112.243`


### Implementation Steps

**1. Install Nginx Ingress Controller**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml

**2. Generate Self-Signed Certificate**
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout pwc-tls.key \
  -out pwc-tls.crt \
  -subj "/CN=pwc-microservice.local/O=PWC"
```

**3. Create TLS Secret**
```bash
kubectl create secret tls pwc-tls-secret \
  --cert=pwc-tls.crt \
  --key=pwc-tls.key \
  -n pwc-microservice
```

**4. Apply Ingress Configuration**
```bash
kubectl apply -f ingress.yaml
```

**5. Verify Deployment**
```bash
kubectl get ingress -n pwc-microservice
kubectl get svc -n ingress-nginx
```

---

### Testing

**Get Ingress IP**:
```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

**Test Endpoints**:
```bash
INGRESS_IP="20.174.112.243"

# HTTP redirects to HTTPS
curl -I http://$INGRESS_IP/health

# HTTPS endpoints
curl -k https://$INGRESS_IP/health
curl -k https://$INGRESS_IP/users
curl -k https://$INGRESS_IP/products
```
---
![ingress](README_images/ingress.png)
![user](README_images/users.png)

### Security Notes

**Current Setup**:
- **Self-signed certificate**: Suitable for testing/internal use
- **TLS termination**: At Ingress level (traffic to pods is HTTP)
- **HTTP redirect**: All traffic forced to HTTPS
  
---
---
## Monitoring Stack Configuration on AKS 

### Overview

Prometheus and Grafana were configured in the AKS cluster to monitor the PWC Flask Microservice, expose both UIs securely over HTTPS using NGINX Ingress, and enable metric collection using Prometheus ServiceMonitor
---

### Helm Installation Steps

**1. Create Monitoring Namespace**
```bash
kubectl create namespace monitoring
```

**2. Add Prometheus Community Helm Repository**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

**3. Install kube-prometheus-stack**
```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
```

**4. Verify Installation**
```bash
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

---

![Helm-monitoring](README_images/monitoring.png)

---
### Prometheus & Grafana Configuration
- Secure HTTPS UI access
- Automatic metric scraping via `ServiceMonitor`
- Cluster + application dashboards in Grafana

| Component     | Version / Chart          | Namespace       | Exposure                                  | Authentication       |
|--------------|--------------------------|----------------|-------------------------------------------|---------------------|
| Prometheus   | kube-prometheus-stack    | `monitoring`    | HTTPS `/prometheus` via Ingress           | TLS (self-signed)   |
| Grafana      | kube-prometheus-stack    | `monitoring`    | HTTPS `/grafana` via Ingress              | Default admin login |
| Flask App    | Python + `prometheus_client` | `pwc-microservice` | `/metrics` endpoint                      | ServiceMonitor      |

### Update Prometheus Base Path
```bash
kubectl edit prometheus -n monitoring kube-prometheus-stack-prometheus
```
- externalUrl: "https://<INGRESS_IP>/prometheus"
- routePrefix: "/prometheus"

![Prom-Base](README_images/Base.png)

```bash
kubectl apply -f prometheus-ingress.yaml
```
### Configure Grafana to serve from /grafana
```bash
kubectl -n monitoring edit configmap kube-prometheus-stack-grafana
```
- root_url = https://<INGRESS_IP>/grafana
- serve_from_sub_path = true

![/grafana](README_images/grafana.png)

```bash
kubectl -n monitoring edit configmap kube-prometheus-stack-grafana-datasource
```
- Set url to url: http://kube-prometheus-stack-prometheus.monitoring.svc.cluster.local:9090/prometheus

```bash
kubectl -n monitoring rollout restart deployment kube-prometheus-stack-grafana
```
### Access URLs

**Grafana Dashboard**: `https://20.174.112.243/grafana`  
![grafana-ui](README_images/grafana-ui.png)
**Prometheus UI**: `https://20.174.112.243/prometheus`
![prom-ui](README_images/prom-ui.png)





### Custom Application Dashboards

#### 1. PWC Microservice Performance Dashboard (Custom Metrics)

![dashboard1](README_images/dashboard1.png)

**Purpose**: Demonstrates custom application metrics.

**Custom Metrics Implemented**:
- `user_requests_total`: Counter tracking total requests to `/users` endpoint
- `product_processing_seconds`: Summary measuring processing time for `/products` endpoint

### Python Application Performance Dashboard
![dashboard1](README_images/dashboard2.png)
**Purpose**: Insight into Python runtime performance, memory behavior, and Flask request latency.


### System Dashboards (Auto-Provisioned)

When Grafana is deployed using the **kube-prometheus-stack** Helm chart, cluster-level dashboards are automatically installed for complete infrastructure observability.

![dashboard3](README_images/dashboard3.png)