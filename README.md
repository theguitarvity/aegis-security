<div align="center">

# Aegis Security

**Local-first Security Validation Harness para agentes.**

`aegis-security` descobre a stack de uma aplicação, executa ferramentas open
source de segurança em escopo controlado, normaliza achados, correlaciona
evidências e entrega relatório técnico + roadmap consumível pelo SpecMaster.

`Python 3 stdlib` · `local-only por padrão` · `Semgrep/Gitleaks/Trivy/Syft/Grype/ZAP/Schemathesis/k6/Toxiproxy` · `compatível com .agent/`

</div>

---

## Por quê

Aegis dá ao agente uma forma segura e repetível de avaliar segurança sem virar
um pentester irrestrito. Ele opera com políticas, escopo explícito, sandboxing
operacional e redaction de evidência sensível.

O contrato é simples:

```text
Aegis identifies.
Aegis proves.
Aegis prioritizes.
Aegis recommends.

SpecMaster implements.
```

## Como funciona

```text
Discovery -> Target validation -> Threat model -> SAST/secrets/SCA/SBOM
-> DAST/API/resilience quando permitido -> Normalization -> Deduplication
-> Correlation -> Score -> Release gate -> Report -> SpecMaster roadmap
```

O agente deve usar os scripts como fonte de verdade para discovery,
normalização, score e gate. A interpretação em linguagem natural só acontece
depois que os artefatos estruturados existem.

## Instalação Global

Uma vez por máquina:

```bash
./init.sh
```

Isso espelha o engine para `~/.aegis-security-engine` e instala ponteiros
globais em:

| Agente | Entrypoint global |
|---|---|
| OpenAI Codex CLI | `~/.codex/skills/aegis-security/SKILL.md` |
| fallback `.agent/` | `~/.agents/skills/aegis-security/SKILL.md` |
| GitHub Copilot CLI | `~/.copilot/skills/aegis-security/SKILL.md` |
| Claude Code | `~/.claude/commands/aegis-security.md`, `~/.claude/skills/aegis-security/SKILL.md` |

Para instalar ponteiros em um projeto específico:

```bash
./init.sh link ~/code/meu-projeto
```

## Uso rápido

```bash
python3 .agent/skills/aegis-security/scripts/doctor.py
python3 .agent/skills/aegis-security/scripts/scan.py --project . --profile quick
```

Depois da instalação global:

```bash
python3 ~/.aegis-security-engine/scripts/scan.py --project . --profile quick
```

Perfis:

| Perfil | Uso |
|---|---|
| `quick` | SAST, secrets, SCA, SBOM e filesystem/container/IaC quando as ferramentas existem |
| `standard` | `quick` + ZAP baseline/passive + Schemathesis se houver OpenAPI |
| `adversarial-local` | active scan/interception local autorizados |
| `resilience` | `standard` + k6/Toxiproxy com limites |
| `full` | tudo que estiver permitido pelas políticas |

## Saídas

Os artefatos ficam em `.aegis-security/` no projeto analisado:

- `discovery.json`
- `raw/<tool>.json`
- `normalized-findings.json`
- `assessment.json`
- `security-assessment.md`
- `specmaster-remediation.md`

## Estrutura

```text
.agent/skills/aegis-security/
  SKILL.md
  constitution.md
  policies/
  knowledge/
  tools/
  schemas/
  templates/
  scripts/
  lib/
  adapters/
```

## Guardrails

Por padrão Aegis só trabalha contra repo local, localhost, loopback, Docker e
redes privadas explicitamente autorizadas. URL pública em config não é
autorização. Operações agressivas exigem perfil explícito, alvo explícito e
limites de execução.

## Desenvolvimento

```bash
python3 .agent/skills/aegis-security/scripts/doctor.py
python3 .agent/skills/aegis-security/scripts/scan.py --project . --profile quick
python3 -m unittest discover -s .agent/skills/aegis-security/tests -v
```

O harness degrada com segurança quando uma ferramenta não está instalada,
registrando `skipped` em `assessment.json`.
