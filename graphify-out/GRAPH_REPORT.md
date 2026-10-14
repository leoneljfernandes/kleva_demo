# Graph Report - kleva_demo  (2026-10-14)

## Corpus Check
- Corpus is ~20,905 words - fits in a single context window. You may not need a graph.

## Summary
- 699 nodes · 1747 edges · 35 communities (24 shown, 11 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.93)
- Token cost: 102,169 input · 0 output

## Community Hubs (Navigation)
- API y servicio de agentes
- Deudores y registro de llamadas
- Cableado de la app
- Engine de llamadas emulado
- Config, métricas y CI
- Fixtures de test y auth
- Alembic y modelos ORM
- Migración inicial y login
- Auth y cliente HTTP (front)
- Catálogos y labels
- Campos de formulario y esfera
- Botones y stat cards
- Config de TypeScript
- Manifiesto del frontend
- Formularios y errores de agente
- Tipos de API y transcript
- Ruteo y layout
- Dependencias de desarrollo
- Hooks de datos de agentes
- Detalle de agente y formato
- Tarjeta de agente y badges
- Tests del formulario
- Dependencias de runtime
- Scripts de npm
- Internals de AgentForm
- Config de Vite
- Metadatos del proyecto
- Dinero como Decimal

## God Nodes (most connected - your core abstractions)
1. `Country` - 37 edges
2. `ProductType` - 36 edges
3. `CallOutcome` - 36 edges
4. `CollectionAgent` - 30 edges
5. `NegotiationStyle` - 24 edges
6. `DebtorSnapshot` - 22 edges
7. `SimulatedCallEngine` - 22 edges
8. `AgentStatus` - 21 edges
9. `AgentSnapshot` - 20 edges
10. `place_call()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Call outcomes (no answer / promise in N days / refuses)` --references--> `CallOutcome`  [INFERRED]
  README.md → app/domain/enums.py
- `Auth: OAuth2 password + JWT HS256 + Argon2id, constant-time login` --references--> `login()`  [INFERRED]
  README.md → app/api/auth.py
- `Debtor eligibility rule (country, product, min days overdue, next_contact_at)` --references--> `next_eligible()`  [INFERRED]
  README.md → app/crud/debtors.py
- `Enums stored as VARCHAR (native_enum=False)` --references--> `str_enum()`  [INFERRED]
  README.md → app/models/types.py
- `Agent soft delete, 409 if active` --references--> `AgentIsActive`  [INFERRED]
  README.md → app/services/agents.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Grafana metrics/logs/traces correlation via trace_id** — monitoring_grafana_provisioning_datasources_datasources_prometheus, monitoring_grafana_provisioning_datasources_datasources_loki, monitoring_grafana_provisioning_datasources_datasources_tempo, app_telemetry, readme_trace_log_correlation [INFERRED 0.95]
- **CircleCI build-and-test pipeline jobs** — circleci_config_build_and_test, circleci_config_test_python, circleci_config_migrations, circleci_config_test_frontend [EXTRACTED 1.00]
- **Observability stack services (Prometheus, Grafana, Loki, Alloy, Tempo)** — docker_compose_prometheus, docker_compose_grafana, docker_compose_loki, docker_compose_alloy, docker_compose_tempo, readme_observability [INFERRED 0.95]

## Communities (35 total, 11 thin omitted)

### Community 0 - "API y servicio de agentes"
Cohesion: 0.07
Nodes (62): agent_stats(), call_now(), create_agent(), delete_agent(), get_agent(), list_agent_calls(), list_agents(), pause_agent() (+54 more)

### Community 1 - "Deudores y registro de llamadas"
Cohesion: 0.08
Nodes (52): get_debtor(), list_debtor_calls(), list_debtors(), CurrentUser, DbSession, ge, get, le (+44 more)

### Community 2 - "Cableado de la app"
Cohesion: 0.05
Nodes (51): get_call_engine(), get_clock(), datetime, datetime, utcnow(), app_crud, lifespan(), FastAPI (+43 more)

### Community 3 - "Engine de llamadas emulado"
Cohesion: 0.11
Nodes (39): CallOutcome, NegotiationStyle, app_services_call_engine, AgentSnapshot, CallResult, DebtorSnapshot, Puerto de llamadas: el engine recibe snapshots inmutables y devuelve un…, TranscriptLine (+31 more)

### Community 4 - "Config, métricas y CI"
Cohesion: 0.05
Nodes (46): Settings, BaseSettings, CircleCI config.yml, build-and-test workflow, Coveralls orb (coverage upload), migrations job (alembic round-trip + seed vs Postgres 16), py executor (cimg/python:3.14), setup-uv command (uv install + cache + sync --frozen) (+38 more)

### Community 5 - "Fixtures de test y auth"
Cohesion: 0.06
Nodes (32): hash_password(), fastapi_testclient, fixture, itertools, pytest, sqlalchemy_pool, auth_headers(), call_engine() (+24 more)

### Community 6 - "Alembic y modelos ORM"
Cohesion: 0.09
Nodes (39): do_run_migrations(), UTCDateTime solo agrega lógica en Python: en la migración es un timestamptz…, Run migrations in 'offline' mode. This configures the context with just a URL…, In this scenario we need to create an Engine and associate a connection with…, Run migrations in 'online' mode., render_item(), run_async_migrations(), run_migrations_offline() (+31 more)

