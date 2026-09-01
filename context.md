# Implementação da Skill `aegis-security` — Local Security Validation Harness

Você está atuando como Principal Security Engineer, Application Security Architect e Agent Harness Engineer.

Sua missão é implementar no repositório atual uma nova skill chamada:

`aegis-security`

Ela será uma capability cross-agent reutilizável por Codex, Claude Code, GitHub Copilot, Antigravity/Gemini e outros agentes compatíveis com o padrão `.agent/`.

O objetivo é criar um Security Validation Harness local-first capaz de analisar aplicações, executar ferramentas open source de segurança em ambiente controlado, correlacionar achados e gerar um relatório técnico + roadmap de remediação consumível diretamente pelo SpecMaster.

A skill NÃO deve se comportar como um pentester irrestrito.

Ela deve operar como um orquestrador de segurança governado por políticas, com sandboxing, limites de execução, escopo explícito e proteção contra execução destrutiva ou contra alvos externos não autorizados.

---

# 1. Objetivos principais

A implementação deve permitir:

1. Descobrir automaticamente a stack e a superfície de ataque do projeto.
2. Executar análises SAST.
3. Executar análise de secrets.
4. Executar SCA e análise de dependências.
5. Gerar SBOM.
6. Analisar Dockerfiles, Compose, manifests e IaC.
7. Executar DAST local.
8. Executar fuzzing de APIs baseado em OpenAPI quando disponível.
9. Executar interceptação HTTP local controlada.
10. Executar testes de resiliência de rede.
11. Executar load/stress/spike testing local.
12. Correlacionar resultados provenientes de múltiplas ferramentas.
13. Deduplicar findings.
14. Identificar possíveis attack chains.
15. Calcular um Security Score.
16. Definir um release/security gate.
17. Gerar um roadmap de remediação priorizado.
18. Gerar artefatos estruturados consumíveis pelo SpecMaster.
19. Registrar histórico de findings.
20. Operar por padrão somente contra localhost, Docker e redes privadas explicitamente autorizadas.

---

# 2. Nome e localização

Criar:

```text
.agent/
└── skills/
    └── aegis-security/
```

A estrutura mínima esperada é:

```text
.agent/
└── skills/
    └── aegis-security/
        ├── SKILL.md
        ├── README.md
        ├── constitution.md
        ├── threat-modeling.md
        │
        ├── policies/
        │   ├── execution-policy.yaml
        │   ├── target-policy.yaml
        │   ├── severity-policy.yaml
        │   ├── release-gate-policy.yaml
        │   └── tool-allowlist.yaml
        │
        ├── knowledge/
        │   ├── owasp-top-10.md
        │   ├── owasp-api-top-10.md
        │   ├── cwe.md
        │   ├── cvss.md
        │   ├── stride.md
        │   ├── authentication.md
        │   ├── authorization.md
        │   ├── cryptography.md
        │   ├── secure-design.md
        │   ├── supply-chain.md
        │   ├── secrets-management.md
        │   ├── containers.md
        │   ├── resilience.md
        │   └── threat-modeling.md
        │
        ├── tools/
        │   ├── semgrep.md
        │   ├── gitleaks.md
        │   ├── trivy.md
        │   ├── syft.md
        │   ├── grype.md
        │   ├── zap.md
        │   ├── schemathesis.md
        │   ├── mitmproxy.md
        │   ├── k6.md
        │   └── toxiproxy.md
        │
        ├── schemas/
        │   ├── discovery.schema.json
        │   ├── finding.schema.json
        │   ├── assessment.schema.json
        │   ├── attack-chain.schema.json
        │   ├── remediation.schema.json
        │   └── roadmap.schema.json
        │
        ├── templates/
        │   ├── executive-summary.md
        │   ├── security-assessment.md
        │   ├── threat-model.md
        │   ├── attack-surface.md
        │   ├── attack-chains.md
        │   ├── remediation-roadmap.md
        │   └── specmaster-remediation.md
        │
        ├── scripts/
        │   ├── doctor.*
        │   ├── scan.*
        │   ├── normalize.*
        │   ├── correlate.*
        │   ├── report.*
        │   └── cleanup.*
        │
        └── adapters/
            ├── claude/
            ├── codex/
            ├── copilot/
            └── antigravity/
```

Escolha Bash, PowerShell e/ou Python conforme os padrões já adotados no repositório.

