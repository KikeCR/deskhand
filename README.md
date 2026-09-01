# DeskHand

**An AI-powered onboarding assistant that combines RAG, a CrewAI multi-agent crew, and a deterministic decision engine to automate new-hire onboarding.**

## Why this exists

A lot of "AI automation" job descriptions boil down to the same shape: pull structured data from one system, ground an LLM's output in real documents instead of letting it hallucinate policy, run a small pipeline of specialized steps instead of one giant prompt, and branch behavior based on real-world conditions. DeskHand is a small, self-contained project built to demonstrate exactly that shape, using employee onboarding as the concrete scenario:

- A **RAG layer** grounds every onboarding step in the company's actual policy docs, not the model's guess at what a typical company might do.
- A **CrewAI crew** splits the work across three specialized agents (Intake, Research, Reporting) instead of one prompt trying to do everything.
- A **deterministic decision engine** (plain Python, not an LLM call) branches the checklist by location and department, and the branching is fully visible in the output.
- A small **FastAPI + React UI** turns the CLI script into something a recruiter can actually click through.

It's a portfolio piece, so the "company," "employees," and documents are all mock data — but the pipeline, the branching logic, and the test suites are real.

## Architecture

```
                    ┌─────────────────────┐
   New hire  ────▶  │   Intake Agent      │  validates & normalizes
   profile          │                     │  the hire's profile
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐       ┌─────────────────────┐
                    │  Decision Engine     │──────▶│  Chroma vectorstore  │
                    │  (plain Python)      │       │  (company docs)      │
                    │  location + dept     │       └──────────┬───────────┘
                    │  branch + rationale  │                  │
                    └──────────┬──────────┘        RAGSearchTool
                               │                              │
                    ┌──────────▼──────────┐                  │
                    │  Research Agent      │◀─────────────────┘
                    │  queries the RAG     │
                    │  vectorstore         │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Reporting Agent      │  writes the final
                    │                       │  markdown checklist
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  FastAPI  /  CLI      │  → React UI or run.py
                    └───────────────────────┘
```

The Decision Engine sits **outside** the CrewAI agents, between Intake and Research. It reads the hire's `location` and `department` and returns a structured result: which track matched, which steps that track adds, and a plain-English explanation of why. That result is handed to the Research and Reporting agents as guidance, and is also rendered directly (not paraphrased by an LLM) in the final checklist and the API response, so the branching is guaranteed visible no matter how the agents phrase things.

## Setup

Requires Python 3.12+ and Node 20+.

```bash
git clone <this-repo>
cd deskhand

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env   # then add at least one LLM provider's API key
uvicorn api:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api/*` to the backend on port 8000.

### LLM providers

Only one provider needs to be configured, but you can set more than one and DeskHand will fail over between them automatically:

```env
LLM_PROVIDERS=openai,deepseek,kimi   # tried in this order; missing keys are skipped

OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=sk-...
```

