# Zemazap CEO AI-agent TODO

Updated: 2026-08-23.

## Mission

Coordinate the remaining business, legal, catalogue, cloud and provider work and
produce an evidence-backed launch recommendation. Work from the latest
`origin/main`. The repository engineering baseline, local tests, browser E2E and
native PostgreSQL rehearsal are already complete.

You may prepare content, configure staging with authorized access, run checks and
document results. You must not invent owner data, approve legal/accounting
decisions, expose credentials, enable live payments/fiscalization, or authorize a
production launch on behalf of the CEO.

Read these files before acting:

1. `docs/ceo-launch-master-plan-ru.md`
2. `TODO.md`
3. `docs/launch-readiness-checklist.md`
4. `docs/yandex-cloud-production-runbook.md`
5. `docs/alfa-bank-and-fiscalization-runbook.md`
6. `.env.example` and `backend/.env.example`

## Mandatory operating rules

- Track every item as `READY`, `IN_PROGRESS`, `BLOCKED_BY_CEO`,
  `BLOCKED_BY_PROVIDER`, `FAILED`, or `DONE`.
- Ask for missing facts; never replace them with plausible placeholders.
- Never paste secrets, customer PII, `.env` contents, database dumps or private
  legal files into chat, Git commits, screenshots or logs.
- Put production secrets in Yandex Lockbox. Use separate staging and production
  credentials and resources.
- Never run `seed_demo` against production.
- Keep payment, fiscalization and public indexing disabled until their explicit
  acceptance gates pass.
- Do not modify application code merely to bypass `check --deploy`,
  `check_launch_content`, CI or another release gate.
- Do not delete or overwrite production data. Before migrations/imports, create a
  verified backup and record the rollback procedure.
- Any code/configuration change requires a commit on `main`, a green CI run, and a
  new acceptance SHA. Never force-push `main`.

## 1. Collect CEO decisions

- [ ] Obtain the legal seller type, legal/public name, INN, OGRN/OGRNIP, optional
  KPP, legal address and actual address.
- [ ] Obtain bank name, settlement account, correspondent account, BIK, tax mode
  and exact VAT wording approved by the accountant.
- [ ] Obtain the public region, pickup/address text, business hours, public phone
  label and `tel:` value, order email, claims email and approved messenger links.
- [ ] Record the production/staging domains, domain registrant and account owner.
- [ ] Record the Yandex Cloud organization/billing owner, budget alert recipients,
  region, RPO/RTO and technical owner.
- [ ] Record the people who will hold owner, manager, accountant and technical
  administrator roles.
- [ ] Obtain the catalogue source owner, update frequency, price/stock semantics,
  image rights and a dated source export.
- [ ] Obtain lawyer-approved legal texts and the lawyer's decision on the required
  Roskomnadzor notification and data-retention policy.
- [ ] Obtain Alfa-Bank and KKT/OFD contacts, contract status and authorized
  credential-transfer mechanism. Do not request credentials in chat.
- [ ] Obtain the CEO-approved brand/SEO text and the intended indexing date.

Deliverable: a sanitized input register listing each field, its owner, approval
date and evidence location. Mark missing facts `BLOCKED_BY_CEO`.

## 2. Prepare legal and public content in staging

- [ ] Enter verified values in Django Admin `SiteSettings` and
  `LegalEntitySettings`; leave `is_ready_for_production` false during drafting.
- [ ] Create versioned records for all seven `LegalDocument.kind` values:
  `privacy_policy`, `privacy_consent`, `terms`, `delivery`, `payment`, `warranty`,
  and `returns`.
- [ ] Ensure each body is substantive, contains no draft/placeholder language and
  has written legal approval before publication.
- [ ] Match the published privacy-policy, consent and terms versions to the
  configured version values. Preserve previous versions for consent evidence.
- [ ] Publish only approved versions and run:

  ```powershell
  .\.venv\Scripts\python.exe backend\manage.py check_launch_content
  ```

- [ ] Inspect the public legal pages, contacts, footer, order consent links,
  `/bank-review`, sitemap and robots on desktop and mobile.
- [ ] Set `is_ready_for_production` only after the CEO confirms every public field.

Evidence: sanitized screenshots, command output, document version list, approval
references and unresolved legal questions. The AI agent must not provide final
legal approval.

## 3. Prepare and validate the catalogue

- [ ] Preserve the untouched source export and create a cleaned CSV/XLSX copy.
- [ ] Require `name`/`название` and `article`/`артикул`. Where available include
  OEM, brand, model, category, manufacturer, price, availability, stock, delivery,
  condition, photo kind, warranty, return and marking fields.
- [ ] Detect duplicate normalized articles, missing names, zero/stale prices,
  inconsistent availability, unsupported values and unlicensed images.
- [ ] Import a small sample into staging through the staff-only price import,
  record imported/skipped counts and verify selected items against the source.
- [ ] Test search, filters, categories, product details, photos, cart and request
  snapshots using the sample.
- [ ] Back up staging, import the full cleaned file, then repeat control totals and
  selected-item comparisons.
