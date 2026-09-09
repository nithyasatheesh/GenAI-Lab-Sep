---
title: GenAI RAG Lab
emoji: 📓
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8888
pinned: false
---

# GenAI / Agentic-AI Lab — real browser JupyterLab

A **real JupyterLab** (not a widget imitation) running in the browser, pre‑loaded
with the RAG lab. Learners open `RAG_Lab_Participant.ipynb`, write Python in real
cells, run them against a live kernel, see stdout/stderr/tracebacks, and run the
**Score** cell to grade themselves with the unchanged `grader.py`
(criterion‑based, partial marks, "it ran" ≠ full marks).

- No local install — everything is in the browser.
- Boots in **Mock mode** — no API key needed.
- `grader.py`, `sandbox.py`, `content/`, rubrics and scoring are **byte‑for‑byte
  the same** as the Streamlit platform.

---

## Deploy

### Option 1 — Hugging Face Spaces (free, fastest)

1. huggingface.co → **New Space** → **Docker** SDK → **blank** template.
2. Set the Space **private** (Settings → Visibility) so only invited people can open it.
3. Upload **all files in this folder** to the Space repo root (`Dockerfile`,
   `requirements.txt`, `jupyter_server_config.py`, `README.md`, `sandbox.py`,
   `grader.py`, `grader_tests.py`, the two `.ipynb`, and the `content/` folder).
4. Space **Settings → Secrets** → add `JUPYTER_TOKEN` = some long random string.
5. Wait for the build. Open the Space; JupyterLab loads. If prompted for a token,
   paste `JUPYTER_TOKEN`.
   (Direct URL form: `https://<user>-<space>.hf.space/lab?token=<JUPYTER_TOKEN>`)

Free CPU Spaces run Labs **1 and 2**. For Labs 3–5 add the heavy packages
(see `requirements.txt` comment) and use a bigger Space or Option 3.

### Option 2 — Render / Railway / Fly.io

- **Render:** New → **Web Service** → "Deploy an existing image / Dockerfile" →
  point at this repo → Environment: `Docker` → add env var `JUPYTER_TOKEN` →
  Instance type with ≥1 GB RAM. Render sets `$PORT`; the config already reads it.
- **Railway / Fly.io:** `railway up` / `fly launch` in this folder; set
  `JUPYTER_TOKEN`; expose port 8888 (Fly: `fly.toml` `internal_port = 8888`).

### Option 3 — any VM with Docker

```bash
docker compose up --build -d
# open http://<host>:8888/lab?token=changeme   (change JUPYTER_TOKEN in docker-compose.yml first)
```

Put it behind nginx/Caddy with TLS. Add `- OPENAI_API_KEY=sk-...` to the compose
`environment:` to enable real OpenAI mode (then set `SANDBOX_MODE=openai` in the
notebook's setup cell).

---

## Real LLM mode

Never bake a key into the image. Set `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) as
a **platform secret**, then in the notebook's first cell:

```python
os.environ["SANDBOX_MODE"] = "openai"   # or "claude"
```

⚠️ In a **single shared container** every learner shares that key and each
other's kernel. That's fine for a solo demo or a proctored one‑at‑a‑time class.
For a real multi‑learner assessment you need **one container per learner** —
front this image with **JupyterHub** (`jupyterhub-ltiauthenticator` for Lumen /
LTI 1.3). See `BROWSER_CODING_ENV_DESIGN.md` and `LMS_INTEGRATION_DESIGN.md`.

---

## Want VS Code instead of Jupyter?

Swap the base image: use `Dockerfile.codeserver` (in this folder) instead of
`Dockerfile`. It serves **code‑server** (VS Code in the browser) with the same
content mounted. For these labs JupyterLab is the better fit (cells + shared
kernel match how the labs build a pipeline) — code‑server is better for a future
multi‑file "build & ship an agent" capstone.