Evite duplicar lógica entre adapters.

A implementação canônica deve viver em `.agent/skills/aegis-security/`.

Os adapters devem apenas apontar ou adaptar o formato esperado por cada harness.

---

# 3. Filosofia arquitetural

A skill deve seguir este pipeline:

```text
DISCOVERY
   ↓
TARGET VALIDATION
   ↓
THREAT MODEL
   ↓
STATIC ANALYSIS
   ↓
SUPPLY CHAIN ANALYSIS
   ↓
RUNTIME PREPARATION
   ↓
DAST / API TESTING
   ↓
RESILIENCE / LOAD TESTING
   ↓
NORMALIZATION
   ↓
DEDUPLICATION
   ↓
CORRELATION
   ↓
ATTACK CHAIN ANALYSIS
   ↓
RISK PRIORITIZATION
   ↓
SECURITY SCORE
   ↓
RELEASE GATE
   ↓
REPORT
   ↓
SPECMASTER ROADMAP
```

A skill deve distinguir claramente:

- coleta de evidência;
- interpretação;
- priorização;
- recomendação;
- implementação.

Aegis NÃO deve corrigir automaticamente a aplicação sem delegação explícita.

Por padrão:

```text
Aegis identifies.
Aegis proves.
Aegis prioritizes.
Aegis recommends.

SpecMaster implements.
```

---

# 4. Ferramentas suportadas no MVP

Implementar integração arquitetural e documentação para:

## SAST

- Semgrep

## Secrets

- Gitleaks
- Trivy secret scanning

## Vulnerability / IaC / Containers

- Trivy

## SBOM

- Syft

## SCA

- Grype

## DAST

- OWASP ZAP

## API Testing / Fuzzing

- Schemathesis

## HTTP Interception

- mitmproxy

## Load / Stress

- k6

## Network resilience / failure injection

- Toxiproxy

Não acoplar o projeto fortemente ao formato interno de uma ferramenta.

Todos os outputs devem passar por uma camada de normalização.

---

# 5. Perfis de execução

Implementar conceitualmente os seguintes profiles:

```text
quick
standard
adversarial-local
resilience
full
```

## quick

Executar:

```text
Semgrep
Gitleaks
Trivy
Syft
Grype
```

## standard

Executar:

```text
quick
+
ZAP baseline/passive
+
Schemathesis quando OpenAPI estiver disponível
```

## adversarial-local

Executar:

```text
standard
+
ZAP active scan
+
mitmproxy inspection
+
auth/security negative tests
```

Somente contra alvo explicitamente permitido.

## resilience

Executar:

```text
standard
+
k6
+
Toxiproxy
```

## full

Executar todas as etapas permitidas.

---

# 6. Guardrails obrigatórios

Criar uma policy central.

Exemplo inicial:

```yaml
target_policy:
  default_scope: local-only

  allowed:
    - localhost
    - 127.0.0.1
    - ::1
    - host.docker.internal
    - docker-network
    - private-sandbox

  public_targets:
    default: deny

  production:
    active_scanning: deny
    load_testing: deny
    interception: deny

aggressive_operations:
  default: deny

  require:
    - explicit_profile
    - explicit_authorized_target
    - bounded_execution

destructive_operations:
  default: deny

load_testing:
  max_duration_seconds: 300
  max_virtual_users: 500

  emergency_stop:
    error_rate_percent: 25
    cpu_percent: 95

secrets:
  redact_in_reports: true

evidence:
  redact_tokens: true
  redact_passwords: true
  redact_private_keys: true
```

Nenhuma etapa potencialmente agressiva deve ser executada automaticamente contra um hostname público.

Uma URL pública encontrada em config NÃO representa autorização.

---

# 7. Discovery Engine

Criar um mecanismo de descoberta capaz de detectar, quando possível:

```yaml
application:
  languages: []
  frameworks: []
  package_managers: []
  interfaces: []
  databases: []
  caches: []
  messaging: []
  authentication: []
  authorization: []
  external_integrations: []
  exposed_ports: []
  containers: false
  compose: false
  openapi_files: []
  dockerfiles: []
  ci_cd: []
  infrastructure_as_code: []
```

Exemplos de detecção:

