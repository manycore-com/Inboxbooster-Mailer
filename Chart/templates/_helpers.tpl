{{/*
Expand the name of the chart.
*/}}
{{- define "inboxbooster-mailer.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.fullname" -}}
  {{- if .Values.fullnameOverride }}
    {{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
  {{- else }}
    {{- $name := default .Chart.Name .Values.nameOverride }}
    {{- if contains $name .Release.Name }}
      {{- .Release.Name | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
    {{- end }}
  {{- end }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.backdata.fullname" -}}
{{- printf "%s-backdata" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.http-receiver.fullname" -}}
{{- printf "%s-http-receiver" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.mx-server.fullname" -}}
{{- printf "%s-mx-server" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.postfix.fullname" -}}
{{- printf "%s-postfix" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.receiver.fullname" -}}
{{- printf "%s-receiver" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.redis.fullname" -}}
{{- printf "%s-redis" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "inboxbooster-mailer.transformer.fullname" -}}
{{- printf "%s-transformer" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "inboxbooster-mailer.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "inboxbooster-mailer.labels" -}}
helm.sh/chart: {{ include "inboxbooster-mailer.chart" . }}
{{ include "inboxbooster-mailer.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "inboxbooster-mailer.selectorLabels" -}}
app.kubernetes.io/name: {{ include "inboxbooster-mailer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.backdata.serviceAccountName" -}}
  {{- if .Values.backdata.serviceAccount.create }}
    {{- if (empty .Values.backdata.serviceAccount.name) }}
      {{- printf "%s-backdata" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.backdata.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.backdata.serviceAccount.name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.http-receiver.serviceAccountName" -}}
  {{- if .Values.httpReceiver.serviceAccount.create }}
    {{- if (empty .Values.httpReceiver.serviceAccount.name) }}
      {{- printf "%s-http-receiver" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.httpReceiver.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.httpReceiver.serviceAccount.name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.mx-server.serviceAccountName" -}}
  {{- if .Values.mxServer.serviceAccount.create }}
    {{- if (empty .Values.mxServer.serviceAccount.name) }}
      {{- printf "%s-mx-server" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.mxServer.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.mxServer.serviceAccount.name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.postfix.serviceAccountName" -}}
  {{- if .Values.postfix.serviceAccount.create }}
    {{- if (empty .Values.postfix.serviceAccount.name) }}
      {{- printf "%s-postfix" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.postfix.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.postfix.serviceAccount.name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.receiver.serviceAccountName" -}}
  {{- if .Values.receiver.serviceAccount.create }}
    {{- if (empty .Values.receiver.serviceAccount.name) }}
      {{- printf "%s-receiver" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.receiver.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.receiver.serviceAccount.name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.redis.serviceAccountName" -}}
  {{- if .Values.redis.serviceAccount.create }}
    {{- if (empty .Values.redis.serviceAccount.name) }}
      {{- printf "%s-redis" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.redis.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.redis.serviceAccount.name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "inboxbooster-mailer.transformer.serviceAccountName" -}}
  {{- if .Values.transformer.serviceAccount.create }}
    {{- if (empty .Values.transformer.serviceAccount.name) }}
      {{- printf "%s-transformer" (include "inboxbooster-mailer.fullname" .) | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- .Values.transformer.serviceAccount.name }}
    {{- end }}
  {{- else }}
    {{- default "default" .Values.transformer.serviceAccount.name }}
  {{- end }}
{{- end }}