- [ ] Test a corrected re-import and document how a bad import is rolled back.
- [ ] Confirm no demo catalogue remains in production and `seed_demo` was not run.

Evidence: source checksum, sanitized validation report, row counts, rejected-row
list, control sample, screenshots and rollback result.

## 4. Provision external services

- [ ] Register/configure the domains and DNS under the authorized owner.
- [ ] Create separate Yandex Cloud staging and production folders/resources by
  following `docs/yandex-cloud-production-runbook.md`.
- [ ] Configure VPC/security groups, private Managed PostgreSQL, private Object
  Storage, Lockbox, Container Registry, VM, ALB, Certificate Manager, WAF and
  Monitoring.
- [ ] Enable PostgreSQL backups, logical `pg_dump`, bucket versioning/lifecycle,
  budget alerts and service alerts.
- [ ] Configure GitHub OIDC federation; do not add long-lived service-account JSON
  keys to GitHub Secrets.
- [ ] Verify ALB reaches only Caddy `:8080`, while Django, Next.js and PostgreSQL
  are not directly public.
- [ ] Create application roles with `bootstrap_roles`, create named admin users and
  assign least-privilege groups.
- [ ] Restore a backup into a separate database and record counts and duration.

Evidence: non-secret resource IDs, architecture snapshot, sanitized access matrix,
HTTPS/health results, alert test and restore report.

## 5. Configure staging integrations

- [ ] Obtain Alfa-Bank test credentials through the approved secret channel and
  store them outside Git.
- [ ] Submit the public site and `/bank-review` for bank review and record the case
  ID/status.
- [ ] Register the protected payment callback and verify server-to-server status
  reconciliation.
- [ ] Configure the selected KKT/OFD staging path and confirm how the application
  receives the final receipt status. `pending_confirmation` is not success.
- [ ] Configure SMTP and any legally approved Telegram channel; verify PII-safe
  messages and logs.
- [ ] Execute successful payment, failed/cancelled payment, duplicate callback,
  invalid amount, unknown order, full refund, partial refund, sale receipt, refund
  receipt and temporary-provider-failure retry scenarios.
- [ ] Reconcile provider, application, KKT and OFD records for each scenario.

Evidence: redacted transaction/reference IDs, status timeline, receipt status,
screenshots from provider consoles and a discrepancy list. Never include tokens,
card data or customer PII.

## 6. Run the release gate

- [ ] Record the candidate commit SHA and verify GitHub CI is green.
- [ ] Run the release commands in `TODO.md`, including `check --deploy`, migration
  drift, backend tests, audits, typecheck, build and browser E2E.
- [ ] Run the external smoke check against staging.
- [ ] Complete every item in `docs/launch-readiness-checklist.md`.
- [ ] Verify scheduler work, notification backlog, payment/fiscal failures,
  retention dry-run, health, 5xx monitoring and PII-safe logs.
- [ ] Perform and document backup/restore and rollback using the candidate SHA.
- [ ] Confirm the same SHA and configuration are proposed for production.

If any P0 item fails, the recommendation must be `NO-GO`; do not downgrade it to
a warning.

## 7. Prepare the CEO decision packet

Produce one concise report with:

- candidate SHA, domains and acceptance timestamp;
- status table for every P0/P1 item;
- links to CI, deployment and evidence artifacts;
- approved legal-document versions and catalogue control totals;
- cloud/backup/monitoring status;
- payment/refund/fiscal reconciliation summary;
- named operational owners and escalation contacts;
- open risks, rollback trigger and rollback owner;
- a final recommendation: `GO`, `NO-GO`, or `BLOCKED`, with reasons.

Only the CEO may convert a `GO` recommendation into launch authorization. Record
their decision, authorized SHA, time window and indexing/payment/fiscal flags.

## 8. Production and post-launch follow-up

- [ ] Create a pre-deploy backup and deploy the exact authorized SHA.
- [ ] Run production smoke before enabling live payment/fiscal flags.
- [ ] Open indexing only after final production content/legal review.
- [ ] Manually trace the first real order through payment and final fiscal receipt.
- [ ] Monitor health, 5xx, database, disk, scheduler, payments, receipts and
  notification backlog closely for the first 24 hours.
- [ ] Reconcile payments and receipts daily for the first week.
- [ ] Test restore within one month and schedule monthly restore exercises.
- [ ] Review WAF/throttles, retention, permissions and incident findings after the
  first stable month.

## Status report template

```text
Candidate SHA:
Environment/domain:
Overall status: READY | BLOCKED | NO-GO

DONE:
- ...

BLOCKED_BY_CEO:
- item / exact missing decision / requested date

BLOCKED_BY_PROVIDER:
- item / provider / case ID / next follow-up

FAILED:
- check / evidence / owner / remediation

RISKS:
- likelihood / impact / mitigation / owner

RECOMMENDATION:
- GO or NO-GO, with reasons

NEXT THREE ACTIONS:
1. ...
2. ...
3. ...
```
