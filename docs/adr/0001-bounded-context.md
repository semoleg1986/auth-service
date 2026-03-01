# ADR-0001: Bounded Context For Auth Service

## Status
Accepted

## Date
2026-02-28

## Context
Platform consists of multiple services (`auth`, `user-children`, `admin`, `notification`, BFFs).
Auth responsibilities must remain isolated to avoid leakage of foreign business logic.

## Decision
`auth-service` owns:
- user account credentials and status
- login/register/refresh/logout flows
- session lifecycle for refresh tokens
- role assignment and role listing
- JWT issuing and JWKS publishing

`auth-service` does not own:
- children or stories domain operations
- cross-service admin orchestration
- notifications delivery

Integration rule:
- external services use API/JWKS/events only
- direct storage access by external services is prohibited

## Consequences
- clear ownership of authentication and authorization primitives
- independent release cadence for auth
- stable API/JWKS contracts for consumers

