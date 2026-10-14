"""Genera monitoring/grafana/dashboards/kleva-api.json (dashboard provisionado en Grafana).

Uso: `python3 monitoring/build_dashboard.py`. Versionar el JSON generado.
Para cambiar el dashboard se edita este script, no la UI.
"""

import json
from pathlib import Path

SERVICE = "kleva-api"  # = OTEL_SERVICE_NAME del backend
CONTAINER = "kleva_backend"  # = container_name del backend en docker-compose
TITLE = "Kleva - Agentes de cobranza"

PROM = {"type": "prometheus", "uid": "prometheus"}
LOKI = {"type": "loki", "uid": "loki"}
TEMPO = {"type": "tempo", "uid": "tempo"}
SEL = 'handler!="/metrics"'
panels: list[dict] = []
pid = 0
y = 0  # cursor vertical: cada sección se apila debajo de la anterior


def add(kind, title, x, w, h, targets, ds=PROM, unit=None, options=None, extra=None):
    global pid
    pid += 1
    panel = {
        "id": pid, "type": kind, "title": title, "datasource": ds,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [dict(t, datasource=ds, refId=chr(65 + i)) for i, t in enumerate(targets)],
        "fieldConfig": {"defaults": {"unit": unit} if unit else {}, "overrides": []},
        "options": options or {},
    }
    if extra:
        panel.update(extra)
    panels.append(panel)


