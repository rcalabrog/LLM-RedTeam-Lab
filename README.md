# LLM Red Team Lab

![LLM Red Team Lab Preview](frontend/public/images/redteamlab.JPG)

**LLM Red Team Lab** is a local-first security testing lab for evaluating jailbreak, prompt injection, prompt leakage, and defense effectiveness across vulnerable and defended LLM targets.
It provides a full workflow to run deterministic offensive campaigns, compare vulnerable vs defended targets, evaluate outcomes with transparent rules, and persist campaign history in SQLite.

## 1. Project Overview

LLM Red Team Lab lets you:

- Run offensive prompt campaigns against configurable local targets.
- Compare baseline vulnerable behavior against guarded behavior with switchable defenses.
- Evaluate results using deterministic rules with explicit evidence.
- Save and reopen historical campaigns from local SQLite storage.

The project is built to demonstrate practical AI security engineering patterns: reusable target abstractions, modular defenses, deterministic evaluation, and reproducible local experimentation.

## 2. Features

- Local Ollama-based model runtime integration.
- Two target variants: `simple_vulnerable_chat` (intentionally weak baseline) and `guarded_chat` (defense pipeline enabled).
- Reusable, switchable defense pipeline (`input_filter`, `context_sanitizer`, `output_guard`).
- Built-in offensive attack library (multiple categories, typed schemas, filterable catalog).
- Deterministic campaign runner with batch execution and partial-failure handling.
- Rule-based evaluator with `success`, `failed`, and `ambiguous` classification.
- Per-attack reasoning artifacts: matched signals, matched rules, reasoning summary, and response excerpt.
- Aggregate metrics and category/severity breakdowns.
- SQLite persistence for evaluated campaign history.
- Consolidated FastAPI workflow endpoints for frontend-friendly orchestration.
- Portfolio-ready Next.js frontend for run configuration, metrics, and result inspection.

## 3. Prerequisites and Installation

### Prerequisites

- Python `3.10+`
- Node.js `20+`
- Ollama installed and available in PATH
- Local models: `qwen3.5:9b` and `llama3.1:8b`

### Clone

```bash
git clone https://github.com/rcalabrog/LLM-RedTeam-Lab
cd llm-red-team-lab
```

### Backend setup

```bash
cd backend
python -m pip install -r requirements.txt
copy .env.example .env
cd ..
```

### Frontend setup

```bash
cd frontend
npm install
cd ..
```

### Pull required Ollama models

```bash
ollama pull qwen3.5:9b
ollama pull llama3.1:8b
```

### Run backend

From repo root:

```bash
uvicorn backend.app.main:app --reload
```

From `backend/`:

```bash
cd backend
uvicorn app.main:app --reload
```

### Run frontend

```bash
cd frontend
npm run dev
```

### Environment notes

- Backend env file: `backend/.env`
- Default SQLite path: `backend/data/llm_red_team_lab.db`
- Frontend API base defaults to: `http://127.0.0.1:8000/api/v1`
- Optional frontend override (set in your shell before `npm run dev`):

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 3.1 LLM Requirements

### Test Machine Used for This Project

This project was tested locally on a machine with:

- **GPU:** NVIDIA GeForce GTX 1660 6GB
- **RAM:** 32GB DDR4 3200 C16

This setup is enough to run the current local model configuration used in the project, but generation speed and responsiveness will still depend on quantization level, context size, and whether the model fits fully in VRAM or needs CPU/RAM offloading.

### Minimum Requirements for the Current Models

The project currently uses:

- `qwen3.5:9b`
- `llama3.1:8b`

As a practical baseline for local usage:

- **`qwen3.5:9b`**
  - **Minimum VRAM:** ~5GB for 4-bit quantized variants
  - **Recommended system RAM:** 16GB+
  - **Recommended for smoother local use:** 6GB+ VRAM and 16–32GB RAM  
    Public hardware guides for Qwen 3.5 9B report roughly **~5GB VRAM at 4-bit quantization** and around **~18GB at BF16/full precision**, with memory needs increasing as context grows. :contentReference[oaicite:0]{index=0}

- **`llama3.1:8b`**
  - **Practical minimum VRAM:** ~6–8GB for quantized local usage
  - **Recommended system RAM:** 16GB+
  - **Recommended for smoother local use:** 8GB+ VRAM and 16–32GB RAM  
    For 7B–9B class models, local hardware guidance commonly places them in the **6–8GB VRAM** range for quantized inference, with larger VRAM preferred for better speed and less offloading. :contentReference[oaicite:1]{index=1}

### If Your PC Is Weaker — or If You Want to Use Stronger Models

If your machine does not meet these requirements, or if it exceeds them and you want to try larger or more capable local models, a very useful resource is:

- **CanIRun.ai** — a hardware/model compatibility checker that estimates which local AI models your machine can run based on your GPU, VRAM, RAM, and browser-detected hardware. :contentReference[oaicite:2]{index=2}

You can use it here:

- `https://www.canirun.ai/`

### Where to Change the Model in This Project

To switch to a different local model, update the backend environment configuration in:

```bash
backend/.env
```

## 4. Detailed Usage Guide

1. Start Ollama:

```bash
ollama serve
```

2. Verify required models exist:

```bash
ollama list
```

