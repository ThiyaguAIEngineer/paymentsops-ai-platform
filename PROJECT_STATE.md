# Payment Operations Intelligence Platform — project state

## Current phase

Week 1 — Commercial Wire Payment Validation Simulator.
Implementation and manual acceptance are complete, subject to the final Git
checkpoint. This document reflects requirements supplied during development;
the original approved PRD and project handoff are not available locally.

## Completed functionality

- Immutable Payment model with eight required instruction fields, optional
  missing values, Decimal amounts, and Python date values.
- Input validation collecting all errors without mutating instructions.
- Four vendor-neutral connector Protocols and deterministic mock implementations:
  Core Banking, Limits, Fraud, and Sanctions.
- Deterministic evaluation of six areas: payment input, active/wire-enabled
  account, available balance, single-wire limit, fraud, and sanctions.
- Dependency-injected PaymentService orchestrating validation, independent
  connector lookups, error normalization, and decision evaluation.
- Twenty synthetic instructions spanning successful, rejected, review, boundary,
  invalid-input, and connector-outage scenarios.
- Streamlit dashboard with dynamic metrics, decision filtering, payment
  selection, all control findings, and read-only connector evidence.
- Complete DecisionResult with retained findings and deterministic primary reason.
- Immutable PaymentProcessingResult and ConnectorEvidence; compatible legacy
  process_payment() consumers continue receiving DecisionResult.

## Architecture

The Payment Service coordinates components; this is a logical flow rather than
a chain in which connectors invoke the Decision Engine:

```text
Streamlit UI
    |
    v
Payment Service
    |-- Payment Input Validation
    |      `-- Invalid input: skip connector lookups
    |-- Valid input: Vendor-Neutral Connector Interfaces
    |      `-- Mock Core / Limits / Fraud / Sanctions
    |-- Deterministic Decision Engine (input + normalized responses/errors)
    `-- PaymentProcessingResult
           |-- DecisionResult
           `-- ConnectorEvidence (exact retrieved response objects)
                   |
                   v
              Streamlit UI
```

Domain models and input validation live under domain/, connector contracts and
mock data under connectors/, orchestration and evaluation under services/,
synthetic instructions under samples/, and presentation under ui/. The UI
composes injected mock dependencies but performs no screening lookups or banking
rule evaluation. Cached service results supply both findings and evidence.

## Architectural decisions

- Synthetic payment data only; no real bank integrations or payment execution.
- Domain logic separated from UI; vendor-neutral interfaces and constructor
  dependency injection keep orchestration independent of mock implementations.
- Deterministic business rules: rejection takes precedence over review; all
  failed/review findings remain available and primary reasons use fixed ordering.
- Unavailable mandatory controls never silently pass. Safe review treatment
  preserves available rejections. Invalid input produces skipped downstream checks.
- Immutable connector evidence reuses normalized frozen response types. No
  fabricated zero balances, PASS decisions, or raw exceptions are exposed.
- Decimal monetary values; read-only mock records; privacy-conscious logging.
- Shared processing workflow retrieves each connector once per valid instruction.

## Verification

The final Week 1 suite contains 273 tests covering domain validation, connectors,
decision boundaries and precedence, service interactions, evidence identity,
compatibility, all 20 scenarios, UI metrics/filtering/selection, error presentation,
and a temporary localhost Streamlit startup health check.

Final checkpoint verification: uv run pytest passed all 273 tests; git diff --check
passed. The project owner confirmed successful manual dashboard launch, correctly
displayed evidence, and all important manual scenarios.

Baseline metrics: 20 payments; $300,107.02 total finite positive instruction value;
4 ready, 6 manual review, 10 rejected. Three invalid amounts are excluded from
value, while all instructions remain included in counts and the table.

## Dependencies and commands

- Python 3.13 (.python-version; project requires Python >=3.13).
- uv manages the environment and uv.lock.
- Runtime: Streamlit >=1.65.0 (locked to 1.65.0 plus transitive dependencies).
- Development: pytest >=9.1.1 (locked to 9.1.1).
- Build backend: uv_build >=0.12.23,<0.13.0.

```powershell
uv sync --locked
uv run pytest
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

## Remaining blockers and warnings

No identified functional blockers against the stated Week 1 requirements.
The final Git commit remains pending explicit approval; no automatic commit/push.
Original PRD/handoff documents are unavailable locally, limiting verification to
the requirements supplied during development and docs/WEEK1_ACCEPTANCE.md.

Environment warnings encountered: an unrelated VIRTUAL_ENV is ignored by uv;
restricted uv cache access required elevated execution; Git may normalize LF
to CRLF on Windows. These did not prevent successful verification.
The scaffold console command payment-ops still prints a greeting; use the
documented Streamlit launch command. Project description metadata remains a
placeholder, with no effect on simulator operation.

Git review retains application files and excludes environments, bytecode,
pytest caches, .env files, and Streamlit secrets. No credentials were identified
in reviewed project files; secret-pattern inspection is not a formal security audit.

## Explicitly out of scope

Real banking integrations, payment execution/release, authentication, databases,
API servers, AWS infrastructure, RAG, LLMs, and AI agents. No additional banking
rules, production controls, or Week 2 features were implemented.

## Next task

Review and approve the final Week 1 Git checkpoint. Then define the requirements
and knowledge sources for Week 2 — Payment Operations Knowledge using RAG.
Do not implement Week 2 until its scope is agreed.
