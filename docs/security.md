# Security And Release Checklist

Before publishing this repository, run the release check and manually inspect the final tree.

## Never Commit

- `.env`, `.env.local`, or any file containing real credentials.
- API keys, notification tokens, email passwords, broker credentials, or account identifiers.
- Holdings lists, trade records, broker exports, screenshots, or statements.
- Local databases, raw market-data bundles, vendor downloads, cache files, and generated outputs.
- Proprietary strategy names, thresholds, filters, or backtest reports.

## Recommended Layout

- Public repository: framework code, synthetic sample data, generic tests, and documentation.
- Private repository: strategy modules, private configuration, real datasets, generated reports, and notification credentials.

## Local Check

```powershell
.\scripts\check_release.ps1
```

The scanner catches common credential formats and suspicious key assignments. It is not a substitute for manual review.
