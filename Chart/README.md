# Manycore-Mailer Helm Chart

## Prerequisites

- Kubernetes 1.24+
- Helm 3.2.0+

## Installing the Chart

[//]: # (TODO: setup chart repository: https://helm.sh/docs/topics/chart_repository/#github-pages-example)

[//]: # (```console)

[//]: # (helm repo add manycore-com https://manycore-com.github.com/Inboxbooster-Mailer)

[//]: # (helm install my-manycore-mailer manycore-com/inboxbooster-mailer)

[//]: # (```)


Before installing this chart, you must provide:
- a secret containing your TLS certificate and your TLS key for your receiver.
- other secrets containing your DKIM certificates if necessary (depending on your configuration).
- a configMap containing your custom [inboxbooster-mailer-customer.yaml settings file](../README.md#inboxbooster-mailer-customeryaml)

To install this chart with the release name `my-manycore-mailer`:
```shell
# Create the TLS secret.
kubectl create secret generic inboxbooster-receiver-secret \
  --from-file=receiver_key.pem \
  --from-file=receiver_cert.pem

# Create a DKIM secret
kubectl create secret generic dkim-secret \
  --from-file=dkim-private-key.pem

# Create the configMap with your custom configuration
kubectl create configmap inboxbooster-config \
  --from-file inboxbooster-mailer-customer.yaml

# Install the Helm release
helm install my-manycore-mailer ./Chart \
  --set receiver.tlsCert.existingSecret.name="inboxbooster-receiver-secret" \
  --set receiver.tlsCert.existingSecret.key="receiver_cert.pem" \
  --set receiver.tlsKey.existingSecret.name="inboxbooster-receiver-secret" \
  --set receiver.tlsKey.existingSecret.key="receiver_key.pem" \
  --set 'transformer.dkimCertificates.existingSecrets[0].name="dkim-secret"' \
  --set 'transformer.dkimCertificates.existingSecrets[0].key="dkim-private-key.pem"' \
  --set config.existingConfigMap="inboxbooster-config"
```


## Helm Parameters

You can specify each following parameter using `--set key=value[,key=value]` parameters with the `helm install` command.

Otherwise, you can use a YAML file which specify all the values parameters you want using the `-f my-file.yaml` parameter with the `helm install` command.


### Global parameters

| Name                                 | Description                                                                                                                                | Default value |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `config.existingConfigMap`           | Name of an existing configMap containing you `inboxbooster-mailer-customer.yaml` file. (Must be in the same namespace as your deployment). | `""`          |
| `prometheus.serviceMonitor.enabled`  | Enable the creation of ServiceMonitor to setup Prometheus.                                                                                 | `false`       |
| `prometheus.prometheusRule.enabled`  | Enable the creation of PrometheusRule to setup Prometheus alerts.                                                                          | `false`       |
| `prometheus.prometheusRule.receiver` | AlertManager receiver used when the Manycore-Mailer alerts are active.  Only used if `prometheus.prometheusRule.enabled` is `true`.        | `""`          |

### Backdata parameters

| Name                                          | Description                                                                               | Default value           |
|-----------------------------------------------|-------------------------------------------------------------------------------------------|-------------------------|
| `backdata.replicaCount`                       | Number of Backdata replicas to deploy.                                                    | `1`                     |
| `backdata.image.repository`                   | Backdata image repository.                                                                | `inboxbooster/backdata` |
| `backdata.image.tag`                          | Backdata image tag.                                                                       | `latest`                |
| `backdata.image.pullPolicy`                   | Backdata image pull policy.                                                               | `IfNotPresent`          |
| `backdata.updateStrategy`                     | Update strategy configuration for Backdata Deployment.                                    | `type: RollingUpdate`   |
| `backdata.serviceAccount.create`              | Enable creation of ServiceAccount for Backdata pods.                                      | `true`                  |
| `backdata.serviceAccount.name`                | Name of the created serviceAccount.                                                       | `""`                    |
| `backdata.serviceAccount.annotations`         | Annotations for service account. Only used if `backdata.serviceAccount.create` is `true`. | `{}`                    |
| `backdata.service.httpPort`                   | Backdata HTTP service port.                                                               | `9090`                  |
| `backdata.resources`                          | Resources requests/limits for Backdata containers.                                        | `{}`                    |
| `backdata.livenessProbe.enabled`              | Enable Backdata livenessProbe.                                                            | `true`                  |
| `backdata.livenessProbe.path`                 | Path for Backdata livenessProbe.                                                          | `/`                     |
| `backdata.livenessProbe.initialDelaySeconds`  | Initial delay seconds for Backdata livenessProbe.                                         | `120`                   |
| `backdata.livenessProbe.periodSeconds`        | Period seconds for Backdata livenessProbe.                                                | `30`                    |
| `backdata.livenessProbe.timeoutSeconds`       | Timeout seconds for Backdata livenessProbe.                                               | `20`                    |
| `backdata.livenessProbe.failureThreshold`     | Failure threshold for Backdata livenessProbe.                                             | `6`                     |
| `backdata.livenessProbe.successThreshold`     | Success threshold for Backdata livenessProbe.                                             | `1`                     |
| `backdata.readinessProbe.enabled`             | Enable Backdata readinessProbe.                                                           | `true`                  |
| `backdata.livenessProbe.path`                 | Path for Backdata readinessProbe.                                                         | `/`                     |
| `backdata.readinessProbe.initialDelaySeconds` | Initial delay seconds for Backdata readinessProbe.                                        | `10`                    |
| `backdata.readinessProbe.periodSeconds`       | Period seconds for Backdata readinessProbe.                                               | `30`                    |
| `backdata.readinessProbe.timeoutSeconds`      | Timeout seconds for Backdata readinessProbe.                                              | `20`                    |
| `backdata.readinessProbe.failureThreshold`    | Failure threshold for Backdata readinessProbe.                                            | `3`                     |
| `backdata.readinessProbe.successThreshold`    | Success threshold for Backdata readinessProbe.                                            | `1`                     |
| `backdata.podAnnotations`                     | Backdata Pod annotations.                                                                 | `{}`                    |
| `backdata.affinity`                           | Affinity for Backdata pods.                                                               | `{}`                    |
| `backdata.nodeSelector`                       | Node labels for Backdata pods.                                                            | `{}`                    |
| `backdata.tolerations`                        | Tolerations for Backdata pods.                                                            | `[]`                    |
| `backdata.podSecurityContext`                 | Backdata pods security context configuration.                                             | `enabled: false`        |
| `backdata.securityContext`                    | Backdata containers security context configuration.                                       | `enabled: false`        |

### Http Receiver parameters

| Name                                              | Description                                                                                                   | Default value               |
|---------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------|
| `httpReceiver.replicaCount`                       | Number of HttpReceiver replicas to deploy.                                                                    | `1`                         |
| `httpReceiver.image.repository`                   | HttpReceiver image repository.                                                                                | `inboxbooster/httpreceiver` |
| `httpReceiver.image.tag`                          | HttpReceiver image tag.                                                                                       | `latest`                    |
| `httpReceiver.image.pullPolicy`                   | HttpReceiver image pull policy.                                                                               | `IfNotPresent`              |
| `httpReceiver.updateStrategy`                     | Update strategy configuration for HttpReceiver Deployment.                                                    | `type: RollingUpdate`       |
| `httpReceiver.serviceAccount.create`              | Enable creation of ServiceAccount for HttpReceiver pods.                                                      | `true`                      |
| `httpReceiver.serviceAccount.name`                | Name of the created serviceAccount.                                                                           | `""`                        |
| `httpReceiver.serviceAccount.annotations`         | Annotations for service account. Only used if `httpReceiver.serviceAccount.create` is `true`.                 | `{}`                        |
| `httpReceiver.service.httpPort`                   | HttpReceiver HTTP port.                                                                                       | `8080`                      |
| `httpReceiver.service.metricsPort`                | HttpReceiver metrics port.                                                                                    | `9090`                      |
| `httpReceiver.resources`                          | Resources requests/limits for HttpReceiver containers.                                                        | `{}`                        |
| `httpReceiver.livenessProbe.enabled`              | Enable HttpReceiver livenessProbe.                                                                            | `true`                      |
| `httpReceiver.livenessProbe.path`                 | Path for HttpReceiver livenessProbe.                                                                          | `/metrics`                  |
| `httpReceiver.livenessProbe.initialDelaySeconds`  | Initial delay seconds for HttpReceiver livenessProbe.                                                         | `120`                       |
| `httpReceiver.livenessProbe.periodSeconds`        | Period seconds for HttpReceiver livenessProbe.                                                                | `30`                        |
| `httpReceiver.livenessProbe.timeoutSeconds`       | Timeout seconds for HttpReceiver livenessProbe.                                                               | `20`                        |
| `httpReceiver.livenessProbe.failureThreshold`     | Failure threshold for HttpReceiver livenessProbe.                                                             | `6`                         |
| `httpReceiver.livenessProbe.successThreshold`     | Success threshold for HttpReceiver livenessProbe.                                                             | `1`                         |
| `httpReceiver.readinessProbe.enabled`             | Enable HttpReceiver readinessProbe.                                                                           | `true`                      |
| `httpReceiver.readinessProbe.path`                | Path for HttpReceiver readinessProbe.                                                                         | `/metrics`                  |
| `httpReceiver.readinessProbe.initialDelaySeconds` | Initial delay seconds for HttpReceiver readinessProbe.                                                        | `10`                        |
| `httpReceiver.readinessProbe.periodSeconds`       | Period seconds for HttpReceiver readinessProbe.                                                               | `30`                        |
| `httpReceiver.readinessProbe.timeoutSeconds`      | Timeout seconds for HttpReceiver readinessProbe.                                                              | `20`                        |
| `httpReceiver.readinessProbe.failureThreshold`    | Failure threshold for HttpReceiver readinessProbe.                                                            | `3`                         |
| `httpReceiver.readinessProbe.successThreshold`    | Success threshold for HttpReceiver readinessProbe.                                                            | `1`                         |
| `httpReceiver.podAnnotations`                     | HttpReceiver Pod annotations.                                                                                 | `{}`                        |
| `httpReceiver.affinity`                           | Affinity for HttpReceiver pods.                                                                               | `{}`                        |
| `httpReceiver.nodeSelector`                       | Node labels for HttpReceiver pods.                                                                            | `{}`                        |
| `httpReceiver.tolerations`                        | Tolerations for HttpReceiver pods.                                                                            | `[]`                        |
| `httpReceiver.podSecurityContext`                 | HttpReceiver pods security context configuration.                                                             | `enabled: false`            |
| `httpReceiver.securityContext`                    | HttpReceiver containers security context configuration.                                                       | `enabled: false`            |
| `httpReceiver.ingress.enabled`                    | Create an Ingress resource for the HttpReceiver.                                                              | `false`                     |
| `httpReceiver.ingress.className`                  | IngressClass used to implement the HttpReceiver Ingress.                                                      | `""`                        |
| `httpReceiver.ingress.annotations`                | Additional annotations for the HttpReceiver Ingress (useful for cert-manager annotations).                    | `{}`                        |
| `httpReceiver.ingress.hosts`                      | List of Ingress hosts configuration.                                                                          | `[]`                        |
| `httpReceiver.ingress.hosts[].host`               | An Ingress hostname for the HttpReceiver.                                                                     | `""`                        |
| `httpReceiver.ingress.hosts[].paths[].path`       | An Ingress path for the HttpReceiver.                                                                         | `/`                         |
| `httpReceiver.ingress.hosts[].paths[].pathType`   | Ingress path type for the HttpReceiver.                                                                       | `ImplementationSpecific`    |
| `httpReceiver.ingress.tls.enabled`                | Enable Ingress TLS for the HttpReceiver.                                                                      | `true`                      |
| `httpReceiver.ingress.tls.secretName`             | The secret name where the TLS certificate is stored (a name will be generated if empty for cert-manager use). | `""`                        |

### MxServer parameters

| Name                                          | Description                                                                               | Default value           |
|-----------------------------------------------|-------------------------------------------------------------------------------------------|-------------------------|
| `mxServer.replicaCount`                       | Number of MxServer replicas to deploy.                                                    | `1`                     |
| `mxServer.image.repository`                   | MxServer image repository.                                                                | `inboxbooster/mxserver` |
| `mxServer.image.tag`                          | MxServer image tag.                                                                       | `latest`                |
| `mxServer.image.pullPolicy`                   | MxServer image pull policy.                                                               | `IfNotPresent`          |
| `mxServer.updateStrategy`                     | Update strategy configuration for MxServer Deployment.                                    | `type: RollingUpdate`   |
| `mxServer.serviceAccount.create`              | Enable creation of ServiceAccount for MxServer pods.                                      | `true`                  |
| `mxServer.serviceAccount.name`                | Name of the created serviceAccount.                                                       | `""`                    |
| `mxServer.serviceAccount.annotations`         | Annotations for service account. Only used if `mxServer.serviceAccount.create` is `true`. | `{}`                    |
| `mxServer.service.smtpPort`                   | MxServer SMTP service port.                                                               | `25`                    |
| `mxServer.service.httpPort`                   | MxServer HTTP service port.                                                               | `9090`                  |
| `mxServer.resources`                          | Resources requests/limits for MxServer containers.                                        | `{}`                    |
| `mxServer.livenessProbe.enabled`              | Enable MxServer livenessProbe.                                                            | `true`                  |
| `mxServer.livenessProbe.initialDelaySeconds`  | Initial delay seconds for MxServer livenessProbe.                                         | `120`                   |
| `mxServer.livenessProbe.periodSeconds`        | Period seconds for MxServer livenessProbe.                                                | `30`                    |
| `mxServer.livenessProbe.timeoutSeconds`       | Timeout seconds for MxServer livenessProbe.                                               | `20`                    |
| `mxServer.livenessProbe.failureThreshold`     | Failure threshold for MxServer livenessProbe.                                             | `6`                     |
| `mxServer.livenessProbe.successThreshold`     | Success threshold for MxServer livenessProbe.                                             | `1`                     |
| `mxServer.readinessProbe.enabled`             | Enable MxServer readinessProbe.                                                           | `true`                  |
| `mxServer.readinessProbe.initialDelaySeconds` | Initial delay seconds for MxServer readinessProbe.                                        | `10`                    |
| `mxServer.readinessProbe.periodSeconds`       | Period seconds for MxServer readinessProbe.                                               | `30`                    |
| `mxServer.readinessProbe.timeoutSeconds`      | Timeout seconds for MxServer readinessProbe.                                              | `20`                    |
| `mxServer.readinessProbe.failureThreshold`    | Failure threshold for MxServer readinessProbe.                                            | `3`                     |
| `mxServer.readinessProbe.successThreshold`    | Success threshold for MxServer readinessProbe.                                            | `1`                     |
| `mxServer.podAnnotations`                     | MxServer Pod annotations.                                                                 | `{}`                    |
| `mxServer.affinity`                           | Affinity for MxServer pods.                                                               | `{}`                    |
| `mxServer.nodeSelector`                       | Node labels for MxServer pods.                                                            | `{}`                    |
| `mxServer.tolerations`                        | Tolerations for MxServer pods.                                                            | `[]`                    |
| `mxServer.podSecurityContext`                 | MxServer pods security context configuration.                                             | `enabled: false`        |
| `mxServer.securityContext`                    | MxServer containers security context configuration.                                       | `enabled: false`        |

### Postfix parameters

| Name                                         | Description                                                                              | Default value          |
|----------------------------------------------|------------------------------------------------------------------------------------------|------------------------|
| `postfix.replicaCount`                       | Number of Postfix replicas to deploy.                                                    | `1`                    |
| `postfix.image.repository`                   | Postfix image repository.                                                                | `inboxbooster/postfix` |
| `postfix.image.tag`                          | Postfix image tag.                                                                       | `latest`               |
| `postfix.image.pullPolicy`                   | Postfix image pull policy.                                                               | `IfNotPresent`         |
| `postfix.updateStrategy`                     | Update strategy configuration for Postfix Deployment.                                    | `type: RollingUpdate`  |
| `postfix.serviceAccount.create`              | Enable creation of ServiceAccount for Postfix pods.                                      | `true`                 |
| `postfix.serviceAccount.name`                | Name of the created serviceAccount.                                                      | `""`                   |
| `postfix.serviceAccount.annotations`         | Annotations for service account. Only used if `postfix.serviceAccount.create` is `true`. | `{}`                   |
| `postfix.service.httpPort`                   | Postfix HTTP service port.                                                               | `9090`                 |
| `postfix.resources`                          | Resources requests/limits for Postfix containers.                                        | `{}`                   |
| `postfix.livenessProbe.enabled`              | Enable Postfix livenessProbe.                                                            | `true`                 |
| `postfix.livenessProbe.path`                 | Path for Postfix livenessProbe.                                                          | `/`                    |
| `postfix.livenessProbe.initialDelaySeconds`  | Initial delay seconds for Postfix livenessProbe.                                         | `120`                  |
| `postfix.livenessProbe.periodSeconds`        | Period seconds for Postfix livenessProbe.                                                | `30`                   |
| `postfix.livenessProbe.timeoutSeconds`       | Timeout seconds for Postfix livenessProbe.                                               | `20`                   |
| `postfix.livenessProbe.failureThreshold`     | Failure threshold for Postfix livenessProbe.                                             | `6`                    |
| `postfix.livenessProbe.successThreshold`     | Success threshold for Postfix livenessProbe.                                             | `1`                    |
| `postfix.readinessProbe.enabled`             | Enable Postfix readinessProbe.                                                           | `true`                 |
| `postfix.readinessProbe.path`                | Path for Postfix readinessProbe.                                                         | `/`                    |
| `postfix.readinessProbe.initialDelaySeconds` | Initial delay seconds for Postfix readinessProbe.                                        | `10`                   |
| `postfix.readinessProbe.periodSeconds`       | Period seconds for Postfix readinessProbe.                                               | `30`                   |
| `postfix.readinessProbe.timeoutSeconds`      | Timeout seconds for Postfix readinessProbe.                                              | `20`                   |
| `postfix.readinessProbe.failureThreshold`    | Failure threshold for Postfix readinessProbe.                                            | `3`                    |
| `postfix.readinessProbe.successThreshold`    | Success threshold for Postfix readinessProbe.                                            | `1`                    |
| `postfix.podAnnotations`                     | Postfix Pod annotations.                                                                 | `{}`                   |
| `postfix.affinity`                           | Affinity for Postfix pods.                                                               | `{}`                   |
| `postfix.nodeSelector`                       | Node labels for Postfix pods.                                                            | `{}`                   |
| `postfix.tolerations`                        | Tolerations for Postfix pods.                                                            | `[]`                   |
| `postfix.podSecurityContext`                 | Postfix pods security context configuration.                                             | `enabled: false`       |
| `postfix.securityContext`                    | Postfix containers security context configuration.                                       | `enabled: false`       |

### Receiver parameters

| Name                                          | Description                                                                                                     | Default value           |
|-----------------------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------|
| `receiver.replicaCount`                       | Number of Receiver replicas to deploy.                                                                          | `1`                     |
| `receiver.tlsCert.existingSecret.name`        | Name of an existing Secret containing your TLS certificate. (Must be in the same namespace as your deployment). | `""`                    |
| `receiver.tlsCert.existingSecret.key`         | Key of the Secret whose value is your TLS certificate.                                                          | `""`                    |
| `receiver.tlsKey.existingSecret.name`         | Name of an existing Secret containing your TLS key. (Must be in the same namespace as your deployment).         | `""`                    |
| `receiver.tlsKey.existingSecret.key`          | Key of the Secret whose value is your TLS key.                                                                  | `""`                    |
| `receiver.image.repository`                   | Receiver image repository.                                                                                      | `inboxbooster/receiver` |
| `receiver.image.tag`                          | Receiver image tag.                                                                                             | `latest`                |
| `receiver.image.pullPolicy`                   | Receiver image pull policy.                                                                                     | `IfNotPresent`          |
| `receiver.updateStrategy`                     | Update strategy configuration for Receiver Deployment.                                                          | `type: RollingUpdate`   |
| `receiver.serviceAccount.create`              | Enable creation of ServiceAccount for Receiver pods.                                                            | `true`                  |
| `receiver.serviceAccount.name`                | Name of the created serviceAccount.                                                                             | `""`                    |
| `receiver.serviceAccount.annotations`         | Annotations for service account. Only used if `receiver.serviceAccount.create` is `true`.                       | `{}`                    |
| `receiver.service.smtpPort`                   | Receiver SMTP service port.                                                                                     | `587`                   |
| `receiver.service.httpPort`                   | Receiver HTTP service port.                                                                                     | `9090`                  |
| `receiver.resources`                          | Resources requests/limits for Receiver containers.                                                              | `{}`                    |
| `receiver.livenessProbe.enabled`              | Enable Receiver livenessProbe.                                                                                  | `true`                  |
| `receiver.livenessProbe.initialDelaySeconds`  | Initial delay seconds for Receiver livenessProbe.                                                               | `120`                   |
| `receiver.livenessProbe.periodSeconds`        | Period seconds for Receiver livenessProbe.                                                                      | `30`                    |
| `receiver.livenessProbe.timeoutSeconds`       | Timeout seconds for Receiver livenessProbe.                                                                     | `20`                    |
| `receiver.livenessProbe.failureThreshold`     | Failure threshold for Receiver livenessProbe.                                                                   | `6`                     |
| `receiver.livenessProbe.successThreshold`     | Success threshold for Receiver livenessProbe.                                                                   | `1`                     |
| `receiver.readinessProbe.enabled`             | Enable Receiver readinessProbe.                                                                                 | `true`                  |
| `receiver.readinessProbe.initialDelaySeconds` | Initial delay seconds for Receiver readinessProbe.                                                              | `10`                    |
| `receiver.readinessProbe.periodSeconds`       | Period seconds for Receiver readinessProbe.                                                                     | `30`                    |
| `receiver.readinessProbe.timeoutSeconds`      | Timeout seconds for Receiver readinessProbe.                                                                    | `20`                    |
| `receiver.readinessProbe.failureThreshold`    | Failure threshold for Receiver readinessProbe.                                                                  | `3`                     |
| `receiver.readinessProbe.successThreshold`    | Success threshold for Receiver readinessProbe.                                                                  | `1`                     |
| `receiver.podAnnotations`                     | Receiver Pod annotations.                                                                                       | `{}`                    |
| `receiver.affinity`                           | Affinity for Receiver pods.                                                                                     | `{}`                    |
| `receiver.nodeSelector`                       | Node labels for Receiver pods.                                                                                  | `{}`                    |
| `receiver.tolerations`                        | Tolerations for Receiver pods.                                                                                  | `[]`                    |
| `receiver.podSecurityContext`                 | Receiver pods security context configuration.                                                                   | `enabled: false`        |
| `receiver.securityContext`                    | Receiver containers security context configuration.                                                             | `enabled: false`        |

### Redis parameters

| Name                                       | Description                                                                            | Default value         |
|--------------------------------------------|----------------------------------------------------------------------------------------|-----------------------|
| `redis.replicaCount`                       | Number of Redis replicas to deploy.                                                    | `1`                   |
| `redis.image.repository`                   | Redis image repository.                                                                | `inboxbooster/redis`  |
| `redis.image.tag`                          | Redis image tag.                                                                       | `latest`              |
| `redis.image.pullPolicy`                   | Redis image pull policy.                                                               | `IfNotPresent`        |
| `redis.updateStrategy`                     | Update strategy configuration for Redis Deployment.                                    | `type: RollingUpdate` |
| `redis.serviceAccount.create`              | Enable creation of ServiceAccount for Redis pods.                                      | `true`                |
| `redis.serviceAccount.name`                | Name of the created serviceAccount.                                                    | `""`                  |
| `redis.serviceAccount.annotations`         | Annotations for service account. Only used if `redis.serviceAccount.create` is `true`. | `{}`                  |
| `redis.service.redisPort`                  | Redis Redis service port.                                                              | `6379`                |
| `redis.service.metricsPort`                | Redis Metrics HTTP service port.                                                       | `9090`                |
| `redis.resources`                          | Resources requests/limits for Redis containers.                                        | `{}`                  |
| `redis.livenessProbe.enabled`              | Enable Redis livenessProbe.                                                            | `true`                |
| `redis.livenessProbe.initialDelaySeconds`  | Initial delay seconds for Redis livenessProbe.                                         | `120`                 |
| `redis.livenessProbe.periodSeconds`        | Period seconds for Redis livenessProbe.                                                | `30`                  |
| `redis.livenessProbe.timeoutSeconds`       | Timeout seconds for Redis livenessProbe.                                               | `20`                  |
| `redis.livenessProbe.failureThreshold`     | Failure threshold for Redis livenessProbe.                                             | `6`                   |
| `redis.livenessProbe.successThreshold`     | Success threshold for Redis livenessProbe.                                             | `1`                   |
| `redis.readinessProbe.enabled`             | Enable Redis readinessProbe.                                                           | `true`                |
| `redis.readinessProbe.initialDelaySeconds` | Initial delay seconds for Redis readinessProbe.                                        | `10`                  |
| `redis.readinessProbe.periodSeconds`       | Period seconds for Redis readinessProbe.                                               | `30`                  |
| `redis.readinessProbe.timeoutSeconds`      | Timeout seconds for Redis readinessProbe.                                              | `20`                  |
| `redis.readinessProbe.failureThreshold`    | Failure threshold for Redis readinessProbe.                                            | `3`                   |
| `redis.readinessProbe.successThreshold`    | Success threshold for Redis readinessProbe.                                            | `1`                   |
| `redis.podAnnotations`                     | Redis Pod annotations.                                                                 | `{}`                  |
| `redis.affinity`                           | Affinity for Redis pods.                                                               | `{}`                  |
| `redis.nodeSelector`                       | Node labels for Redis pods.                                                            | `{}`                  |
| `redis.tolerations`                        | Tolerations for Redis pods.                                                            | `[]`                  |
| `redis.podSecurityContext`                 | Redis pods security context configuration.                                             | `enabled: false`      |
| `redis.securityContext`                    | Redis containers security context configuration.                                       | `enabled: false`      |

### Transformer parameters

| Name                                                  | Description                                                                                                                    | Default value              |
|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `transformer.replicaCount`                            | Number of Transformer replicas to deploy.                                                                                      | `1`                        |
| `transformer.dkimCertificates.existingSecrets`        | List of existing Secrets containing your DKIM certificates. (Must be in the same namespace as your deployment).                | `[]`                       |
| `transformer.dkimCertificates.existingSecrets[].name` | Name of an existing Secret containing your DKIM certificate. It will be mounted in the `/configs/dkim/` directory in the pods. | `""`                       |
| `transformer.dkimCertificates.existingSecrets[].key`  | Key of the Secret whose value is a DKIM certificate.                                                                           | `""`                       |
| `transformer.image.repository`                        | Transformer image repository.                                                                                                  | `inboxbooster/transformer` |
| `transformer.image.tag`                               | Transformer image tag.                                                                                                         | `latest`                   |
| `transformer.image.pullPolicy`                        | Transformer image pull policy.                                                                                                 | `IfNotPresent`             |
| `transformer.updateStrategy`                          | Update strategy configuration for Transformer Deployment.                                                                      | `type: RollingUpdate`      |
| `transformer.serviceAccount.create`                   | Enable creation of ServiceAccount for Transformer pods.                                                                        | `true`                     |
| `transformer.serviceAccount.name`                     | Name of the created serviceAccount.                                                                                            | `""`                       |
| `transformer.serviceAccount.annotations`              | Annotations for service account. Only used if `transformer.serviceAccount.create` is `true`.                                   | `{}`                       |
| `transformer.service.httpPort`                        | Transformer HTTP service port.                                                                                                 | `9090`                     |
| `transformer.resources`                               | Resources requests/limits for Transformer containers.                                                                          | `{}`                       |
| `transformer.livenessProbe.enabled`                   | Enable Transformer livenessProbe.                                                                                              | `true`                     |
| `transformer.livenessProbe.path`                      | Path for Transformer livenessProbe.                                                                                            | `/`                        |
| `transformer.livenessProbe.initialDelaySeconds`       | Initial delay seconds for Transformer livenessProbe.                                                                           | `120`                      |
| `transformer.livenessProbe.periodSeconds`             | Period seconds for Transformer livenessProbe.                                                                                  | `30`                       |
| `transformer.livenessProbe.timeoutSeconds`            | Timeout seconds for Transformer livenessProbe.                                                                                 | `20`                       |
| `transformer.livenessProbe.failureThreshold`          | Failure threshold for Transformer livenessProbe.                                                                               | `6`                        |
| `transformer.livenessProbe.successThreshold`          | Success threshold for Transformer livenessProbe.                                                                               | `1`                        |
| `transformer.readinessProbe.enabled`                  | Enable Transformer readinessProbe.                                                                                             | `true`                     |
| `transformer.readinessProbe.path`                     | Path for Transformer readinessProbe.                                                                                           | `/`                        |
| `transformer.readinessProbe.initialDelaySeconds`      | Initial delay seconds for Transformer readinessProbe.                                                                          | `10`                       |
| `transformer.readinessProbe.periodSeconds`            | Period seconds for Transformer readinessProbe.                                                                                 | `30`                       |
| `transformer.readinessProbe.timeoutSeconds`           | Timeout seconds for Transformer readinessProbe.                                                                                | `20`                       |
| `transformer.readinessProbe.failureThreshold`         | Failure threshold for Transformer readinessProbe.                                                                              | `3`                        |
| `transformer.readinessProbe.successThreshold`         | Success threshold for Transformer readinessProbe.                                                                              | `1`                        |
| `transformer.podAnnotations`                          | Transformer Pod annotations.                                                                                                   | `{}`                       |
| `transformer.affinity`                                | Affinity for Transformer pods.                                                                                                 | `{}`                       |
| `transformer.nodeSelector`                            | Node labels for Transformer pods.                                                                                              | `{}`                       |
| `transformer.tolerations`                             | Tolerations for Transformer pods.                                                                                              | `[]`                       |
| `transformer.podSecurityContext`                      | Transformer pods security context configuration.                                                                               | `enabled: false`           |
| `transformer.securityContext`                         | Transformer containers security context configuration.                                                                         | `enabled: false`           |

## Uninstalling the Chart

To uninstall/delete the `my-manycore-mailer` release:

```console
helm uninstall my-manycore-mailer
```

This command removes all the Kubernetes resources related to the `my-manycore-mailer` deployment. 
