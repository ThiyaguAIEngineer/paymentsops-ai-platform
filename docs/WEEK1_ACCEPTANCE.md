# Week 1 acceptance checklist

Based on the Week 1 requirements stated during development. No original PRD or
separate Definition of Done document was found in the repository.

- [x] Immutable Payment dataclass: eight fields, optional missing values, Decimal
  amounts, Python date; domain independent of UI and external systems.
- [x] Six validation areas: input, active/wire-enabled account, available balance,
  single-wire limit, predetermined fraud decision, and sanctions outcome.
- [x] Four vendor-neutral Protocols, injected into PaymentService; read-only,
  deterministic synthetic mock datasets with normalized frozen response types.
- [x] Decision precedence: REJECTED, then MANUAL REVIEW, then READY FOR PROCESSING;
  all findings retained with deterministic primary-reason selection.
- [x] Connector failures never imply PASS; available rejections retain precedence;
  invalid instructions skip downstream lookups; logs and errors omit raw details.
- [x] Twenty synthetic scenarios with independently asserted expected outcomes,
  including boundaries, rejection/review combinations, invalid inputs, and outage.
- [x] Streamlit dashboard: dynamic metrics, decision filter, payment selection,
  six check findings, primary reason, and all review/rejection explanations.
- [x] Read-only connector evidence: exact responses used for decisions; absent
  evidence labeled UNAVAILABLE or SKIPPED; balances and limits formatted as USD.
- [x] Automated tests cover compatibility, evidence identity, single lookups,
  unchanged decisions, failure safety, UI interactions, and localhost startup.
- [x] Automated verification: uv run pytest passed all 273 tests, including the
  localhost Streamlit startup health check; git diff --check passed.
- [x] Manual verification confirmed by the project owner: dashboard launched,
  connector evidence correctly displayed, and important scenarios checked.
- [x] Git ignore rules exclude generated caches, environments, and local .env files;
  source, tests, uv.lock, and .python-version are retained.
- [x] Git delivery preparation: source, tests, dependencies, and documentation
  reviewed and staged; no generated files or credentials included.
- [ ] Final Git checkpoint: commit only after explicit approval; no automatic
  commit or push. Week 1 implementation is complete subject to this checkpoint.

Excluded from Week 1: banking execution, external integrations, authentication,
APIs, databases, cloud infrastructure, RAG, and AI agents. No extra banking rules.
