# Kleva · Agentes de cobranza (demo)

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/XZTndtAwv9XQN3WLyPAvnc/D3ybhcijZg5kwmstvXqcNX/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/XZTndtAwv9XQN3WLyPAvnc/D3ybhcijZg5kwmstvXqcNX/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/leoneljfernandes/kleva_demo/badge.svg?branch=main)](https://coveralls.io/github/leoneljfernandes/kleva_demo?branch=main)

Challenge técnico. Usuarios Kleva administran **agentes de cobranza**. Un agente activo busca deudores elegibles según su configuración (país, producto y días mínimos de atraso) y los "llama". No hay IA ni MCP: la llamada es una **emulación aleatoria con semilla inyectable**, detrás de un puerto (`CallEngine`) que mañana puede implementar un LLM sin tocar el resto.

Cada llamada termina en **no atendió**, **promesa de pago en N días** o **no abonará**, y queda guardada con su transcript.

## Levantar todo

```bash
cp .env.example .env            # completar DB_PASSWORD y SECRET_KEY
docker compose up -d --build    # db → migrate → backend → frontend + observabilidad
docker compose exec backend python -m app.seed
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:8080 |
| API (Swagger) | http://localhost:8010/docs |
| Grafana (dashboard "Kleva - Agentes de cobranza") | http://localhost:3010 (admin / admin) |
| Prometheus | http://localhost:9091 |
| Postgres | localhost:5433 |

Los puertos del host y los nombres de contenedor (`kleva_*`) evitan los valores por defecto (5432, 8000, 3000, 9090) para convivir con otros stacks locales. Todos se cambian en `.env`.

**Usuario del seed:** `admin@kleva.demo` / `Kleva2026`. El seed carga 520 deudores (8 por cada combinación país × producto, más 8 al azar) y 3 agentes pausados: Valeria (AR, tarjeta, suave), Mateo (MX, internet, flexible) y Emily (US, electricidad, rígido; transcript en inglés).

### Desarrollo sin Docker

```bash
docker compose up -d db
uv sync && uv run alembic upgrade head && uv run python -m app.seed
uv run uvicorn app.main:app --reload --port 8010      # un solo proceso: un solo dispatcher
cd frontend && npm install && npm run dev              # http://localhost:5173, proxy de /api al 8010
```

## Cómo funciona la emulación

1. **¿Atiende?** `ANSWER_RATE` (0.65). No depende del estilo: el estilo no hace que alguien levante el teléfono.
2. **Si atiende, ¿qué decide?** Depende del perfil del estilo. A los deudores con más de 90 días de atraso se les restan 0.15 puntos de probabilidad de promesa.

| Estilo | Oferta | P(promesa) | N días | Monto prometido |
|---|---|---|---|---|
| Suave | plan en cuotas | 0.70 | 15–30 | 100 % del saldo |
| Flexible | quita por pago | 0.55 | 7–15 | saldo − 10 a 30 % |
| Rígido | pago total inmediato | 0.40 | 1–5 | 100 % del saldo |

**Elegibilidad.** Un deudor es elegible si coinciden el país y el producto, si tiene `days_overdue >= min_days_overdue` y si `next_contact_at` es nulo o ya pasó. Se llama primero a la deuda más vieja y, a igual atraso, a la más grande.

**Después de cada llamada**, el deudor vuelve a la cola según el resultado:

| Resultado | Vuelve a la cola |
|---|---|
| No atendió | en 30 minutos |
| No abonará | en 7 días |
| Promesa | un día después de la fecha prometida, por si no pagó |

La emulación **nunca** toca el saldo.

**Dispatcher.** Un único loop asyncio en el `lifespan` hace un tick cada `DISPATCH_INTERVAL_SECONDS` y coloca una llamada por agente activo. Las llamadas se hacen en secuencia y con un commit por llamada, así que dos agentes no pueden llamar al mismo deudor. Pausar un agente es cambiar una columna, y el loop lo ve en el tick siguiente. El botón **"Llamar ahora"** usa la misma función (`place_call`).

## Decisiones y por qué

| Decisión | Por qué |
|---|---|
| Capas `api → services → crud → models` | routers finos y testeables vía HTTP; el SQL vive solo en `crud/` |
| `CallEngine` recibe snapshots inmutables, no modelos ORM | no puede tocar la DB, se testea sin sesión, y un engine LLM recibe exactamente lo mismo |
| `random.Random` y el reloj **inyectados** (`get_call_engine`, `get_clock`) | tests deterministas; con `SIMULATION_SEED` la demo es reproducible |
| Estado del agente en la DB, un solo dispatcher | sobrevive reinicios y no hay carreras. Por eso uvicorn corre **sin `--workers`**: N workers serían N dispatchers |
| `next_contact_at` resume reintento, cooldown y promesa | una sola columna mantiene simple la query de elegibilidad |
| `country` agregado al deudor (el enunciado no lo trae) | sin él, el país del agente no filtraría nada |
| Enums como `VARCHAR` (`native_enum=False`) | agregar un valor no exige `ALTER TYPE` y funciona igual en el SQLite de los tests |
| `UTCDateTime` (TypeDecorator) | Postgres devuelve fechas con zona y SQLite no: así la app siempre ve UTC aware |
| Soft delete de agentes, 409 si está activo | preserva el historial de llamadas |
| Sin registro público de usuarios | el ABM del enunciado es de agentes; los usuarios Kleva vienen del seed |
| Dinero en `Numeric` / `Decimal`, string en JSON | nunca `float` para montos |
| Auth: OAuth2 password + JWT HS256, Argon2id, mensaje y tiempo constantes en login | estándar de FastAPI/Swagger; no revela qué emails existen |
| Frontend con los tipos generados desde OpenAPI y los labels desde `/catalogs` | el backend es la única fuente de contratos y enums |
| Estilo visual de kleva.co con tokens propios (`tokens.css`), sin copiar assets | el logo es texto, la esfera es CSS y las fuentes (Archivo, JetBrains Mono, OFL) se sirven desde el bundle |
| SQLAlchemy fijado en `<2.1` | `opentelemetry-instrumentation-sqlalchemy` todavía no instrumenta 2.1 |
| TypeScript fijado en 5.x | `openapi-typescript` usa la API de compilador de TS 5 |

## API

Todas las rutas van bajo `/api` y requieren token, salvo `/auth/login`. La referencia completa está en `/docs`.

| Método | Ruta | Respuesta |
|---|---|---|
| POST | `/auth/login` | JWT (form OAuth2: `username` = email) |
| GET | `/auth/me` | usuario actual |
| GET | `/catalogs` | enums con labels, la categoría de cada producto y la moneda de cada país |
| GET · POST | `/agents` | lista / alta (201, se crea pausado) |
| GET · PATCH · DELETE | `/agents/{id}` | PATCH y DELETE devuelven 409 si el agente está activo; DELETE es soft delete (204) |
| POST | `/agents/{id}/start` · `/pause` | idempotentes |
| POST | `/agents/{id}/calls` | llamada manual: 201, o 204 si no hay deudores elegibles |
| GET | `/agents/{id}/calls` · `/stats` | historial (más reciente primero) y contadores |
| GET | `/debtors` · `/debtors/{id}` · `/debtors/{id}/calls` | solo lectura |

## Tests

```bash
uv run pytest -v                                  # 52 tests, SQLite en memoria, sin Postgres
uv run coverage run --source=app -m pytest && uv run coverage report -m
cd frontend && npm test                           # formulario de agente (Vitest + Testing Library)
```

- **E2E vía HTTP** para todo lo que pasa por la API. Un `FixedOutcomeEngine` y un `FrozenClock` prueban las reglas de persistencia y reintento sin esperar.
- **Unitarios del engine** (lógica pura): misma semilla da el mismo resultado; la tasa de promesa cumple `rígido < flexible < suave`; montos y plazos quedan dentro del perfil; el transcript sale en inglés para USA.
- **Dispatcher**: se llama a `tick()` directamente, sin `sleep` ni tarea en background.

## Observabilidad

- **Prometheus**: métricas HTTP más `kleva_calls_total{outcome,style,country}`.
- **Loki + Alloy**: logs de los contenedores del proyecto `kleva`.
- **Tempo + OpenTelemetry**: trazas de FastAPI y SQLAlchemy, más un span `dispatcher.place_call` por cada llamada del loop.
- Los logs llevan `trace_id`: desde Grafana se salta de un log a su traza y de una traza a sus logs.
- El dashboard se genera con `python3 monitoring/build_dashboard.py`. Para cambiarlo se edita el script, no la UI.

## CI

CircleCI corre tres jobs:
- `test-python`: lint, tests, cobertura a Coveralls y resultados JUnit.
- `migrations`: `upgrade → check → downgrade → upgrade` y seed, contra Postgres 16 real.
- `test-frontend`: typecheck, build y Vitest.

Para Coveralls, cargá `COVERALLS_REPO_TOKEN` en las variables de entorno del proyecto de CircleCI y reemplazá `<org>/<project>/<usuario>/<repo>` en los badges.

## Estructura

```text
app/
├── api/              routers (solo HTTP) + deps (engine, reloj)
├── services/         agents (ABM + estados), calls (place_call), dispatcher, catalogs
│   └── call_engine/  base (puerto + snapshots), simulated (decisión), scripts (texto es/en)
├── crud/             queries SQLAlchemy
├── models/           ORM + tipos (UTCDateTime, str_enum)
├── schemas/          DTOs Pydantic
├── domain/enums.py   enums, categoría de producto, moneda, labels
├── config.py         Settings: única fuente de configuración
└── seed.py           datos de demo reproducibles e idempotentes
frontend/src/
├── api/              cliente fetch, hooks de TanStack Query, tipos generados
├── styles/           tokens.css (estilo kleva.co) + base.css
├── components/       Button, AgentCard, AgentStage/Orb, TranscriptView, AgentForm…
├── layout/ pages/    nav, encabezado de página, login, agentes, formulario, detalle
monitoring/           Prometheus, Loki, Tempo, Alloy, Grafana provisionado
```

## Reemplazo por IA

Para pasar a IA hay que implementar un `LLMCallEngine` con la misma firma: `async run(agent: AgentSnapshot, debtor: DebtorSnapshot) -> CallResult`. Recibe los mismos datos, usa el estilo de negociación como instrucción, devuelve el resultado con `engine="llm"` y se elige en el `lifespan`. No cambian `place_call`, el dispatcher, la API ni el frontend.