def row(title):
    global pid, y
    pid += 1
    panels.append({"id": pid, "type": "row", "title": title, "collapsed": False,
                   "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []})
    y += 1


def advance(h):
    global y
    y += h


def q(expr, legend=""):
    return {"expr": expr, "legendFormat": legend}


stat = {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value"}
ts = {"legend": {"displayMode": "table", "placement": "bottom", "calcs": ["mean", "max"]}}
CALLS = "kleva_calls_total"

# --- Dominio: llamadas emuladas ---
row("Llamadas emuladas")
add("stat", "Llamadas totales", 0, 6, 4, [q(f"sum({CALLS})")], unit="short", options=stat)
add("stat", "Promesas de pago", 6, 6, 4, [q(f'sum({CALLS}{{outcome="payment_promise"}})')], unit="short", options=stat)
add("stat", "Tasa de promesa (%)", 12, 6, 4,
    [q(f'100 * sum({CALLS}{{outcome="payment_promise"}}) / sum({CALLS})')], unit="percent", options=stat)
add("stat", "Llamadas/min", 18, 6, 4, [q(f"sum(rate({CALLS}[5m])) * 60")], unit="short", options=stat)
advance(4)
add("timeseries", "Llamadas/min por resultado", 0, 12, 8,
    [q(f"sum by (outcome) (rate({CALLS}[1m])) * 60", "{{outcome}}")], unit="short", options=ts)
add("barchart", "Resultado por estilo de negociación", 12, 12, 8,
    [{**q(f"sum by (style, outcome) ({CALLS})", "{{style}} · {{outcome}}"), "instant": True, "format": "table"}],
    options={"orientation": "horizontal", "showValue": "auto"},
    extra={"transformations": [{"id": "groupingToMatrix", "options": {
        "columnField": "outcome", "rowField": "style", "valueField": "Value"}}]})
advance(8)
add("bargauge", "Llamadas por país", 0, 24, 6,
    [{**q(f"sum by (country) ({CALLS})", "{{country}}"), "instant": True}],
    unit="short", options={"orientation": "vertical", "displayMode": "gradient"})
advance(6)

# --- Resumen HTTP ---
row("API")
add("stat", "Requests/s", 0, 6, 4, [q(f"sum(rate(http_requests_total{{{SEL}}}[1m]))")], unit="reqps", options=stat)
add("stat", "Errores 5xx (%)", 6, 6, 4,
    [q(f'100 * sum(rate(http_requests_total{{{SEL},status="5xx"}}[5m])) / sum(rate(http_requests_total{{{SEL}}}[5m]))')],
    unit="percent", options=stat,
    extra={"fieldConfig": {"defaults": {"unit": "percent", "thresholds": {"mode": "absolute", "steps": [
        {"color": "green", "value": None}, {"color": "orange", "value": 1}, {"color": "red", "value": 5}]},
        "color": {"mode": "thresholds"}}, "overrides": []}})
add("stat", "Latencia p95", 12, 6, 4,
    [q(f"histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{{{SEL}}}[5m])))")],
    unit="s", options=stat)
add("stat", "Requests totales", 18, 6, 4, [q(f"sum(http_requests_total{{{SEL}}})")], unit="short", options=stat)
advance(4)

# --- Tráfico ---
row("Tráfico y errores")
add("timeseries", "Requests/s por endpoint", 0, 12, 8,
    [q(f"sum by (method, handler) (rate(http_requests_total{{{SEL}}}[1m]))", "{{method}} {{handler}}")],
    unit="reqps", options=ts)
add("timeseries", "Requests/s por código de estado", 12, 12, 8,
    [q(f"sum by (status) (rate(http_requests_total{{{SEL}}}[1m]))", "{{status}}")], unit="reqps", options=ts)
advance(8)

# --- Latencia ---
row("Latencia")
hist = "http_request_duration_seconds_bucket"
add("timeseries", "Latencia p50 / p95 / p99", 0, 12, 8, [
    q(f"histogram_quantile(0.50, sum by (le) (rate({hist}{{{SEL}}}[5m])))", "p50"),
    q(f"histogram_quantile(0.95, sum by (le) (rate({hist}{{{SEL}}}[5m])))", "p95"),
    q(f"histogram_quantile(0.99, sum by (le) (rate({hist}{{{SEL}}}[5m])))", "p99")], unit="s", options=ts)
add("timeseries", "Latencia p95 por endpoint", 12, 12, 8,
    [q(f"histogram_quantile(0.95, sum by (le, handler) (rate({hist}{{{SEL}}}[5m])))", "{{handler}}")],
    unit="s", options=ts)
advance(8)

# --- Recursos ---
row("Recursos del proceso")
add("timeseries", "CPU (cores)", 0, 8, 7, [q("rate(process_cpu_seconds_total[1m])", "cpu")], unit="short")
add("timeseries", "Memoria residente", 8, 8, 7, [q("process_resident_memory_bytes", "rss")], unit="bytes")
add("timeseries", "Archivos abiertos", 16, 8, 7, [q("process_open_fds", "fds")], unit="short")
advance(7)

# --- Logs ---
row("Logs (Loki)")
add("timeseries", "Volumen de logs por nivel", 0, 24, 5,
    [{"expr": 'sum by (level) (count_over_time({container="%s"} | regexp `(?P<level>INFO|WARNING|ERROR|CRITICAL)` [1m]))'
      % CONTAINER, "legendFormat": "{{level}}"}], ds=LOKI, unit="short", options=ts)
advance(5)
add("logs", "Llamadas del dispatcher", 0, 24, 8,
    [{"expr": '{container="%s"} |= "call placed"' % CONTAINER}], ds=LOKI,
    options={"showTime": True, "wrapLogMessage": True, "enableLogDetails": True, "sortOrder": "Descending"})
advance(8)
add("logs", "Logs del backend", 0, 24, 10,
    [{"expr": '{container="%s"} |~ "(?i)$search"' % CONTAINER}], ds=LOKI,
    options={"showTime": True, "wrapLogMessage": True, "enableLogDetails": True, "sortOrder": "Descending"})
advance(10)
add("logs", "Solo errores (backend)", 0, 24, 8,
    [{"expr": '{container="%s"} |~ "ERROR|CRITICAL|Traceback"' % CONTAINER}], ds=LOKI,
    options={"showTime": True, "wrapLogMessage": True, "enableLogDetails": True})
advance(8)

# --- Trazas ---
row("Trazas (Tempo)")
add("table", "Trazas recientes", 0, 24, 10,
    [{"queryType": "traceqlSearch", "limit": 20, "tableType": "traces",
      "filters": [{"id": "service-name", "tag": "service.name", "operator": "=", "scope": "resource",
                   "value": [SERVICE], "valueType": "string"}]}], ds=TEMPO)
advance(10)
add("table", "Trazas lentas (> 500ms)", 0, 24, 8,
    [{"queryType": "traceql", "query": '{ resource.service.name = "%s" && duration > 500ms }' % SERVICE,
      "limit": 20, "tableType": "traces"}], ds=TEMPO)
advance(8)

dashboard = {
    "uid": SERVICE, "title": TITLE,
    "tags": ["fastapi", "observability", "kleva"], "timezone": "browser", "schemaVersion": 39,
    "version": 1, "refresh": "10s", "time": {"from": "now-30m", "to": "now"},
    "templating": {"list": [{"name": "search", "label": "Buscar en logs", "type": "textbox",
                             "query": "", "current": {"value": "", "text": ""}}]},
    "panels": panels,
}
out = Path(__file__).parent / "grafana" / "dashboards" / f"{SERVICE}.json"
out.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False))
print(out)
