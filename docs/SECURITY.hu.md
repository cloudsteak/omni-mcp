# Biztonsági Alapok (HU)

A projekt biztonságos alapbeállításokra épül.

## Megvalósított kontrollok

- Csak `HTTPS` kimenő URL engedélyezett
- Opcionális host allowlist
- Kimenő válaszméret/időtúllépés limit
- Nincs shell futtató tool
- Fájl olvasásnál path traversal védelem
- Konténerben non-root futtatás
- Helm default: read-only root FS, capability drop, token automount tiltás

## Erősen ajánlott éles környezetben

- mTLS kliens és szerver között
- OIDC/JWT alapú hitelesítés shared secret helyett
- Secret manager használat
- Kubernetes NetworkPolicy
- Admission policy (OPA/Kyverno)
- Kép-aláírás és provenance ellenőrzés
- SBOM + folyamatos dependency scan
