# Claude turn accounting (v4, all 44 cells, from surviving session transcripts)

## Per model/config means

| model | config | n | mean turns | mean calls | recon_src | recon_lib | sanka_cli | overlay_read | overlay_adopt | oracle_probe | harness_write | implement | target_probe | verify | unknown_run | env | cleanup | plan | other | mean 1st target_app | mean verify runs | cap hits |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus 4.8 | alone | 11 | 50.9 | 49.9 | 7.8 | 2.4 | 0 | 0 | 0 | 10 | 9.9 | 9.1 | 0.9 | 3.7 | 3.5 | 0.3 | 0.4 | 0 | 2 | 28.6 | 3.7 | 4 |
| Claude Opus 4.8 | with-sanka | 11 | 54 | 54.9 | 11.7 | 2.6 | 3.1 | 1.4 | 0 | 8.5 | 7.2 | 7.2 | 0.9 | 4.1 | 4.5 | 1.5 | 0.7 | 0 | 1.5 | 33.9 | 4.1 | 3 |
| Claude Sonnet 5 | alone | 11 | 59.7 | 67 | 16.9 | 7.8 | 0 | 0 | 0 | 12.2 | 7.8 | 10 | 0.9 | 3.5 | 3.1 | 1.7 | 0.4 | 0 | 2.7 | 44.4 | 3.5 | 7 |
| Claude Sonnet 5 | with-sanka | 11 | 59.7 | 66.7 | 15.1 | 7.5 | 0.8 | 0.3 | 0 | 15 | 7.5 | 6.8 | 1.5 | 4.5 | 2 | 3.8 | 1 | 0 | 0.9 | 47 | 4.5 | 9 |

## Per cell

