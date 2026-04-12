# Security Baseline (2026-oriented)

This project follows strict secure-by-default principles for MCP workloads.

## Implemented controls

- Outbound HTTP tool allows **HTTPS only**
- Optional outbound host allowlist (`OMNI_MCP_ALLOWED_OUTBOUND_HOSTS`)
- Outbound response size and timeout limits
- No shell-execution tool exposed
- Safe file-read tool with path traversal prevention
- Structured JSON logs for SIEM pipelines
- Container runs as non-root user
- Helm defaults include:
  - non-root pod/container security context
  - dropped Linux capabilities
  - read-only root filesystem
  - service account token automount disabled

## Recommended production controls

- Enforce mTLS between client and server
- Use OIDC/JWT-based service auth instead of shared secrets
- Store secrets only in dedicated secret manager (not in values files)
- Add network policies to restrict ingress/egress
- Add admission policies (Kyverno/OPA) for pod hardening checks
- Sign images and verify provenance (e.g., Sigstore/Cosign, SLSA-aligned CI)
- Generate SBOM and run continuous dependency scanning
- Add runtime threat detection and audit logging retention policies

## Slack integration security model

Slack verification and request normalization should happen in the separate client service.
The MCP server should only accept authenticated requests from that client.