```text
pom.xml
build.gradle
package.json
pyproject.toml
go.mod
Cargo.toml

Dockerfile
docker-compose.yml
compose.yaml

openapi.yaml
swagger.json

application.yml
application.properties

.env.example

.github/workflows
azure-pipelines.yml
```

Nunca expor secret real durante discovery.

---

# 8. Threat Model

A partir do discovery, gerar:

```text
attack-surface.md
threat-model.md
```

Usar conceitos:

- STRIDE
- OWASP Top 10
- OWASP API Security Top 10
- CWE
- trust boundaries
- entry points
- data flows
- privileged operations
- external dependencies

Gerar uma representação simples da superfície:

```text
Actor
 ↓
Frontend
 ↓
API
 ↓
Domain
 ↓
Database

API
 ↓
External Provider
```

Mapear:

```text
Component
Trust boundary
Data classification
Attack surface
Potential threat
Security control
```

---

# 9. Schema canônico de Finding

Definir um schema JSON capaz de representar resultados de qualquer ferramenta.

Exemplo conceitual:

```json
{
  "id": "SEC-001",
  "fingerprint": "",
  "title": "",
  "description": "",
  "severity": "critical|high|medium|low|info",
  "confidence": "high|medium|low",

  "source": {
    "tool": "",
    "rule_id": "",
    "raw_reference": ""
  },

  "classification": {
    "cwe": [],
    "owasp": [],
    "owasp_api": [],
    "cvss": null
  },

  "component": {
    "service": "",
    "file": "",
    "line": null,
    "endpoint": "",
    "dependency": ""
  },

  "evidence": [],

  "risk": {
    "exploitability": "",
    "impact": "",
    "likelihood": ""
  },

  "remediation": {
    "summary": "",
    "architectural_action_required": false,
    "recommended_actions": []
  },

  "status": "open|accepted|fixed|false-positive"
}
```

---

# 10. Normalização

Cada ferramenta deve possuir um adapter:

```text
raw tool result
    ↓
parser
    ↓
normalized Finding
```

Exemplo:

```text
Semgrep JSON
Trivy JSON
Grype JSON
ZAP JSON
Schemathesis results
```

devem convergir para o mesmo modelo.

Nunca fazer o relatório final diretamente sobre outputs raw.

---

# 11. Deduplicação

Implementar fingerprint baseado, quando disponível, em uma combinação de:

```text
rule
component
file
line
endpoint
dependency
CWE
normalized title
```

Exemplo:

```text
Semgrep finds SQL Injection
ZAP reproduces SQL Injection
```

Não devem obrigatoriamente aparecer como dois findings distintos.

O correlation engine pode gerar:

```yaml
finding:
  id: SEC-013
  confidence: high

evidence_sources:
  - semgrep
  - zap

static_evidence: true
runtime_reproduction: true
```

---

# 12. Correlation Engine

O correlation engine deve conseguir elevar confiança quando múltiplas ferramentas corroboram o mesmo problema.

Exemplo:

```text
Semgrep
   +
ZAP
   +
Runtime
   ↓
Confirmed vulnerability
```

Outro exemplo:

```text
Trivy CVE
+
Syft SBOM
+
Dependency actually reachable
↓
Higher priority
```

O LLM pode ajudar na interpretação, porém resultados determinísticos devem ser preservados.

Nunca permitir que raciocínio probabilístico destrua a evidência original.

---

# 13. Attack Chain Analysis

Implementar estrutura para correlacionar achados potencialmente encadeáveis.

Exemplo:

```text
User enumeration
       ↓
Weak reset endpoint
       ↓
No rate limit
       ↓
Account takeover
```

Schema conceitual:

```json
{
  "id": "CHAIN-001",
  "title": "Potential account takeover",
  "severity": "critical",
  "steps": [
    "SEC-003",
    "SEC-008",
    "SEC-011"
  ],
  "confidence": "medium",
  "reasoning": "",
  "recommended_controls": []
}
```

Evitar afirmar exploração real sem evidência.

Distinguir:

```text
confirmed chain
potential chain
hypothesized chain
```

---

# 14. Security Score

Criar score de 0–100.

Categorias iniciais:

```text
Code Security
Dependencies
Secrets
API Security
Authentication
Authorization
Container Security
Data Protection
Resilience
Configuration
```

Exemplo:

```text
Overall             67

Code Security       82
Dependencies        63
Secrets             96
API Security        58
Authentication      74
Authorization       52
Container Security  70
Resilience          44
```