| cell | turns | calls | recon_src | recon_lib | sanka_cli | overlay_read | overlay_adopt | oracle_probe | harness_write | implement | target_probe | verify | unknown_run | env | cleanup | plan | other | 1st write | 1st target_app | verify runs | 1st all-pass | verify after | last signal | cap | frozen | result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 001-opus48-alone | 61 | 60 | 5 | 12 | 0 | 0 | 0 | 15 | 14 | 3 | 0 | 8 | 3 | 0 | 0 | 0 | 0 | 36 | 37 | 8 | None | 0 | failures-present | Y | Y | PASS |
| 002-opus48-alone | 36 | 35 | 4 | 1 | 0 | 0 | 0 | 2 | 17 | 6 | 1 | 3 | 0 | 0 | 0 | 0 | 1 | 18 | 22 | 3 | None | 0 | unclear |  | Y | PASS |
| 003-opus48-alone | 45 | 44 | 5 | 0 | 0 | 0 | 0 | 11 | 4 | 9 | 0 | 10 | 5 | 0 | 0 | 0 | 0 | 22 | 23 | 10 | None | 0 | unclear |  | Y | PASS |
| 004-opus48-alone | 60 | 59 | 10 | 0 | 0 | 0 | 0 | 10 | 8 | 12 | 5 | 5 | 9 | 0 | 0 | 0 | 0 | 17 | 18 | 5 | None | 0 | failures-present |  | Y | PASS |
| 005-opus48-alone | 61 | 60 | 4 | 1 | 0 | 0 | 0 | 11 | 19 | 12 | 0 | 3 | 10 | 0 | 0 | 0 | 0 | 15 | 27 | 3 | None | 0 | unclear | Y | Y | PASS |
| 006-opus48-alone | 61 | 60 | 8 | 0 | 0 | 0 | 0 | 13 | 11 | 20 | 0 | 3 | 5 | 0 | 0 | 0 | 0 | 24 | 25 | 3 | None | 0 | unclear | Y | Y | PASS |
| 007-opus48-alone | 61 | 60 | 13 | 0 | 0 | 0 | 0 | 18 | 6 | 17 | 0 | 1 | 0 | 1 | 1 | 0 | 3 | 26 | 46 | 1 | None | 0 | unclear | Y | Y | PASS |
| 008-opus48-alone | 32 | 31 | 4 | 2 | 0 | 0 | 0 | 12 | 3 | 4 | 0 | 3 | 2 | 0 | 0 | 0 | 1 | 20 | 21 | 3 | 27 | 2 | unclear |  | Y | PASS |
| 009-opus48-alone | 52 | 51 | 6 | 8 | 0 | 0 | 0 | 1 | 12 | 5 | 0 | 0 | 0 | 2 | 2 | 0 | 15 | 29 | 30 | 0 | None | 0 | None |  | Y | PASS |
| 010-opus48-alone | 53 | 52 | 12 | 2 | 0 | 0 | 0 | 12 | 12 | 6 | 2 | 4 | 1 | 0 | 0 | 0 | 1 | 18 | 39 | 4 | None | 0 | failures-present |  | Y | PASS |
| 011-opus48-alone | 38 | 37 | 15 | 0 | 0 | 0 | 0 | 5 | 3 | 6 | 2 | 1 | 3 | 0 | 1 | 0 | 1 | 24 | 27 | 1 | None | 0 | unclear |  | Y | PASS |
| 001-opus48-with-sanka | 50 | 49 | 13 | 2 | 5 | 6 | 0 | 2 | 12 | 6 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 29 | 33 | 1 | None | 0 | unclear |  | Y | PASS |
| 002-opus48-with-sanka | 55 | 54 | 5 | 2 | 4 | 1 | 0 | 9 | 2 | 5 | 0 | 7 | 9 | 7 | 2 | 0 | 1 | 31 | 32 | 7 | None | 0 | failures-present |  | Y | PASS |
| 003-opus48-with-sanka | 53 | 52 | 11 | 0 | 4 | 5 | 0 | 14 | 4 | 7 | 0 | 3 | 3 | 0 | 1 | 0 | 0 | 35 | 36 | 3 | None | 0 | unclear |  | Y | PASS |
| 004-opus48-with-sanka | 42 | 41 | 16 | 0 | 2 | 0 | 0 | 6 | 8 | 3 | 0 | 3 | 1 | 0 | 1 | 0 | 1 | 32 | 33 | 3 | None | 0 | failures-present |  | Y | PASS |
| 005-opus48-with-sanka | 61 | 71 | 17 | 0 | 5 | 1 | 0 | 3 | 18 | 5 | 1 | 7 | 14 | 0 | 0 | 0 | 0 | 53 | 54 | 7 | None | 0 | unclear | Y | Y | PASS |
| 006-opus48-with-sanka | 61 | 69 | 17 | 6 | 2 | 0 | 0 | 13 | 2 | 13 | 4 | 9 | 1 | 0 | 0 | 0 | 2 | 36 | 37 | 9 | 55 | 5 | failures-present | Y | Y | PASS |
| 007-opus48-with-sanka | 60 | 59 | 6 | 10 | 4 | 1 | 0 | 6 | 10 | 8 | 1 | 0 | 0 | 2 | 1 | 0 | 10 | 36 | 43 | 0 | None | 0 | None |  | Y | PASS |
| 008-opus48-with-sanka | 59 | 58 | 13 | 2 | 2 | 0 | 0 | 12 | 4 | 9 | 1 | 3 | 8 | 1 | 2 | 0 | 1 | 30 | 31 | 3 | None | 0 | failures-present |  | Y | PASS |
| 009-opus48-with-sanka | 61 | 61 | 11 | 0 | 2 | 0 | 0 | 14 | 9 | 8 | 2 | 5 | 6 | 2 | 0 | 0 | 2 | 20 | 22 | 5 | 49 | 1 | unclear | Y | N | UNEVALUATED |
| 010-opus48-with-sanka | 34 | 33 | 4 | 0 | 2 | 0 | 0 | 4 | 7 | 5 | 0 | 4 | 2 | 5 | 0 | 0 | 0 | 16 | 17 | 4 | None | 0 | unclear |  | Y | PASS |
| 011-opus48-with-sanka | 58 | 57 | 16 | 7 | 2 | 1 | 0 | 10 | 3 | 10 | 1 | 3 | 4 | 0 | 0 | 0 | 0 | 34 | 35 | 3 | None | 0 | unclear |  | Y | PASS |
| 001-sonnet5-alone | 56 | 55 | 15 | 0 | 0 | 0 | 0 | 9 | 8 | 10 | 3 | 5 | 3 | 0 | 2 | 0 | 0 | 21 | 22 | 5 | None | 0 | unclear |  | Y | PASS |
| 002-sonnet5-alone | 61 | 72 | 22 | 3 | 0 | 0 | 0 | 12 | 7 | 5 | 1 | 6 | 13 | 2 | 0 | 0 | 1 | 49 | 52 | 6 | None | 0 | unclear | Y | Y | PASS |
| 003-sonnet5-alone | 62 | 61 | 16 | 0 | 0 | 0 | 0 | 17 | 2 | 11 | 1 | 7 | 3 | 2 | 2 | 0 | 0 | 32 | 33 | 7 | None | 0 | failures-present |  | Y | PASS |
| 004-sonnet5-alone | 61 | 69 | 17 | 0 | 0 | 0 | 0 | 20 | 6 | 17 | 2 | 3 | 1 | 3 | 0 | 0 | 0 | 36 | 37 | 3 | None | 0 | unclear | Y | Y | PASS |
| 005-sonnet5-alone | 61 | 73 | 26 | 2 | 0 | 0 | 0 | 18 | 11 | 8 | 0 | 0 | 6 | 2 | 0 | 0 | 0 | 36 | 37 | 0 | None | 0 | None | Y | Y | PASS |
| 006-sonnet5-alone | 51 | 50 | 16 | 0 | 0 | 0 | 0 | 7 | 8 | 10 | 1 | 6 | 2 | 0 | 0 | 0 | 0 | 28 | 30 | 6 | None | 0 | unclear |  | Y | PASS |
| 007-sonnet5-alone | 61 | 68 | 11 | 27 | 0 | 0 | 0 | 2 | 6 | 10 | 0 | 1 | 0 | 0 | 0 | 0 | 11 | 49 | 60 | 1 | None | 0 | unclear |  | Y | FAIL 7/8 |
| 008-sonnet5-alone | 61 | 72 | 15 | 5 | 0 | 0 | 0 | 22 | 11 | 7 | 1 | 3 | 3 | 3 | 0 | 0 | 2 | 45 | 52 | 3 | None | 0 | failures-present | Y | Y | PASS |
| 009-sonnet5-alone | 61 | 72 | 16 | 8 | 0 | 0 | 0 | 16 | 8 | 15 | 0 | 3 | 1 | 4 | 0 | 0 | 1 | 18 | 46 | 3 | None | 0 | unclear | Y | N | UNEVALUATED |
| 010-sonnet5-alone | 61 | 70 | 16 | 19 | 0 | 0 | 0 | 4 | 11 | 2 | 0 | 1 | 1 | 3 | 0 | 0 | 13 | 54 | 55 | 1 | None | 0 | unclear | Y | N | UNEVALUATED |
| 011-sonnet5-alone | 61 | 75 | 16 | 22 | 0 | 0 | 0 | 7 | 8 | 15 | 1 | 3 | 1 | 0 | 0 | 0 | 2 | 48 | 64 | 3 | None | 0 | unclear | Y | N | UNEVALUATED |
| 001-sonnet5-with-sanka | 61 | 66 | 13 | 0 | 0 | 0 | 0 | 12 | 13 | 10 | 3 | 7 | 1 | 5 | 1 | 0 | 1 | 30 | 31 | 7 | None | 0 | unclear | Y | N | UNEVALUATED |
| 002-sonnet5-with-sanka | 61 | 68 | 16 | 16 | 0 | 0 | 0 | 10 | 5 | 6 | 1 | 2 | 4 | 1 | 2 | 0 | 5 | 43 | 45 | 2 | None | 0 | unclear | Y | N | UNEVALUATED |
| 003-sonnet5-with-sanka | 61 | 69 | 16 | 19 | 0 | 0 | 0 | 8 | 9 | 10 | 0 | 2 | 0 | 4 | 1 | 0 | 0 | 44 | 49 | 2 | None | 0 | unclear | Y | N | UNEVALUATED |
| 004-sonnet5-with-sanka | 61 | 77 | 20 | 17 | 2 | 0 | 0 | 20 | 1 | 6 | 1 | 5 | 1 | 4 | 0 | 0 | 0 | 55 | 61 | 5 | None | 0 | unclear | Y | Y | PASS |
| 005-sonnet5-with-sanka | 61 | 69 | 15 | 0 | 0 | 0 | 0 | 21 | 12 | 3 | 2 | 2 | 2 | 12 | 0 | 0 | 0 | 54 | 55 | 2 | None | 0 | failures-present | Y | Y | PASS |
| 006-sonnet5-with-sanka | 62 | 61 | 12 | 12 | 0 | 0 | 0 | 9 | 8 | 5 | 0 | 9 | 3 | 1 | 1 | 0 | 1 | 34 | 35 | 9 | None | 0 | failures-present |  | Y | PASS |
| 007-sonnet5-with-sanka | 61 | 71 | 13 | 16 | 5 | 3 | 0 | 4 | 8 | 9 | 1 | 5 | 1 | 1 | 1 | 0 | 3 | 50 | 60 | 5 | None | 0 | unclear | Y | N | UNEVALUATED |
| 008-sonnet5-with-sanka | 61 | 69 | 15 | 0 | 0 | 0 | 0 | 24 | 8 | 6 | 5 | 4 | 4 | 2 | 1 | 0 | 0 | 42 | 43 | 4 | None | 0 | unclear | Y | Y | PASS |
| 009-sonnet5-with-sanka | 61 | 70 | 14 | 3 | 2 | 0 | 0 | 16 | 5 | 11 | 2 | 5 | 4 | 7 | 1 | 0 | 0 | 40 | 52 | 5 | None | 0 | failures-present | Y | N | UNEVALUATED |
| 010-sonnet5-with-sanka | 46 | 45 | 16 | 0 | 0 | 0 | 0 | 5 | 10 | 2 | 1 | 5 | 1 | 2 | 3 | 0 | 0 | 28 | 29 | 5 | None | 0 | failures-present |  | Y | PASS |
| 011-sonnet5-with-sanka | 61 | 69 | 16 | 0 | 0 | 0 | 0 | 36 | 3 | 7 | 0 | 3 | 1 | 3 | 0 | 0 | 0 | 56 | 57 | 3 | None | 0 | unclear | Y | N | UNEVALUATED |
