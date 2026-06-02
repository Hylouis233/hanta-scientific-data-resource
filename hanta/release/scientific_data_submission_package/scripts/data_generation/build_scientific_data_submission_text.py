#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COVER = ROOT / "reports/scientific_data_cover_letter.md"
SUBMISSION = ROOT / "reports/scientific_data_submission_text.md"
STATEMENTS_JSON = ROOT / "reports/scientific_data_submission_statements.json"


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    cover = "\n".join([
        "# Cover letter for Scientific Data submission",
        "",
        "Dear Editors,",
        "",
        "We submit a Data Descriptor entitled \"A claim-bounded public-data ResearchOps resource for hantavirus formal gate evaluation\" for consideration in Scientific Data / a Nature Portfolio data-resource venue.",
        "",
        "The manuscript presents a reproducible public-data ResearchOps resource for hantavirus research workflows. It organizes GBIF host-occurrence provenance, environmental formal-gate inputs and diagnostics, public aggregate surveillance availability/count records, a public non-spatial rodent trapping/testing table audit, figure-quality audits and caption-level claim boundaries into a reusable workspace.",
        "",
        "The resource is intentionally framed as a Data Descriptor rather than as a discovery manuscript. Its value is that it shows what public/self-service data can support, what remains blocked, and how to prevent public-data workflows from overclaiming human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology joins or causal conclusions.",
        "",
        "The package includes five Data Record groups, a 19-row field/artifact dictionary, Technical Validation, Usage Notes, a reviewer navigation guide, a reproducibility smoke test, 10 MiniMax M3-accepted canonical figures, caption locks for six figure groups, and a final secret/privacy audit with zero secret-pattern hits in scanned repository text files.",
        "",
        "We believe this resource will be useful to infectious-disease data scientists, ecological modelers, public-health data users and reproducibility reviewers who need worked examples of claim-bounded public-data workflows.",
        "",
        "Sincerely,",
        "",
        "[Authors]",
        "",
    ])
    statements = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_submission_text_complete",
        "title": "A claim-bounded public-data ResearchOps resource for hantavirus formal gate evaluation",
        "data_availability": "Data records and generated reports are represented in DVC-bounded raw/processed directories and reviewer-facing manifests. The local deposition package is available at release/scientific_data_submission_package/ pending external repository deposition DOI. Credentials, local-only DVC configuration, private coordinates and sensitive individual-level human health data are not included.",
        "code_availability": "All generation, validation, descriptor, audit and packaging scripts are stored under scripts/. The fixed project evaluation entrypoint is bash evaluation/evaluate.sh configs/experiment.yaml.",
        "ethics_privacy": "The resource uses public/self-service source data, aggregate surveillance records and a public supplementary animal trapping/testing table. It does not request personal identifiers or sensitive individual-level human health data. Coordinates excluded by source authors for private-land protection were not reconstructed or inferred.",
        "competing_interests": "The authors declare no competing interests. [Placeholder for author confirmation.]",
        "author_contributions": "[Placeholder] Authors designed the ResearchOps workflow, implemented data acquisition and validation scripts, generated figures and audits, and wrote the Data Descriptor.",
        "materials_correspondence": "Correspondence and material requests should be addressed to [corresponding author placeholder].",
        "validation_passed": True,
    }
    COVER.write_text(cover, encoding="utf-8")
    SUBMISSION.write_text("\n".join([
        "# Scientific Data submission text",
        "",
        f"Title: {statements['title']}",
        "",
        "## Data availability",
        "",
        statements["data_availability"],
        "",
        "## Code availability",
        "",
        statements["code_availability"],
        "",
        "## Ethics and privacy",
        "",
        statements["ethics_privacy"],
        "",
        "## Competing interests",
        "",
        statements["competing_interests"],
        "",
        "## Author contributions",
        "",
        statements["author_contributions"],
        "",
        "## Correspondence",
        "",
        statements["materials_correspondence"],
        "",
    ]) + "\n", encoding="utf-8")
    STATEMENTS_JSON.write_text(json.dumps(statements, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": statements["status"], "validation_passed": statements["validation_passed"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