Documentar claramente a fórmula.

O score NÃO pode esconder findings críticos.

---

# 15. Release Gate

Criar política como:

```yaml
release_gate:
  block_on:
    critical: 1

  high:
    max_open: 0

  medium:
    max_open: 20

  exceptions:
    accepted_risk_allowed: true
```

Resultado:

```text
PASS
PASS_WITH_RISK
BLOCKED
```

Um Critical aberto deve bloquear por padrão.

---

# 16. Load / Stress Testing

A skill não deve falar em “DDoS contra alvo”.

Modelar esta capability como:

```text
load testing
stress testing
spike testing
soak testing
breakpoint testing
resource exhaustion validation
```

Usar k6.

Definir thresholds configuráveis:

```yaml
thresholds:
  p95_ms: 500
  p99_ms: 1000
  error_rate_percent: 1
```

Criar kill switch.

Nunca executar stress contra internet pública por padrão.

---

# 17. Network resilience

Toxiproxy deve permitir cenários como:

```text
latency
timeout
connection reset
bandwidth restriction
temporary outage
slow downstream
```

Usos:

```text
application → database
application → redis
application → mock payment provider
application → mock external API
```

Sempre em ambiente controlado.

---

# 18. HTTP interception

Usar mitmproxy apenas para ambiente local/sandbox.

Analisar:

```text
Authorization headers
cookies
JWT leakage
query-string secrets
security headers
PII exposure
cache headers
redirects
TLS assumptions
CORS
```

Redactar conteúdo sensível nos artefatos.

---

# 19. Diretório de saída

Cada execução deve gerar:

```text
.security/
└── assessments/
    └── <timestamp-or-run-id>/
        ├── executive-summary.md
        ├── security-assessment.md
        ├── threat-model.md
        ├── attack-surface.md
        ├── attack-chains.md
        ├── findings.json
        ├── assessment.json
        ├── findings.sarif
        ├── sbom.cdx.json
        ├── sbom.spdx.json
        │
        ├── evidence/
        │
        ├── raw/
        │   ├── semgrep/
        │   ├── trivy/
        │   ├── grype/
        │   ├── zap/
        │   ├── schemathesis/
        │   └── k6/
        │
        └── specmaster/
            ├── remediation-roadmap.md
            └── remediation-backlog.json
```

---

# 20. Roadmap para SpecMaster

Este é um requisito fundamental.

Gerar:

```text
.security/assessments/<run>/specmaster/remediation-roadmap.md
```

Formato:

```markdown
# Security Remediation Roadmap

## P0 — Immediate

### SEC-001 — Broken Object Level Authorization

Severity:
CRITICAL

Affected:
user-service

Problem:
...

Evidence:
...

Architecture impact:
...

Recommended approach:
...

Acceptance criteria:

- authorization enforced at service boundary
- user A cannot access user B resource
- integration tests cover horizontal privilege escalation
- adversarial test must no longer reproduce issue

Validation strategy:

- unit tests
- integration tests
- API negative tests
- Aegis re-scan

Definition of Done:

- implementation completed
- tests passing
- finding no longer reproducible
- no new Critical/High introduced
```

---

# 21. Backlog JSON para automação futura

Gerar também:

```json
{
  "source": "aegis-security",
  "assessment": "",
  "items": [
    {
      "id": "SEC-001",
      "priority": "P0",
      "severity": "critical",
      "title": "",
      "affected_components": [],
      "implementation_goal": "",
      "acceptance_criteria": [],
      "validation": [],
      "dependencies": []
    }
  ]
}
```

Esse formato deverá ser pensado para futura ingestão automática pelo SpecMaster.

---

# 22. Security feedback loop

Documentar formalmente o ciclo:

```text
SpecMaster
    ↓
Implementation
    ↓
Aegis
    ↓
Security assessment
    ↓
PASS / FAIL
         ↓
    remediation roadmap
         ↓
    SpecMaster
         ↓
       fixes
         ↓
    Aegis re-scan
```

Definition of Done futura:

```text
Functional Validation
+
Architecture Validation
+
Security Validation
+
No unresolved Critical
+
No unresolved High without accepted risk
=
DONE
```

---

# 23. Histórico de findings

Implementar um mecanismo simples para comparar runs.

Status possíveis:

```text
new
existing
fixed
reintroduced
accepted
```

