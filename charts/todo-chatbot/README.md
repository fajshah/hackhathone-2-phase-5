# Todo Chatbot Helm Chart

This Helm chart deploys the Todo Chatbot application on Kubernetes.

## Prerequisites

- Kubernetes 1.20+
- Helm 3.x
- PV provisioner support in the underlying infrastructure (for database persistence)

## Installing the Chart

To install the chart with the release name `todo-chatbot`:

```bash
helm install todo-chatbot ./charts/todo-chatbot --namespace todo-app --create-namespace
```

## Uninstalling the Chart

To uninstall/delete the `todo-chatbot` release:

```bash
helm delete todo-chatbot -n todo-app
```

## Configuration

The following table lists the configurable parameters of the todo-chatbot chart and their default values.

### Frontend Configuration

| Parameter                      | Description                                     | Default                   |
|-------------------------------|-------------------------------------------------|---------------------------|
| `frontend.replicaCount`       | Number of frontend pods to run                  | `1`                       |
| `frontend.image.repository`   | Frontend image repository                       | `todo-frontend`           |
| `frontend.image.pullPolicy`   | Frontend image pull policy                      | `IfNotPresent`            |
| `frontend.image.tag`          | Frontend image tag                              | `""` (defaults to chart appVersion) |
| `frontend.service.type`       | Type of frontend service                        | `NodePort`                |
| `frontend.service.port`       | Port for frontend service                       | `80`                      |

### Backend Configuration

| Parameter                     | Description                                      | Default                   |
|------------------------------|--------------------------------------------------|---------------------------|
| `backend.replicaCount`       | Number of backend pods to run                    | `1`                       |
| `backend.image.repository`   | Backend image repository                         | `todo-backend`            |
| `backend.image.pullPolicy`   | Backend image pull policy                        | `IfNotPresent`            |
| `backend.image.tag`          | Backend image tag                                | `""` (defaults to chart appVersion) |
| `backend.service.type`       | Type of backend service                          | `ClusterIP`               |
| `backend.service.port`       | Port for backend service                         | `8000`                    |

### Database Configuration

| Parameter                         | Description                                   | Default                |
|----------------------------------|-----------------------------------------------|------------------------|
| `database.enabled`               | Enable database StatefulSet                   | `true`                 |
| `database.image.repository`      | Database image repository                     | `postgres`             |
| `database.image.tag`             | Database image tag                            | `13`                   |
| `database.service.port`          | Port for database service                     | `5432`                 |
| `database.persistence.enabled`   | Enable database persistence                   | `true`                 |
| `database.persistence.size`      | Size of database persistent volume            | `1Gi`                  |

### Global Configuration

| Parameter                | Description                                  | Default        |
|-------------------------|----------------------------------------------|----------------|
| `config.openaiApiKey`   | OpenAI API key (leave empty to auto-generate)| `""`           |
| `config.backendUrl`     | Backend service URL                          | `http://todo-backend-service:8000` |
| `config.frontendUrl`    | Frontend service URL                         | `http://todo-frontend-service`     |

## Example Custom Values

```yaml
frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

backend:
  replicaCount: 2
  resources:
    requests:
      cpu: 150m
      memory: 256Mi
    limits:
      cpu: 300m
      memory: 512Mi

database:
  persistence:
    size: 2Gi