# Infrastructure Optimizer

Reads a JSON log of server metrics and turns it into a structured report a CTO can act on: summary insights, detected anomalies, a predictive risk assessment, prioritized recommendations, and a per-service status summary.

The design rule behind the project: everything measurable is computed deterministically in Python, and the LLM is scoped to language work only (prioritizing and phrasing advice, reading trends). Numbers are never produced by the model, so they stay reproducible and auditable.

## Pipeline

The work is split into nodes wired with LangGraph. Each node reads from and writes to a shared typed state, and the edges define the order:

```
ingestion -> analysis -> prediction -> recommendation
```

1. **Ingestion** loads the records and validates each one against a Pydantic schema. A malformed record is skipped and logged; the run continues on the valid ones.
2. **Analysis** (deterministic) computes the summary numbers, compares each metric to a threshold table to detect anomalies, and rolls up the worst observed state per service.
3. **Prediction** (LLM) reads the ordered history and flags resource-overload and service-degradation risks, with supporting evidence and an explicit confidence level.
4. **Recommendation** (LLM, with fallback) builds rule-based draft actions from the anomalies, then asks the model to prioritize and consolidate them. If the model call fails, it falls back to the rule-based drafts so a report is always produced.

## Design decisions

- **Deterministic core, LLM at the edges.** Aggregates, threshold checks, and service rollups are plain Python. The model only handles prioritization, phrasing, and trend reading. This keeps the quantitative output stable across runs.
- **Anomalies are collapsed to one row per metric.** With hundreds of samples, a single metric can breach repeatedly. Each anomaly row reports the peak value, how often it breached, and when, instead of emitting one row per sample.
- **Worst status wins.** A service that was offline even once is reported as offline. Hiding a brief outage behind a mostly-healthy average would defeat the point of a monitoring report.
- **Telemetry is treated as untrusted.** Before any data reaches the model it is fenced in delimited data blocks and scanned for injection patterns, and the system prompt is constrained to reject instruction-like content. A crafted log field cannot steer the pipeline.
- **Structured output.** LLM responses are constrained to Pydantic schemas, so the result is always machine-readable or it fails loudly.
- **Config kept separate from logic.** Thresholds and recommendation templates live in their own data structures, so they can be tuned without touching the detection code.

## Output

The pipeline produces a single JSON object:

- `timestamp`: ISO 8601 generation time.
- `insights`: summary numbers (average latency and error rate, peak CPU and memory, latest uptime).
- `anomalies`: one entry per breaching metric, with value, threshold, severity, and a description.
- `predictive_analysis`: observation and forecast windows, data-quality notes, detected trends, risks, and preventive actions.
- `recommendations`: prioritized actions with a target, parameters, and a benefit estimate.
- `service_status_summary`: each service sorted into online, degraded, or offline.

## Layout

```
app/
  domain/        data models (Pydantic) and the threshold table
  pipeline/      shared state, the four nodes, and the LangGraph wiring
  services/      the OpenAI client and the prompt-injection guard
  api/           FastAPI routes
  config.py      settings loaded from the environment
  main.py        FastAPI app
scripts/
  run_pipeline.py    reads the input file, runs the pipeline, writes output.json
  make_gitingest.py  flattens the codebase for review
tests/           node-level tests
data/            sample input
```

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

The prediction and recommendation nodes call OpenAI. Without a key the pipeline still runs: the recommendation node falls back to rule-based drafts, and the prediction node is skipped.

## Running

Generate `output.json` from the sample input:

```bash
python -m scripts.run_pipeline
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Then POST a list of records to `/analyze`, or open `http://127.0.0.1:8000/docs` for the interactive form. `/health` returns a basic liveness check.

## Tests

```bash
pytest -q
```

## Stack

Python, FastAPI, Pydantic, LangGraph, LangChain, OpenAI, Docker, pytest.
