from prometheus_client import Counter

CALLS_TOTAL = Counter(
    "kleva_calls_total",
    "Llamadas emuladas por resultado, estilo de negociación y país",
    ["outcome", "style", "country"],
)
