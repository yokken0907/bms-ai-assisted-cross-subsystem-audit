# Prospective Transfer Audit Protocol — external hash registration v1.0.1

Registration date: 2026-10-07
Protocol lineage: foxBMS retrospective case -> M0 -> M1 -> M2 -> M3 -> pre-registration completeness correction v1.0.1
Target-pool state at registration: NOT CONSTRUCTED
Real target state at registration: NOT SELECTED / NOT CLONED / NOT DEFECT-INSPECTED
Issue/PR/fix reconnaissance on a real target before registration: NONE

## Why v1.0.1 supersedes local v1.0.0

Local v1.0.0 referenced four frozen control-schema files under `data/` that were absent from the M3 package. This was discovered before target-pool construction or target inspection. v1.0.1 adds those previously referenced schemas. Primary gates, target-selection queries/rules, B1 model/lenses, terminal technical categories, transfer outcomes, non-claims, and claim ceilings are unchanged.

## Cryptographic commitments

Main protocol SHA-256:
`d3ef7b043ba329fa13f370611c8bc24d0f5d65451e203131abf668beccd5d4ca`

Complete v1.0.1 package ZIP SHA-256:
`7a30ab05bcbac5adaf5e9ea1d4f6857f0e4100ff95ed6c86096b30f374b7d5f3`

## File-level SHA-256 manifest

```
4674e43d969ae3c83f4d1ecd5d268dcb73e9437185c124b044b89a87a52afc6a  ./B1_CANDIDATE_GENERATION_LENS_SET_FROZEN_v1.0.0.md
a8e96abe43d84a3a3c1bcddddf0cc33a2ddf0baba4240ecc793e24ed43c85e43  ./CONTAMINATION_AND_DEVIATION_POLICY_FROZEN_v1.0.0.md
0acd12890d17b39745a4d2b90c7882186997d37c2bc46b8dcafded0d92eb0b9e  ./FREEZE_CHECKLIST_v1.0.1.md
0cf8292092eb5e4828d4dc4ff2bccad596817c742f7d2cb63db21a41f6192cb3  ./M3B_PREREGISTRATION_COMPLETENESS_AUDIT_v1.0.1.md
27091ab6019ee7737f61efb4c3aae7c1ba180039f0664fcdc9ff91761a26f48f  ./PRE_REGISTRATION_CORRECTION_NOTE_v1.0.1.md
d3ef7b043ba329fa13f370611c8bc24d0f5d65451e203131abf668beccd5d4ca  ./PROSPECTIVE_TRANSFER_AUDIT_PROTOCOL_LOCALLY_FROZEN_v1.0.1.md
59b1376a0329877f61eb2704b37b7a12b37ba66bae7923927f2da9bffe451111  ./README_M3_v1.0.0.md
4677605d3205982ebdc0cd6c749109c8c7827d12c72ae2e32fb769bc3266afce  ./SCOPE_FREEZE.md
004b5d9b555e391101af76fb2683d9f67128d681683c373c46cad597e3fffbc5  ./TARGET_POOL_AND_SELECTION_RULE_FROZEN_v1.0.0.md
a63fbb9f47ba10516483a379fb7b07f360c5b7239f4d08bd2eed103189d050e3  ./data/CANDIDATE_RECORD_SCHEMA_v1.0.0.json
62dbf04187154bd2212ce8bbf2b3b5a07f7c7f88e65001d0a14d91871eb944e5  ./data/CONTAMINATION_LOG_SCHEMA_v1.0.0.csv
fb89d85db84a0298bcdb93d217dc1035c16d75caf2a4de43c44696857a49c8ab  ./data/DEVIATION_LOG_SCHEMA_v1.0.0.csv
b683c565d8652253b9f217c0312f575bb8fe38f97e2a244fcbbe364af3fa8ea2  ./data/OUTCOME_AXES_v1.0.0.csv
```

## Interpretation

This registration is a pre-outcome cryptographic commitment to the complete v1.0.1 package. Any later amendment must use a new version/hash and be logged under the frozen deviation policy. The registration itself does not claim detector performance or bug yield.
