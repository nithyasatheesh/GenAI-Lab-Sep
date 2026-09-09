# Real browser JupyterLab, pre-loaded with the GenAI RAG lab.
# Deploy to: Hugging Face Spaces (sdk: docker), Render, Railway, Fly.io, or any VM.
FROM python:3.11-slim

# --- system deps kept minimal ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# --- non-root user (Hugging Face Spaces requires uid 1000) ---
RUN useradd -m -u 1000 learner
ENV HOME=/home/learner \
    PATH=/home/learner/.local/bin:$PATH \
    SANDBOX_MODE=mock \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /home/learner/work

# --- python deps ---
COPY --chown=learner:learner requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- lab content (read-only helpers + the notebooks the learner opens) ---
COPY --chown=learner:learner sandbox.py grader.py grader_tests.py ./
COPY --chown=learner:learner content ./content
COPY --chown=learner:learner RAG_Lab_Participant.ipynb RAG_Lab.ipynb ./
COPY --chown=learner:learner jupyter_server_config.py /etc/jupyter/jupyter_server_config.py
COPY --chown=learner:learner README_IN_LAB.md ./README.md

USER learner
EXPOSE 8888

# token comes from the JUPYTER_TOKEN env var (set it as a platform secret);
# empty means no token (fine only when the platform already gates access).
CMD ["jupyter", "lab", "--config=/etc/jupyter/jupyter_server_config.py"]
