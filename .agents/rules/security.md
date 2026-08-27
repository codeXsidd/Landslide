# NER-SAGE Security Rules

## Authentication

- All API endpoints (except `/health` and `/api/v1/auth/login`) require a valid JWT.
- JWTs are signed with `JWT_SECRET` from environment — never hardcoded.
- JWT expiry: configurable via `JWT_EXPIRE_MINUTES` (default 1440 = 24 hours).
- Refresh tokens are out of scope for MVP; re-login on expiry.

## Authorization — Roles

| Role | Permissions |
|------|-------------|
| `viewer` | Read-only: risk, evidence, map, reports |
| `analyst` | viewer + submit citizen reports + run simulations |
| `responder` | analyst + approve/reject AI recommendations |
| `admin` | All permissions + user management + system config |

- The FastAPI `get_current_user` dependency must be applied to every route.
- Role checks use the `require_role` dependency.
- Decision approval endpoints require `responder` or `admin`.

## Input Validation

- All API inputs validated via Pydantic schemas before reaching service layer.
- GeoJSON coordinates must be validated inside the NER bounding box.
- File uploads (citizen reports) must:
  - Validate MIME type (JPEG, PNG, MP4 only)
  - Limit size (images: 10 MB, videos: 50 MB)
  - Be stored in MinIO — never in MongoDB or the filesystem
  - Be virus-scanned in production (stub in development)

## Audit Logging

- Every write operation (evidence submission, decision, simulation, alert) must create an audit record.
- Audit record must include: `user_id`, `action`, `resource_type`, `resource_id`, `timestamp`, `ip_address`, `result`.
- Audit records are append-only. Never delete or update audit records.
- Use the `audit_logger` from `app/security/audit.py` — never write raw dicts to audit_logs.

## No Autonomous Critical Actions

- The system must NEVER automatically:
  - Issue a public emergency warning
  - Close a road
  - Dispatch a response team
  - Evacuate a village
- All of the above require a human decision record with `approved_by` field.

## Secret Management

- NEVER commit `.env` to version control.
- NEVER log secret values (API keys, passwords, JWT tokens).
- NEVER return JWT secret or DB credentials in any API response.
- Use `.env.example` as the template; actual values stay in `.env`.

## Production Notes (Post-Hackathon)

- Enable HTTPS (TLS termination at nginx).
- Enable MongoDB authentication with strong passwords.
- Enable Neo4j authentication.
- Rate limit all public endpoints via Redis.
- Add CSRF protection for state-changing endpoints.
- Regular dependency security audits (`pip-audit`, `npm audit`).
