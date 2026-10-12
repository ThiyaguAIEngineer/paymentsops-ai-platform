# PaymentOps AI Platform

Week 1: a read-only Commercial Wire Validation Simulator using synthetic data.

Week 1 implementation and manual verification are complete, subject to the final
Git checkpoint. See [PROJECT_STATE.md](PROJECT_STATE.md) for the project handoff.
The next phase is Week 2 — Payment Operations Knowledge using RAG; it is not yet
implemented.

## Run the dashboard

From the repository root:

```powershell
uv sync --locked
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

Open the local URL printed by Streamlit. The dashboard processes all 20 sample
instructions through PaymentService, supports decision filtering and payment
selection, and displays all six control findings.

Total Payment Value sums finite, positive Decimal amounts in USD, including
amounts on rejected instructions. Missing, nonfinite, zero, and negative amounts
are excluded from the value metric, but their instructions remain visible and
count toward Total Payments. The excluded count is shown beside the metrics.

## Architecture and connector evidence

The domain contains the immutable Payment model and input validator. Four
vendor-neutral connector Protocols supply frozen normalized responses from
deterministic, read-only mock datasets. PaymentService receives these connectors
through constructor injection and coordinates lookups. The stateless Decision
Engine evaluates six areas: input, account, balance, limit, fraud, and sanctions.
Rejection takes precedence over review, then readiness; all findings are retained.

`PaymentService.process_payment_with_evidence(payment)` returns a frozen
`PaymentProcessingResult` containing the existing `DecisionResult` and a frozen
`ConnectorEvidence`. Evidence references the same AccountResponse, LimitsResponse,
FraudResponse, and SanctionsResponse objects supplied to the engine. No banking
rules or connector lookups are duplicated. The compatible `process_payment()`
method delegates to this workflow and returns only DecisionResult.

The dashboard caches the rich service results and displays account status,
wire-enabled status, available balance, configured wire limit, fraud score and
decision, and sanctions result. USD amounts retain Decimal precision. The UI
does not perform evidence lookups or interpret screening scores.

Failed lookups leave evidence absent and retain explicit UNAVAILABLE findings.
Invalid instructions skip lookups and retain SKIPPED findings. Exceptions are
sanitized at the service boundary; no balances, scores, or successful screenings
are invented. Retrieved evidence may support a rejection or review and does not
itself imply PASS. Evidence contains no extra account identifiers or metadata.

All inputs and integrations are synthetic mocks. No real bank systems, payment
execution, databases, authentication, or AI capabilities are included.

## Tests

```powershell
uv run pytest
```

Tests include Streamlit AppTest interactions and a local headless server health
check. No payment execution, real integrations, or external API calls are included.

Week 1 acceptance is tracked in [docs/WEEK1_ACCEPTANCE.md](docs/WEEK1_ACCEPTANCE.md),
based on the requirements stated during development, not a local original PRD.