3. Start backend (`http://127.0.0.1:8000`).
4. Start frontend (`http://localhost:3000`).
5. Open the UI and check readiness status in the left sidebar.
6. Review catalog data loaded at startup (targets, defenses, attack categories).
7. Choose a target: `simple_vulnerable_chat` for baseline behavior, or `guarded_chat` for defended behavior.
8. Optionally set category, severity, and max attacks.
9. If using `guarded_chat`, select default or custom defenses.
10. Run a campaign with `Execute` (honors the Persistence checkbox) or `Execute + Evaluate` (no save).
11. Inspect aggregate metrics and category breakdown.
12. Inspect per-attack rows for classification, execution status, and signal counts.
13. Select any row to inspect matched rules, reasoning summary, excerpt, and defense metadata.
14. Reopen saved campaigns from the sidebar to review historical runs.

## 5. Tech Stack (with Rationale)

| Technology                   | Used For                  | Why This Choice                                                              |
| ---------------------------- | ------------------------- | ---------------------------------------------------------------------------- |
| Python                       | Core backend language     | Fast iteration, clear typing, strong ecosystem for API and security tooling. |
| FastAPI                      | HTTP API surface          | Typed contracts, clean dependency injection, strong docs/OpenAPI support.    |
| pydantic / pydantic-settings | Schemas and config        | Strict request/response validation and explicit environment-driven config.   |
| httpx                        | Provider HTTP integration | Async-friendly, reliable client for Ollama provider calls.                   |
| Ollama                       | Local model runtime       | Local-first execution and reproducible testing without cloud dependency.     |
| Qwen `qwen3.5:9b`            | Default main model        | Strong local-capable model for primary target execution.                     |
| Llama `llama3.1:8b`          | Comparison model          | Secondary model support for future differential analysis workflows.          |
| SQLite (`sqlite3`)           | Persistence               | Zero-dependency local storage, explicit SQL, easy reproducibility.           |
| Next.js 16                   | Frontend app framework    | App Router architecture, strong DX, production-ready React setup.            |
| React 19                     | UI layer                  | Composable component architecture for complex inspection workflows.          |
| TypeScript                   | Frontend safety           | Strong typing for API contracts and UI state consistency.                    |
| Tailwind CSS                 | Styling system            | Fast iteration with consistent design tokens and utility-driven layout.      |
| Framer Motion                | UI motion                 | Subtle transitions for panel/metric feedback without heavy animation.        |

## 6. Software Architecture

### Backend module structure

- `llm/`: provider abstraction, Ollama implementation, provider registry.
- `targets/`: target app abstraction and concrete vulnerable/guarded targets.
- `defenses/`: deterministic, switchable defense modules and pipeline orchestration.
- `attacks/`: static typed attack catalog with filtering and lookup.
- `orchestration/`: batch campaign execution and raw per-attack result capture.
- `evaluation/`: deterministic classification rules and aggregate metrics.
- `storage/`: SQLite schema/init/repository for campaign persistence.
- `api/`: thin HTTP routes, shared dependencies, consolidated workflow endpoints.

### Frontend structure

- `components/`: reusable UI sections (sidebar, configurator, table, detail panel, metrics).
- `types/`: typed API and UI domain models.
- `lib/`: typed API client and result transformation helpers.
- `app/page.tsx`: composition layer for bootstrap, state, and workflow actions.

### High-level flow

```text
Frontend UI
  -> workflow catalog / readiness / saved campaigns
  -> execute-evaluate / execute-evaluate-save

FastAPI API
  -> targets
  -> defenses
  -> attack catalog
  -> campaign runner
  -> deterministic evaluator
  -> SQLite persistence

Stored artifacts
  -> raw execution results
  -> evaluation outcomes
  -> aggregate metrics
  -> historical campaign records
```

## 7. API Overview

Main MVP endpoints used by the frontend:

| Endpoint                                       | Purpose                                                   |
| ---------------------------------------------- | --------------------------------------------------------- |
| `GET /api/v1/workflows/catalog`                | Bootstrap targets, defenses, attack category summary.     |
| `POST /api/v1/workflows/execute-evaluate`      | Run campaign and return evaluated result (not persisted). |
| `POST /api/v1/workflows/execute-evaluate-save` | Run, evaluate, and persist in one call.                   |
| `GET /api/v1/storage/campaigns`                | List saved campaign summaries.                            |
| `GET /api/v1/storage/campaigns/{run_id}`       | Retrieve one full saved campaign.                         |
| `GET /api/v1/health/readiness`                 | Local dependency readiness (`llm`, `sqlite`).             |
| `GET /api/v1/health`                           | Basic app health.                                         |
| `GET /api/v1/health/llm`                       | LLM provider availability check.                          |

## 8. Evaluation Approach

The MVP evaluator is fully deterministic and rule-based. It does not use an LLM judge.

Per attack, the evaluator outputs:

- `success`: offensive objective appears achieved.
- `failed`: target appears to have resisted safely.
- `ambiguous`: mixed or inconclusive signals.
- matched signals (structured indicators).
- matched rules (rule ids with evidence).
- reasoning summary (human-readable explanation).

This design favors:

- transparency (why a classification happened),
- reproducibility (same input, same output),
- auditability (traceable evidence and rule matches).

## 9. Current Limitations

- Evaluation rules are heuristic and primarily English-oriented.
- No streaming progress updates during campaign execution yet.
- No authentication or multi-user support.
- Targets are currently simple chat targets, not full agentic/RAG production apps.
- Frontend is desktop-first; mobile ergonomics are not a priority in this MVP.
- Local runtime and model performance depend on host hardware resources.

## 10. Future Improvements

- Add a mini-RAG vulnerable target for indirect prompt injection scenarios.
- Expand defense strategies and policy granularity.
- Improve multilingual rule coverage in evaluation logic.
- Add trend charts and historical comparative analytics.
- Add exportable run reports (JSON/PDF).
- Add side-by-side target comparison mode in the UI.
- Add optional streaming execution progress events.

## 11. License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for details.
