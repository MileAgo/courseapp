{{- define "benny-app.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{- define "benny-app.selectorLabels" -}}
app: {{ include "benny-app.fullname" . }}
{{- end }}

{{- define "benny-app.labels" -}}
{{ include "benny-app.selectorLabels" . }}
chart: {{ .Chart.Name }}-{{ .Chart.Version }}
release: {{ .Release.Name }}
{{- end }}
