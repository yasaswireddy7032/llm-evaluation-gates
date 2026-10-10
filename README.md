# LLM Evaluation Gates

A reproducible evaluation harness for answer correctness, citation validity, latency, and release thresholds.

**Status:** runnable portfolio reference implementation. Uses synthetic or hand-authored demonstration data. No employer code, customer data, or production performance claims.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
python -m unittest -v
```

The default command prints a reproducible JSON demonstration. See `app.py` for the reusable Python API. `example-output.json` records the locally executed demo; it is not an external benchmark.

## Architecture

Labeled cases + prediction records → strict ID validation → per-case grading → aggregate metrics → release gate. CLI accepts JSON files and `--enforce` for nonzero exit on failed gates.

## Validation

Tests exercise failure cases and behavioral invariants, in addition to the executable demo. The included `github-actions-tests.yml` defines tests and the demo on pushes and pull requests. Install it as `.github/workflows/tests.yml` to activate CI. CI has not run on GitHub until this repository is published.

## Limitations and next steps

Exact-match grading is deliberately narrow. A valid citation ID does not prove factual entailment. The one-case demo is a smoke example, not evidence of model quality. Add blinded human labels, semantic graders, safety slices, and confidence intervals for serious release decisions.

## Container

```bash
docker build -t llm-evaluation-gates .
docker run --rm llm-evaluation-gates
```

The Docker recipe is provided; local validation uses Python, not Docker.

## Responsible use

Review the code and understand its assumptions before deploying. Keep credentials in environment variables and exclude private data from commits. This project is an educational engineering baseline, not a production-certified service.

## Paired benchmark and governance report

```bash
python benchmark.py
python benchmark.py --enforce
```

The bundled 18-case synthetic fixture deliberately makes the candidate improve aggregate accuracy while regressing on the refusal slice. The release gate fails and `--enforce` returns exit code 1: this is the expected demonstration outcome, not a test failure. Predictions are authored fixtures, not outputs from a real language model.

The report includes a dataset SHA-256, paired bootstrap interval, per-slice accuracy, citation rules, p95 latency, per-request cost, and explicit gate-failure reasons. Both prediction files must cover exactly the same case IDs. Bootstrap intervals on such a small fixture are illustrative; refusal booleans must be independently labeled in real evaluations. A citation-rule pass still does not prove factual entailment.
