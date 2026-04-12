# omni-mcp dokumentáció (HU)

Az `omni-mcp` egy általános célú, Python alapú MCP szerver váz, biztonságos alapbeállításokkal.

## Fázisok állapota

1. Alap szerver helyi futtatással: **kész**
2. Külön kliens (`omni-studio` repo): **tervezett / előkészített szerződéssel**
3. Docker változat: **kész**
4. Kubernetes kompatibilitás + Helm alap: **kész (baseline)**

## Főbb képességek

- Tool-ok, resource-ok és prompt-ok MCP-n keresztül
- Kapcsolható beépített skill-ek
- Strukturált JSON logolás
- Szigorú alap biztonsági guardok (HTTPS-only, limitált kimenő kérés, path védelem)

## Fontos fájlok

- `README.md` (EN)
- `docs/ARCHITECTURE.md` (EN)
- `docs/SECURITY.md` (EN)
- `docs/CLIENT_CONTRACT.md` (EN)

Magyar részletek:
- [Architektúra (HU)](ARCHITECTURE.hu.md)
- [Biztonság (HU)](SECURITY.hu.md)
- [Kliens szerződés (HU)](CLIENT_CONTRACT.hu.md)
