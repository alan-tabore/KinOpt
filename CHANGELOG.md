# Changelog

## 1.1.0 - 2026-10-16

- Run independent batch jobs in isolated concurrent processes with a global
  worker budget and per-job cancellation.
- Preview and map imported columns, convert common units, and validate every
  selected experimental file before replacing loaded data.
- Report fit, validation, overall, and per-experiment errors; show detailed
  multi-start parameter stability and parameter-bound review warnings.
- Persist live batch progress and migrate complete legacy text results into
  structured comparisons and exports.
- Add optional representative two-stage fitting and cache repeated Vyazovkin
  integral terms, with reproducible performance benchmarks.
- Split application metadata from the main Qt window, close SQLite connections
  deterministically, and use `pyproject.toml` as the dependency source.
