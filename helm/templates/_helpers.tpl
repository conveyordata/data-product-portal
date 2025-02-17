{{/*
Expand the name of the chart.
*/}}
{{- define "data-product-portal.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Expand the name of the chart.
*/}}
{{- define "data-product-portal.frontendname" -}}
{{- $name := printf "%s-%s" .Chart.Name "frontend" }}
{{- default $name .Values.frontendnameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "data-product-portal.agenticname" -}}
{{- $name := printf "%s-%s" .Chart.Name "agentic-system" }}
{{- default $name .Values.agenticnameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "data-product-portal.fullname" -}}
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
{{- define "data-product-portal.frontendfullname" -}}
{{- if .Values.frontendfullnameOverride }}
{{- .Values.frontendfullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $fname := "frontend" }}
{{- $name := default $fname .Values.frontendnameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "data-product-portal.agenticfullname" -}}
{{- if .Values.agenticfullnameOverride }}
{{- .Values.agenticfullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $fname := "agentic-system" }}
{{- $name := default $fname .Values.agenticnameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "data-product-portal.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "data-product-portal.labels" -}}
helm.sh/chart: {{ include "data-product-portal.chart" . }}
{{ include "data-product-portal.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "data-product-portal.frontendlabels" -}}
helm.sh/chart: {{ include "data-product-portal.chart" . }}
{{ include "data-product-portal.frontendselectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "data-product-portal.agenticlabels" -}}
helm.sh/chart: {{ include "data-product-portal.chart" . }}
{{ include "data-product-portal.agenticselectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
{{/*
Selector labels
*/}}
{{- define "data-product-portal.selectorLabels" -}}
app.kubernetes.io/name: {{ include "data-product-portal.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "data-product-portal.frontendselectorLabels" -}}
app.kubernetes.io/name: {{ include "data-product-portal.frontendname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "data-product-portal.agenticselectorLabels" -}}
app.kubernetes.io/name: {{ include "data-product-portal.agenticname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
{{/*
Create the name of the service account to use
*/}}
{{- define "data-product-portal.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "data-product-portal.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
