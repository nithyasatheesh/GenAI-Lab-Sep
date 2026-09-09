# GenAI RAG Lab

You're in a real JupyterLab. Start with **`RAG_Lab_Participant.ipynb`**.

1. Run the **Setup** cell once.
2. Fill in each **`%%task N`** cell and run it. Variables carry over between cells
   (`documents` → `chunks` → `vectorstore` → …).
3. Run the **Score** cell any time for a criterion-by-criterion mark out of 100.

`RAG_Lab.ipynb` is the fully-worked reference — open it only after you've tried.

Mode is **mock** by default (no API key). If a key was provided, set
`os.environ["SANDBOX_MODE"] = "openai"` in the Setup cell.
