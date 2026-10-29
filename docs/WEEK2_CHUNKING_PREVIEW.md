# Structural chunking inspection

Generated from the ingestion and chunking APIs. No embeddings or index created.

Sizes are ceil(characters / 4), not exact model token counts.

| Metric | Actual |
| --- | --- |
| Documents | 6 |
| Sections | 31 |
| Chunks | 32 |
| Minimum estimated tokens | 139 |
| Average estimated tokens | 285.88 |
| Maximum estimated tokens | 435 |
| Sections split | 1 |

## Section split details

- `SYN-STATUS/SS-STATES`: 2 chunks; split at a paragraph boundary.

## Representative chunks

### SYN-ERROR-CATALOG/EC-BENEFICIARY

Estimated tokens: 237

```json
{
  "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856",
  "document_id": "SYN-ERROR-CATALOG",
  "document_title": "Payment Error-Code Catalog",
  "document_version": "1.0.0",
  "effective_date": "2026-10-28",
  "document_type": "catalog",
  "source_path": "data/knowledge/documents/payment_error_code_catalog.md",
  "section_id": "EC-BENEFICIARY",
  "section_heading": "EC-BENEFICIARY — Beneficiary validation codes",
  "chunk_index": 0
}
```

```markdown
## EC-BENEFICIARY — Beneficiary validation codes

**section_id: EC-BENEFICIARY**

| Code | Meaning | Impact | Initial action | Retry restriction | Owner | Governing section |
| --- | --- | --- | --- | --- | --- | --- |
| SYN-BEN-301 | Name mismatch | Beneficiary identity/detail discrepancy unresolved | Compare submitted name with verified beneficiary record | Do not bypass validation; verified correction and revalidation required | Beneficiary Maintenance | SYN-BENEFICIARY/BV-NAME |
| SYN-BEN-302 | Account format invalid | Account-reference syntax fails synthetic format check | Identify format failure against the fictional reference convention | Do not bypass validation; verified correction and revalidation required | Beneficiary Maintenance | SYN-BENEFICIARY/BV-FORMAT |

These checks differ: a well-formed account reference may still have a name
mismatch. Passing either check alone establishes neither payment approval nor settlement.
```

### SYN-WIRE-RECALL/WR-REQUEST

Estimated tokens: 324

```json
{
  "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08",
  "document_id": "SYN-WIRE-RECALL",
  "document_title": "Wire Recall SOP",
  "document_version": "1.0.0",
  "effective_date": "2026-10-28",
  "document_type": "sop",
  "source_path": "data/knowledge/documents/wire_recall_sop.md",
  "section_id": "WR-REQUEST",
  "section_heading": "WR-REQUEST — Prepare the recall request and case",
  "chunk_index": 0
}
```

```markdown
## WR-REQUEST — Prepare the recall request and case

**section_id: WR-REQUEST**

Required details: payment ID, original instruction reference, rail, original
amount and currency, synthetic sender and beneficiary references, requester
reference, requester-verification reviewer/outcome, reason for recall, last
confirmed payment status, status timestamp/source, related case references, and
the proposed case owner. Record these using `SYN-EXCEPTION/EX-EVIDENCE`.

1. Create or link one recall case and preserve the original instruction unchanged.
2. Record the required details and supporting evidence; identify missing items.
3. Ask the Wire Operations supervisor to review completeness and duplicate risk.
4. Record a simulated request reference only when that review is complete.
   This is an educational case record, not transmission to a bank or network.
5. Assign an owner and record the next follow-up checkpoint agreed by that owner.
   This SOP establishes no universal elapsed-time deadline.

Example: fictional requester `SYN-REQUESTER-11` asks to recover `SYN-WIRE-1001`
for USD 125.00 after release. Case `SYN-CASE-3001` links the release event and
requester verification. The analyst prepares a recall request; no recovery is
booked and no payment is executed by this procedure.
```