### Community 7 - "Migración inicial y login"
Cohesion: 0.06
Nodes (40): alembic, app_api, login(), me(), CurrentUser, DbSession, Depends, get (+32 more)

### Community 8 - "Auth y cliente HTTP (front)"
Cohesion: 0.15
Nodes (17): fetchMe(), login(), ApiError, setUnauthorizedHandler(), tokenStore, KlevaUser, App(), AuthContext (+9 more)

### Community 9 - "Catálogos y labels"
Cohesion: 0.18
Nodes (17): get_catalogs(), CurrentUser, get, label(), Catalogs, CountryOption, Option, ProductOption (+9 more)

### Community 10 - "Campos de formulario y esfera"
Cohesion: 0.19
Nodes (10): EMPTY, Values, AgentStage(), FieldProps, frontend_src_components_field_module, SelectField(), TextField(), frontend_src_components_orb_module (+2 more)

### Community 11 - "Botones y stat cards"
Cohesion: 0.20
Nodes (11): Button(), buttonClass(), ButtonLink(), frontend_src_components_button_module, StyleProps, Variant, ConfirmButton(), frontend_src_components_statcard_module (+3 more)

### Community 12 - "Config de TypeScript"
Cohesion: 0.12
Nodes (15): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, noFallthroughCasesInSwitch (+7 more)

### Community 13 - "Manifiesto del frontend"
Cohesion: 0.13
Nodes (14): name, private, type, version, jsdom, lucide-react, openapi-typescript, react-dom (+6 more)

### Community 14 - "Formularios y errores de agente"
Cohesion: 0.23
Nodes (13): useAgent(), useCatalogs(), ValidationErrorItem, FormErrors, MESSAGES, parseFormError(), AgentControls(), placeCall() (+5 more)

### Community 15 - "Tipos de API y transcript"
Cohesion: 0.14
Nodes (13): Agent, AgentCreate, AgentStats, AgentUpdate, Call, Catalogs, Schemas, Token (+5 more)

### Community 16 - "Ruteo y layout"
Cohesion: 0.25
Nodes (10): router, useAuth(), RequireAuth(), AppLayout(), AppNav(), frontend_src_layout_appnav_module, Wordmark(), NotFound() (+2 more)

### Community 17 - "Dependencias de desarrollo"
Cohesion: 0.15
Nodes (13): devDependencies, jsdom, openapi-typescript, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event, @types/node, @types/react (+5 more)

### Community 18 - "Hooks de datos de agentes"
Cohesion: 0.36
Nodes (12): agentKeys, useAgents(), useCallNow(), useCreateAgent(), useDeleteAgent(), useInvalidateAgents(), useSetAgentStatus(), useUpdateAgent() (+4 more)

### Community 19 - "Detalle de agente y formato"
Cohesion: 0.29
Nodes (10): useAgentCalls(), useAgentStats(), frontend_src_layout_pageheader_module, PageHeader(), formatDate(), formatDateTime(), formatDuration(), formatMoney() (+2 more)

### Community 20 - "Tarjeta de agente y badges"
Cohesion: 0.35
Nodes (7): Group, useLabels(), AgentCard(), frontend_src_components_agentcard_module, frontend_src_components_badge_module, OutcomeBadge(), StatusBadge()

### Community 21 - "Tests del formulario"
Cohesion: 0.22
Nodes (6): catalogs, onSubmit(), ref_testing_library_jest_dom_vitest, @testing-library/react, @testing-library/user-event, vitest

### Community 22 - "Dependencias de runtime"
Cohesion: 0.25
Nodes (8): dependencies, @fontsource-variable/archivo, @fontsource-variable/jetbrains-mono, lucide-react, react, react-dom, react-router, @tanstack/react-query

### Community 23 - "Scripts de npm"
Cohesion: 0.33
Nodes (6): scripts, build, dev, gen:api, preview, test

## Knowledge Gaps
- **78 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+73 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 235 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_catalogs()` connect `Catálogos y labels` to `API y servicio de agentes`, `Deudores y registro de llamadas`, `Engine de llamadas emulado`?**
  _High betweenness centrality (0.265) - this node is a cross-community bridge._
- **Why does `Frontend types generated from OpenAPI, labels from /catalogs` connect `Catálogos y labels` to `Tarjeta de agente y badges`?**
  _High betweenness centrality (0.261) - this node is a cross-community bridge._
- **Why does `useLabels()` connect `Tarjeta de agente y badges` to `Catálogos y labels`, `Botones y stat cards`, `Formularios y errores de agente`, `Hooks de datos de agentes`, `Detalle de agente y formato`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Country` (e.g. with `list_debtors()` and `list_debtors()`) actually correct?**
  _`Country` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `ProductType` (e.g. with `list_debtors()` and `list_debtors()`) actually correct?**
  _`ProductType` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CallOutcome` (e.g. with `stats_by_agent()` and `Call`) actually correct?**
  _`CallOutcome` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `CollectionAgent` (e.g. with `AgentStatus` and `AgentType`) actually correct?**
  _`CollectionAgent` has 6 INFERRED edges - model-reasoned connections that need verification._