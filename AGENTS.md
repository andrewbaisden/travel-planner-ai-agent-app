# AGENTS.md

Guidance for humans and coding agents working in this repository.

## What this repo is

This is a **local-first travel planner demo**. Users describe trip preferences; a local [Ollama](https://ollama.ai) model returns a markdown travel plan.

There are **two UIs and one Python backend**:

- **FastAPI** (`backend/api.py`) — REST API on port `8000` for the Next.js frontend
- **Gradio** (`backend/app.py`) — demo UI on port `7860`; calls the same Python functions directly
- **Next.js 14** App Router (`frontend/`) — React UI on port `3000`

Workflows:

1. **Simple** — one prompt, one markdown plan
2. **Agentic** — `TravelAgent` phases: plan → research → generate → reflect → improve

It is **not** a booking product, a cloud SaaS, or a multi-tenant planner. There is **no live flights, hotels, maps, or weather API**. Plans are LLM-generated text. The agentic accordion in the Next.js UI currently **simulates** phase progress with timeouts while a single `/travel-plan-unified` request runs; Gradio waits for the real workflow.

## Non-negotiable rules

- TypeScript **strict** stays on. Do not add `any` without a one-line justification on that binding.
- Never commit secrets. `.env` files stay local. Do not paste keys into screenshots, logs, or agent transcripts.
- **Ollama is the LLM runtime.** Do not add a second provider (OpenAI, Anthropic, etc.) without a dedicated adapter that both Gradio and FastAPI can share. Default model remains whatever the user has pulled locally (`llama3` is the documented fallback).
- Travel-plan HTTP identity lives on FastAPI. The Next.js frontend uses **`POST /travel-plan-unified`** and **`GET /models`**. Do not fork request/response shapes (`user_query`, `model_name`, `workflow_type`; Simple `{ travel_plan }` vs Agentic `{ plan, research, initial_plan, reflection, final_plan }`). Keep `/travel-plan` and `/travel-plan-agentic` consistent with the unified handler or delete them in a dedicated cleanup.
- Agentic phase identity lives in [`backend/agent.py`](backend/agent.py) (`TravelAgent.run_workflow`). Tool prompts live in [`backend/tools.py`](backend/tools.py). Do not hardcode a second phase list or a second set of prompts in the frontend.
- **Tailwind CSS is the established styling system** in `frontend/`. Prefer utilities and the existing `@apply` markdown/accordion classes in [`frontend/app/globals.css`](frontend/app/globals.css). Do not introduce a second CSS-in-JS library or a handwritten global redesign without a dedicated visual pass.
- Do not add Postgres, Prisma, Better Auth / Clerk, Redis, BullMQ, Zustand, or TanStack Query unless there is a clear architectural purpose (persisted trips, signed-in users, background jobs, or interaction state that local component state cannot hold).
- Do not introduce a second travel-plan endpoint contract, a second Ollama client wrapper, or a second model-list parser. `SimpleOllamaAgent` and the Ollama list-parsing logic should stay shared, not copied.
- Prefer small, reversible diffs. Do not rewrite the agentic workflow to land an unrelated UI change.
- Keep authoritative generation on the **server**. The Next.js page holds form and display state only. Do not generate plans in the browser.
- Call the backend through the Next rewrite (`/api/...` → FastAPI) or a single documented base URL. Do not leave a third hardcoded `http://localhost:8000` beside the existing rewrite.

## Tech stack

Use the established engineering stack unless a new dependency has a clear architectural purpose.

### Established in this repo

| Layer | Choice |
| --- | --- |
| Backend language | **Python 3.8+** (`venv` at repo root) |
| LLM | **Ollama** (`ollama` Python client, local models) |
| API | **FastAPI** + **Uvicorn** + **Pydantic v2** |
| Demo UI | **Gradio** |
| Frontend | **Next.js 14** App Router (`frontend/app`) |
| Language (UI) | **TypeScript**, strict mode |
| Styling | **Tailwind CSS** + a small `globals.css` |
| HTTP (UI) | **Axios** |
| Markdown | **react-markdown** |
| Package manager (UI) | **npm** (`frontend/package-lock.json`) |
| Code quality (UI) | **ESLint** via `next lint` (`eslint-config-next`) |
| Hosting | Local processes. Not deployed. |

### Add when justified

These are the target stack defaults for new **product** surface. **Do not install them for this local demo without a real need.**

| Layer | Choice | When |
| --- | --- | --- |
| Styling | shadcn/ui | Dedicated component-system migration on top of Tailwind |
| Client state | **Zustand** | Interaction state that has outgrown the single-page `useState` tree |
| Server state | **TanStack Query** | Remote collections, mutations, and cache invalidation |
| Database | **PostgreSQL** + **Prisma** | Saved trips, users, or history |
| Auth | **Better Auth** (prefer) or **Clerk** | Signed-in users |
| Caching / jobs | **Redis**, **BullMQ** | Queued generation, rate limits, or long agent runs |
| Infra | **Docker**; Fly.io / AWS (or similar) for persistent workers | A process that cannot stay as `python3 api.py` + `npm run dev` |
| Monitoring | **Sentry**, **PostHog** | Error tracking / product analytics with project keys in env |
| Frontend package manager | **pnpm** | Dedicated lockfile migration off npm |
| Next.js line | **16.x** | Dedicated upgrade off 14; do not mix majors casually |
| Lint / format | **Biome** | Dedicated replacement of ESLint, not a second linter |
| Testing | **Vitest**, **React Testing Library**, **Playwright**; **pytest** for Python | First tests, or CI |

#### Zustand (when added)

Use for appropriate **interaction** state such as:

- selected workflow (Simple / Agentic)
- selected Ollama model
- accordion open/closed
- unsaved query text

Do **not** duplicate the generated plan, research payload, or model catalogue in Zustand if the server already owns them.

#### TanStack Query (when added)

Use for remote data such as:

- `GET /models`
- travel-plan mutations
- saved trip listings (if a database exists)

Realtime or long-running agent updates must **update or invalidate** Query caches deliberately rather than becoming a second uncontrolled store.

## Project map

| Path | Role |
| --- | --- |
| `backend/api.py` | FastAPI app, CORS, Pydantic models, `/models` and travel-plan routes |
| `backend/app.py` | `SimpleOllamaAgent`, `create_travel_plan` / `create_travel_plan_agentic`, Gradio UI |
| `backend/agent.py` | `TravelAgent` — in-memory phase orchestration |
| `backend/tools.py` | Prompt tools: destinations, research JSON, plan, reflection, improve |
| `frontend/app/page.tsx` | Single-page UI: form, Simple markdown, Agentic accordions |
| `frontend/app/layout.tsx` | Root layout and metadata |
| `frontend/app/globals.css` | Tailwind layers, markdown, accordion |
| `frontend/next.config.js` | Rewrites `/api/:path*` → `http://localhost:8000/:path*` |
| `requirements.txt` | Python dependencies |
| `frontend/package.json` | Next.js scripts and UI dependencies |
| `README.md` | Human setup and screenshots |

Path alias (frontend only): `@/*` → `frontend/*`.

## Commands

From the repo root:

```shell
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip3 install -r requirements.txt
```

Backend (two processes; Gradio is optional if you only use Next.js):

```shell
cd backend
python3 api.py                    # FastAPI → http://127.0.0.1:8000
python3 app.py                    # Gradio → http://127.0.0.1:7860
```

Frontend:

```shell
cd frontend
npm install
npm run dev                       # http://localhost:3000
npm run build
npm start
npm run lint                      # next lint (ESLint)
```

Ollama must already be running. If no models are listed:

```shell
ollama pull llama3
```

Useful URLs:

| Surface | URL |
| --- | --- |
| Next.js UI | http://localhost:3000 |
| FastAPI | http://127.0.0.1:8000 |
| FastAPI models | http://127.0.0.1:8000/models |
| Gradio | http://127.0.0.1:7860 |
| Ollama tags | http://127.0.0.1:11434/api/tags |

There is **no** `pnpm` workspace, Biome, Vitest, Playwright, or GitHub Actions workflow in this repo today. Do not document or invoke them until they exist.

## Testing expectations before a PR

There is no test suite yet. Until one exists, at minimum:

1. `npm run lint` in `frontend/`
2. Typecheck the frontend (`npx tsc --noEmit` in `frontend/` if no `typecheck` script)
3. Manually run Simple and Agentic once against a local Ollama model when the change is **user-visible** (form, workflows, markdown, API contract, Gradio)

When tests are added:

- New behaviour needs a test at the **cheapest layer** that would catch a regression: Pydantic / prompt parsing / unit first, component next, e2e last.
- Mock `ollama.generate` / `ollama.list`. Never call a real model from CI or unit tests.
- Do not snapshot entire generated travel plans. Assert request contracts, parsed JSON keys (`best_time`, `attractions`, `issues`, …), and a few accessible controls instead.

Also:

- Do not merge with skipped or failing tests once CI exists.
- Keep Gradio and FastAPI on the same Python functions so a backend fix cannot silently apply to only one UI.

## Dependency policy

- Default to the established stack above.
- New **runtime** dependencies need a clear architectural purpose, not convenience or familiarity.
- Do not add a library that duplicates FastAPI, Pydantic, Gradio, the Ollama client, Next App Router, or Tailwind.
- Python: add to `requirements.txt` (pin a minimum as the file already does). Frontend: `npm install` / `npm install -D` in `frontend/` and commit `package-lock.json`.
- Stay on the Next.js **14.x** line already in the repo unless the change is a dedicated upgrade.
- Keep the React runtime and `@types/react` on the **same major**. Do not mix React 18 with React 19 types (or the reverse).
- Do not take a drive-by shadcn dependency to style one control.
- Sentry and PostHog stay out until there are project keys and a product reason to ship them.
- Do not switch the frontend to pnpm (or add a root `package.json`) without a dedicated lockfile migration.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/), scoped where it adds clarity:

`feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:`, `perf:`

Examples in **this** repo:

- `feat(agent): skip improve when reflection is empty`
- `fix(api): share ollama model listing with gradio`
- `feat(frontend): call travel plan through /api rewrite`
- `fix(tools): parse research json without a fenced block`
- `test(api): cover unified simple vs agentic shapes`
- `chore(frontend): pin next 14`
- `docs: explain travel agent phases`

Keep commits **logically scoped**. Do not bundle an agent prompt change with a Tailwind tweak and a README edit.

## Environment

No application secrets are required today. Ollama is local; FastAPI and Gradio talk to it on the machine.

| Variable | Where | Notes |
| --- | --- | --- |
| *(none required)* | — | `python-dotenv` is listed but unused. Add a `.env.example` only when a real key exists. |

If cloud LLM or analytics keys are added later: copy `.env.example` to `.env` / `frontend/.env.local`. Never put a real key in `.env.example`. `.env` and `.env.local` are gitignored.

## Hosting and CI

- This demo is meant to run **locally** (Ollama + FastAPI + optional Gradio + Next.js).
- There is no GitHub Actions workflow, Netlify config, or Docker Compose file. Do not assume a merge gate until CI is added.
- Docker, Fly.io, and AWS are out of scope until a persistent worker or hosted API exists.
- CORS on FastAPI is currently `allow_origins=["*"]` for local development. Do not ship that as-is if the API is ever exposed.

## Do not

- Check in `.env`, `.env.local`, `venv/`, or real API keys.
- Add Prisma, auth, Redis, or a second global state library “for consistency with other repos.”
- Call booking, maps, weather, or other third-party travel APIs from the agent without a dedicated design for server state, keys, and rate limits.
- Generate travel plans in the Next.js client or duplicate `TravelAgent` phases in React.
- Leave a second Ollama list parser or a second unified-endpoint contract.
- Add Biome next to ESLint, or pnpm next to `package-lock.json`, as a drive-by.
- Treat the Next.js agentic spinners as a substitute for streaming or per-phase API events. If you show phases, they must reflect real backend progress or be clearly labelled as estimated.