Exemplo:

```text
SEC-018

first_seen:
2026-08-20

fixed:
2026-08-25

reintroduced:
2026-09-01
```

Não exigir banco externo.

Pode usar JSON/Markdown no próprio `.security/`.

---

# 24. Knowledge Graph readiness

Não tornar o Aegis dependente de Neo4j, JanusGraph ou qualquer engine externa.

Entretanto, estruturar findings para permitir futura Graphify/Obsidian integration.

Modelo conceitual:

```text
Application
  └─ HAS_COMPONENT → Component

Component
  ├─ EXPOSES → Endpoint
  ├─ DEPENDS_ON → Dependency
  ├─ HAS_VULNERABILITY → Finding
  ├─ PROTECTED_BY → SecurityControl
  └─ COMMUNICATES_WITH → ExternalSystem

Finding
  ├─ INSTANCE_OF → CWE
  ├─ RELATED_TO → OWASP
  ├─ ENABLES → AttackChain
  ├─ AFFECTS → Component
  └─ MITIGATED_BY → SecurityControl
```

Se o repositório já possuir mecanismos Graphify/Knowledge Graph, aproveitar os contratos existentes sem criar dependência rígida.

---

# 25. SKILL.md

O `SKILL.md` deve ensinar ao agente:

- quando ativar Aegis;
- quando NÃO executar ferramentas;
- como validar alvo;
- como descobrir stack;
- como selecionar profile;
- como executar scanners;
- como normalizar resultados;
- como interpretar findings;
- como distinguir evidence de hypothesis;
- como correlacionar achados;
- como gerar roadmap;
- como realizar re-scan;
- como encerrar e limpar o sandbox.

Incluir uma regra forte:

```text
Never treat the mere existence of a URL as authorization to attack, scan actively, intercept, load test or fuzz that target.
```

---

# 26. Interface de uso

Criar uma interface simples e independente de agente.

Exemplos desejáveis:

```bash
aegis doctor
```

```bash
aegis scan .
```

```bash
aegis scan . --profile quick
```

```bash
aegis scan . --profile standard
```

```bash
aegis scan . --profile resilience
```

```bash
aegis scan . \
  --profile adversarial-local \
  --target http://localhost:8080
```

```bash
aegis report
```

```bash
aegis compare <run-a> <run-b>
```

```bash
aegis cleanup
```

Se o repositório possuir uma CLI/framework próprio, integrar ao padrão existente em vez de inventar outra arquitetura paralela.

---

# 27. Doctor

Implementar um doctor que detecte disponibilidade de:

```text
Docker
Semgrep
Gitleaks
Trivy
Syft
Grype
ZAP
Schemathesis
mitmproxy
k6
Toxiproxy
```

Resultado esperado:

```text
Aegis Security Doctor

Docker           PASS
Semgrep          PASS
Gitleaks         PASS
Trivy            PASS
Syft             PASS
Grype            PASS
OWASP ZAP        OPTIONAL / Docker
Schemathesis     PASS
mitmproxy        MISSING
k6               PASS
Toxiproxy        PASS
```

Classificar ferramentas em:

```text
required
recommended
optional
```

Não falhar completamente se ferramentas opcionais estiverem indisponíveis.

---

# 28. Docker-first support

Sempre que viável, permitir execução das ferramentas via containers para evitar poluir a máquina host.

Exemplo conceitual:

```text
Aegis
 ↓
Docker network
 ├─ target app
 ├─ zap
 ├─ toxiproxy
 └─ auxiliary tooling
```

Não criar Kubernetes nesta fase.

Local-first significa:

```text
native process
Docker
Docker Compose
```

---

# 29. Cross-platform

A implementação deve considerar:

```text
macOS
Linux
Windows
```

Evitar paths hardcoded.

PowerShell deve ser compatível com Windows PowerShell/PowerShell moderno quando isso fizer sentido para o repo.

Se Python for usado para orchestration, preferir abordagem cross-platform.

---

# 30. Qualidade

A implementação deve possuir:

- lint;
- schemas validados;
- scripts idempotentes;
- tratamento de falha de ferramenta;
- timeout;
- limpeza de processos;
- cleanup de containers;
- logs estruturados;
- exit codes previsíveis.

Um scanner falhar não deve necessariamente invalidar a assessment inteira.

O relatório deve registrar:

