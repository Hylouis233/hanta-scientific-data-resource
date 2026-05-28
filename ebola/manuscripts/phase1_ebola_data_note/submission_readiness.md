# Submission readiness checklist

Status: internal-review complete; journal submission requires external review and source snapshot work.

## Completed in repository

- Reproducible source registry for Phase 1 Ebola sources.
- Raw HDX resources fetched, checksummed, DVC-tracked, and pushed to local MinIO remote.
- Raw validation, normalization, outbreak metadata, Rt proxy, and evaluation entrypoints are runnable.
- Field inventory and manuscript-ready field semantics audit are available.
- Manuscript v0.1 contains abstract, background, data sources, processing workflow, descriptive Rt baseline, limitations, reproducibility, and data/figure availability statements.
- Non-causal claim guardrails are explicit in methods, Rt outputs, captions, and checklist language.

## Not yet journal-submission ready

- Target journal format still needs final selection, but submission metadata templates are drafted in `submission_metadata.md`.
- Author list, acknowledgements, funding, conflicts of interest, and ethics statement templates are drafted in `submission_metadata.md`.
- HDX license and citation language need final confirmation against target journal requirements; source snapshot tasks are enumerated in `source_snapshot_checklist.md`.
- WHO anchor pages need immutable snapshots or archived access-date evidence.
- External epidemiological review is still required for case-definition semantics and field interpretation.
- Final figure polish is pending; current figures support internal review, not final production layout.
- Row-level source URL retention in processed outputs is not yet implemented.

## Submission gate

The manuscript can be treated as submission-ready only after all items below are checked:

- [ ] Target journal selected; draft metadata template exists in `submission_metadata.md`.
- [ ] Author and contribution list confirmed using `submission_metadata.md`.
- [ ] HDX license/citation text finalized using `source_snapshot_checklist.md`.
- [ ] WHO anchors archived or removed from manuscript-critical claims using `source_snapshot_checklist.md`.
- [ ] Field semantics reviewed by an epidemiology domain reviewer.
- [ ] Final figures regenerated with publication captions.
- [ ] Data availability statement updated with public repository or archive location.
- [ ] Reproducibility commands run from a clean checkout.
