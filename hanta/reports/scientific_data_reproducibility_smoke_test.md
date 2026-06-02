# Scientific Data reproducibility smoke test

Status: scientific_data_reproducibility_smoke_test_passed.

| Command | Passed | Return code | Stdout tail |
| --- | --- | ---: | --- |
| `python scripts/data_generation/build_scientific_data_resource_index.py` | true | 0 | {"data_record_count": 5, "field_dictionary_rows": 19, "validation_passed": true} |
| `python scripts/data_generation/build_scientific_data_descriptor_package.py` | true | 0 | {"descriptor": "manuscripts/hanta_scientific_data_descriptor.md", "records": 5, "validation_passed": true} |
| `python scripts/data_generation/audit_scientific_data_descriptor_readiness.py` | true | 0 | {"failed_checks": 0, "validation_passed": true} |
| `bash evaluation/evaluate.sh configs/experiment.yaml` | true | 0 |  |

This smoke test exercises the reviewer-facing resource index, Data Descriptor package generation, descriptor readiness audit, and fixed project evaluation.

