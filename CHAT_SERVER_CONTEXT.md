# CClub Chat Server + Stickerpicker Context

This file consolidates the operational context for Matrix chat infrastructure and Stickerpicker integration.

## Repositories and Roles

- `~/Documents/GitHub/ccawmunity`
  - Matrix community bot and related services.
  - Has its own `docker-compose.yml` with bot, redis, office-presence, stickerpicker.
- `~/Documents/GitHub/server-rebuild`
  - Core infrastructure stack (Caddy, Synapse, Element, LDAP, MediaWiki, Vaultwarden, etc.).
  - Caddy reverse proxy lives here.
- `~/Documents/GitHub/stickerpicker`
  - Upstream Maunium Stickerpicker source (web assets, packs, tooling).
- `~/stickerpicker-deploy`
  - Deployment helper artifacts (`Dockerfile`, `index.json`, guide text).

## Current Routing and Network Model

In `server-rebuild`:

- `containers/Caddy/Caddyfile` includes:
  - `redir /stickers /stickers/`
  - `handle_path /stickers/* { reverse_proxy stickerpicker:5000 }`
- `containers/docker-compose.yml` defines a `caddy` network with explicit name:
  - `networks.caddy.name: caddy`

Implication:

- Any Stickerpicker container reachable as `stickerpicker` on Docker network `caddy` can be served publicly at:
  - `https://cclub.cs.wmich.edu/stickers/`
- No host port publishing is required for Stickerpicker.

## Security Constraints and Goals

- No additional host ports should be opened for Stickerpicker.
- Prefer internal-only container exposure via Docker networking + Caddy reverse proxy.
- Minimize blast radius with container hardening.
- Avoid downtime for existing services (Synapse/Element/Caddy/etc.).
- Do not stop/restart containers unless explicitly approved.

## Stickerpicker Integration Design

Recommended production pattern:

1. Run Stickerpicker as an internal service (no `ports:` mapping).
2. Attach it to external Docker network `caddy`.
3. Ensure DNS name `stickerpicker` is resolvable on that network.
4. Serve only through Caddy `/stickers/*` route.

## Changes Applied in `ccawmunity/docker-compose.yml`

Stickerpicker service has been prepared for production hardening and cross-stack routing:

- Added `caddy` external network attachment.
- Added explicit alias `stickerpicker` on `caddy` network.
- Removed unnecessary writable volume mount from Stickerpicker service.
- Added hardening controls:
  - `read_only: true`
  - `tmpfs: /tmp`
  - `security_opt: no-new-privileges:true`
  - `cap_drop: [ALL]`
  - `pids_limit: 128`

Also added top-level external network:

- `networks.caddy.external: true`

## Why This Works Without Opening Ports

- Caddy and Stickerpicker communicate over Docker network `caddy`.
- Public traffic terminates at Caddy (already exposed on 80/443).
- Stickerpicker remains private to Docker networking.

## Zero-Downtime Rollout Plan

1. Build Stickerpicker image.
2. Start/recreate only Stickerpicker service.
3. Verify internal reachability from Caddy network:
   - `curl http://stickerpicker:5000/` from a container on `caddy`.
4. Verify public route:
   - `curl -I https://cclub.cs.wmich.edu/stickers/`
5. Keep other services untouched.

## Validation Checklist

- `docker compose config` passes.
- `docker network inspect caddy` shows Stickerpicker attached.
- Caddy route `/stickers/` returns HTTP 200.
- Existing paths (`/chat`, `/_matrix`, `/wiki`, etc.) remain healthy.

## Operational Notes

- The `ccawmunity` compose currently uses absolute build paths (e.g., `/home/sysadmin/stickerpicker`).
- If deploying from a different host path, update build contexts accordingly.
- Keep Stickerpicker content static-only; avoid mounting extra writeable paths unless required.