See `.env.example` for the full list of variables. RAG embeddings run on a free local model (see [Design decisions](#design-decisions)), so none of this affects retrieval — it's only for the three agents' chat calls.

### CLI usage

```bash
cd backend
python run.py --hire-file data/sample_hires/remote_engineer.json
# or
python run.py --name "Jordan Reyes" --role "Support Engineer" \
  --department Engineering --location remote --start-date 2026-10-01
```

## Example usage

Both runs below are real output from this codebase (via DeepSeek, one of the configured fallback providers), for the two bundled sample hires — a remote engineer and an in-office sales hire — so the branching is visible side by side.

### Remote engineer

Input: `data/sample_hires/remote_engineer.json` — Priya Nakamura, Software Engineer II, Engineering, remote.

```markdown
# Week 1 Onboarding Checklist

**Name:** Priya Nakamura
**Role:** Software Engineer II
**Department:** Engineering
**Location:** Remote
**Start Date:** 2026-09-15

---

## IT & Equipment

- IT will ship a company laptop and docking station to your home address. Expect delivery at least 3 business days before your start date.
- On Day 1, install the company VPN client and connect to the corporate network to verify access to internal tools.
- Submit your one-time $500 home-office equipment stipend request through the expense system (for items such as a monitor, chair, or desk).
- Read and electronically acknowledge the Remote Work Policy before the end of Week 1.

---

## Tool & System Access

- Accept your invitation to the company GitHub organization.
- Request access to the cloud sandbox/staging environment.
- Set up your local development environment following the engineering onboarding document.
- Get added to the on-call rotation as an observer (training track).

---

## From Company Policy

- You must complete mandatory compliance training by the end of Week 1, including code of conduct, security awareness, and harassment prevention modules. (Source: `onboarding_policy.md`)
- Set a strong password and enable multi-factor authentication (MFA) on your company account on Day 1. (Source: `it_setup_checklist.md`)
- You are eligible for a one-time $500 home-office equipment stipend and a $50/month internet-and-phone reimbursement, submitted monthly through the expense system. (Source: `benefits_faq.md`)
- All company equipment remains company property and must be returned upon termination of employment. (Source: `remote_work_policy.md`)

## Why These Steps (Decision Log)

- Location='remote' matched track 'remote' -> added 4 IT/equipment step(s).
- Department='Engineering' matched track 'engineering' -> added 4 tool-access step(s).
```

### In-office sales hire

Input: `data/sample_hires/inoffice_sales.json` — Marcus Delgado, Account Executive, Sales, in-office.

```markdown
# Week 1 Onboarding Checklist

**Name:** Marcus Delgado
**Role:** Account Executive
**Department:** Sales
**Location:** In-office
**Start Date:** 2026-09-08

---

## IT & Equipment

- **Day 1:** Pick up your physical badge and access card at the front desk to gain entry to the building and your assigned floor.
- **Day 1:** Visit the on-site IT help desk to collect your laptop, monitor, and peripherals. IT staff will also help you connect to office Wi-Fi and printers.
- **Day 1 (or by end of Week 1):** Confirm your assigned desk (and locker, if requested) with Facilities.
- **Day 1 (or by end of Week 1):** Pick up your parking permit or transit subsidy card from Facilities, depending on your commute preference.

---

## Tool & System Access

- **By end of Week 1:** Get provisioned in the CRM (Salesforce) with your territory assigned, so you can begin real work in Week 2.
- **By end of Week 1:** Complete the sales enablement portal training modules assigned to you.
- **By end of Week 1:** Review your commission plan document with your manager to understand your compensation structure.
- **By end of Week 1:** Shadow two customer calls with a senior account executive to observe sales processes and best practices.

---

## From Company Policy

- Attend a company-wide orientation session on Day 1, covering company history, mission, org structure, and a walkthrough of internal tools such as Slack, the HR portal, and the expense system (`onboarding_policy.md`).
- Complete all mandatory compliance training, including code of conduct, security awareness, and harassment prevention, by the end of Week 1 (`onboarding_policy.md`).
- Meet your assigned onboarding buddy and review your 30-60-90 day plan with your manager during Week 1 (`onboarding_policy.md`).
- Review and sign your offer letter and any role-specific agreements by the end of Week 1 (`onboarding_policy.md`).

## Why These Steps (Decision Log)

- Location='in_office' matched track 'in_office' -> added 4 IT/equipment step(s).
- Department='Sales' matched track 'sales' -> added 4 tool-access step(s).
```

Notice the IT/equipment and tool-access sections are completely different between the two, and the decision log at the bottom names exactly why. In the UI, the same decision object drives a "Decision Log" panel with the two tracks shown as separate cards, plus a "Research Sources" panel showing the grounded excerpts the Research Agent pulled, before the rendered checklist.

## Design decisions

**Why CrewAI, and why three agents instead of one prompt.** A single prompt that reads a hire's profile, decides what they need, searches documents, and writes a checklist conflates four different jobs into one context window, and it's much harder to test or debug why a particular step showed up. Splitting into Intake → Research → Reporting means each agent has one job, each step is independently inspectable in the output, and it mirrors how a real onboarding automation would likely be built as a pipeline of specialized steps.

**Why the decision engine is plain code, not an LLM call.** Whether a hire needs a badge or a VPN, GitHub access or CRM access, is a business rule with a right answer, not a judgment call. Leaving it to an LLM risks the same inputs producing different branches on different runs, and makes the "why" hard to audit. Making it a deterministic function means the branch is always correct for a given input, it's unit-testable with plain `pytest.mark.parametrize`, and its output can be safely rendered verbatim instead of trusted to an LLM's paraphrase.

**Why RAG at all, instead of just prompting the LLM with the policy.** The four "company docs" are small enough to fit directly in a prompt, but that's not the point: RAG is what happens when the document set doesn't fit, changes over time, or needs to be swapped without redeploying code. Building it here (even at small scale) is what makes this project representative of the real pattern rather than a shortcut around it.

**Why local embeddings but a multi-provider chat LLM.** Embeddings and chat completions are separate concerns with different constraints. Embeddings just need to place semantically similar text near each other, which a free local model (`all-MiniLM-L6-v2` via `onnxruntime`, bundled with Chroma) does perfectly well for four small policy docs, so retrieval never depends on anyone's API billing status. Chat completions (the three agents' reasoning) benefit more from a stronger hosted model, so that piece is provider-agnostic: `LLM_PROVIDERS` lists OpenAI, DeepSeek, and Kimi (Moonshot) in priority order, and `agents/crew.py::kickoff_with_fallback` retries the next provider if one fails (auth error, rate limit, out of quota), so the demo keeps working for whoever's running it regardless of which provider they happen to have credit on.

**Why a FastAPI layer instead of CLI-only.** `pipeline.run_onboarding(hire) -> OnboardingResult` is the one function every entry point calls. `run.py` and `api.py` are both thin wrappers around it — argparse on one side, pydantic request/response models on the other — so the actual pipeline logic is never duplicated. This also means a future n8n workflow or webhook trigger is a small addition (call the same function from a new handler), not a rewrite. The FastAPI layer exists mainly so the React UI has something to call, which makes the branching demo interactive instead of something you have to read off a terminal.

## Limitations / what I'd add next

- **HR system integration.** The "HR system" is two JSON files. A real version would pull from Workday, BambooHR, or similar via their API.
- **Delivery.** The checklist is written to a markdown file and returned over HTTP; it isn't emailed or posted to Slack. Wiring up an email/Slack delivery step would be a natural next agent or task.
- **Trigger.** `run_onboarding()` is called from a CLI and a REST endpoint today. An n8n workflow (HR system webhook → DeskHand → Slack) or a native webhook receiver would be the production trigger.
- **Synchronous execution.** A crew run takes roughly 15-40 seconds and the API blocks for the whole thing. A production version would queue the run and stream progress (or poll a job status endpoint) instead.
- **Rule coverage.** The decision engine only has rules for two departments (engineering, sales); anything else falls back to a generic step list. Real coverage would need a rule (or a config-driven table) per department.

## Tech stack

**Backend:** Python, CrewAI, Chroma (local vector store), `onnxruntime` (local embeddings), FastAPI, pydantic, pytest, `python-dotenv`.

**LLM providers:** OpenAI, DeepSeek, Kimi (Moonshot) — configurable, with automatic fallback.

**Frontend:** React, TypeScript, Vite, Tailwind CSS v4, `class-variance-authority`, `react-markdown`, Vitest, Testing Library.

**CI:** GitHub Actions, two path-filtered workflows (backend/frontend), both fully offline (no real API calls in either test suite).