```text
tool_status:
  semgrep: success
  trivy: success
  zap: timeout
```

---

# 31. Testes

Criar testes para pelo menos:

1. validação de target permitido;
2. bloqueio de hostname público;
3. redaction de secret;
4. normalização de finding;
5. fingerprint;
6. deduplicação;
7. correlação;
8. severity sorting;
9. release gate;
10. roadmap generation;
11. historical comparison;
12. tool failure handling.

Criar fixtures sintéticas.

Não depender de vulnerabilidades reais externas.

---

# 32. Fixtures vulneráveis locais

Se apropriado, criar um pequeno conjunto de fixtures de teste local para validar o harness.

Exemplos:

```text
test-fixtures/
  vulnerable-api/
  vulnerable-config/
  vulnerable-dockerfile/
```

Eles podem conter falhas intencionais exclusivamente para teste automatizado.

Não usar sistemas externos.

---

# 33. Definition of Done

A implementação só é considerada completa quando:

```text
[ ] Skill criada em .agent/skills/aegis-security
[ ] Policies implementadas
[ ] Target guard funcionando
[ ] Discovery funcionando
[ ] Tool adapters definidos
[ ] Normalização funcionando
[ ] Deduplicação funcionando
[ ] Correlation engine funcionando
[ ] Security Score funcionando
[ ] Release Gate funcionando
[ ] Report generation funcionando
[ ] SpecMaster roadmap funcionando
[ ] Historical comparison funcionando
[ ] Cross-agent adapters criados
[ ] Doctor funcionando
[ ] Tests passing
[ ] README atualizado
[ ] Exemplos de execução documentados
```

---

# 34. Importante: respeitar o harness existente

Antes de implementar:

1. inspecione o repositório;
2. identifique a arquitetura do SpecMaster;
3. identifique convenções existentes para `.agent/`;
4. identifique adapters Claude/Codex/Copilot/Antigravity existentes;
5. identifique mecanismos de knowledge, Graphify ou Obsidian existentes;
6. identifique padrões de CLI;
7. identifique padrões de testes;
8. identifique padrões de configuração.

Não crie estruturas paralelas se já existir um padrão equivalente.

Prefira estender o harness existente.

---

# 35. Não fazer

Não:

- atacar endereços públicos;
- executar load test em internet pública;
- executar scans ativos em produção;
- criar código de DDoS;
- implementar evasão de WAF;
- implementar malware;
- implementar persistência ofensiva;
- implementar credential stuffing;
- implementar brute force irrestrito;
- armazenar secrets capturados;
- enviar código ou findings para serviços externos;
- exigir SaaS;
- exigir Kubernetes;
- tornar DefectDojo obrigatório.

---

# 36. Evolução futura

Preparar arquitetura, mas NÃO necessariamente implementar agora:

```text
DefectDojo integration
CI/CD security gates
Kubernetes sandbox
DAST against ephemeral environments
Graphify security graph
Obsidian security knowledge
SARIF publishing
GitHub/Azure DevOps annotations
risk acceptance workflow
policy-as-code
security baselines
architecture threat drift
```

O MVP deve permanecer simples o suficiente para rodar localmente.

---

# 37. Entrega

Implemente de fato.

Não entregue apenas documentação ou plano.

Durante a implementação:

- faça mudanças incrementais;
- mantenha o build verde;
- execute testes;
- corrija problemas encontrados;
- documente decisões arquiteturais relevantes.

Ao terminar, gere um relatório:

```text
.spec-master/reports/aegis-security-implementation-report.md
```

Incluindo:

```text
Summary
Architecture
Files created
Files modified
Supported capabilities
Security guardrails
Tool support
Testing performed
Known limitations
Future evolution
Example commands
Definition of Done validation
```

Também inclua uma árvore final relevante da implementação.

---

# 38. Critério arquitetural final

O resultado deve se comportar como:

```text
              Agent Harness
                   │
            aegis-security
                   │
       ┌───────────┼───────────┐
       │           │           │
   Discovery    Testing    Correlation
       │           │           │
       └───────────┼───────────┘
                   │
             Risk Analysis
                   │
          Security Assessment
                   │
         Remediation Roadmap
                   │
              SpecMaster
```

O Aegis deve ser uma capability de Security Engineering integrada ao harness.

Ele não deve ser simplesmente um wrapper de shell em torno de scanners.