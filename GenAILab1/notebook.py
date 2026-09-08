"""A minimal Jupyter-style notebook panel for the practice platform.

One ordered list of code cells per lab, a persistent kernel namespace (shared
across cells, like a real notebook), per-cell Run + output, Run-all, Restart,
Add/Delete cell — plus a Grade button that scores the task cells with grader.py
using the exact same rubric as the per-task pages.

Wired into streamlit_app.py: nav_bar adds a "📓 Notebook" entry that calls
render_notebook(spec, mode, dev).
"""
from __future__ import annotations

import contextlib
import tempfile
import time
import traceback

import streamlit as st

import grader  # preamble(), assemble_source(), grade_task(), has_criteria()


# --------------------------------------------------------------------------- #
#  per-lab notebook state                                                      #
# --------------------------------------------------------------------------- #
def _nb(lab_id: str) -> dict:
    store = st.session_state.setdefault("_notebooks", {})
    if lab_id not in store:
        store[lab_id] = {"cells": [], "ns": None, "count": 0, "uid": 0}
    return store[lab_id]


def _seed(spec: dict) -> None:
    nb = _nb(spec["lab_id"])
    if nb["cells"]:
        return
    for t in spec["tasks"]:
        nb["uid"] += 1
        nb["cells"].append({
            "uid": nb["uid"], "task_id": t["id"],
            "src": f"# ===== Task {t['id']} — {t['title']} =====\n" + t.get("starter", ""),
            "out": "", "err": "", "n": None,
        })


def _add_cell(lab_id: str, after: int | None = None, task_id=None, src: str = "") -> None:
    nb = _nb(lab_id)
    nb["uid"] += 1
    cell = {"uid": nb["uid"], "task_id": task_id, "src": src, "out": "", "err": "", "n": None}
    nb["cells"].insert(len(nb["cells"]) if after is None else after + 1, cell)


def _new_ns(mode: str) -> dict:
    ns: dict = {"__name__": "__notebook__",
                "input": lambda *_a: _demo_input()}
    exec(compile(grader.preamble(mode), "<preamble>", "exec"), ns)  # noqa: S102
    return ns


_DEMO_Q = iter(["What is the standard notice period?", "How many casual leave days?",
                "exit", "exit", "exit"])


def _demo_input() -> str:
    return next(_DEMO_Q, "exit")


def _run_cell(lab_id: str, idx: int, mode: str) -> None:
    nb = _nb(lab_id)
    if nb["ns"] is None:
        nb["ns"] = _new_ns(mode)
    cell = nb["cells"][idx]
    cap = tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace")
    err = ""
    t0 = time.perf_counter()
    try:
        with contextlib.redirect_stdout(cap), contextlib.redirect_stderr(cap):
            exec(compile(cell["src"], f"<cell {idx + 1}>", "exec"), nb["ns"])  # noqa: S102
    except SystemExit:
        pass
    except BaseException:  # noqa: BLE001 — show every real failure
        err = traceback.format_exc()
    cap.seek(0)
    cell["out"] = cap.read()
    cap.close()
    cell["err"] = err
    cell["secs"] = time.perf_counter() - t0
    nb["count"] += 1
    cell["n"] = nb["count"]


def _run_all(lab_id: str, mode: str) -> None:
    nb = _nb(lab_id)
    nb["ns"] = _new_ns(mode)          # fresh kernel, like "Restart & Run All"
    nb["count"] = 0
    for i in range(len(nb["cells"])):
        _run_cell(lab_id, i, mode)


def _restart(lab_id: str) -> None:
    nb = _nb(lab_id)
    nb["ns"] = None
    nb["count"] = 0
    for c in nb["cells"]:
        c["out"] = c["err"] = ""
        c["n"] = None


def _accumulated_task_src(lab_id: str, upto_task_id: int, mode: str) -> str:
    """preamble + every task cell's source up to and including upto_task_id —
    what grader.build_namespace() executes for the runtime criteria."""
    nb = _nb(lab_id)
    codes = [c["src"] for c in nb["cells"]
             if c.get("task_id") is not None and c["task_id"] <= upto_task_id]
    return grader.assemble_source(codes, mode)


# --------------------------------------------------------------------------- #
#  UI                                                                          #
# --------------------------------------------------------------------------- #
def _keep_alive(lab_id: str) -> None:
    for c in _nb(lab_id)["cells"]:
        k = f"nbc_{lab_id}_{c['uid']}"
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]


def render_notebook(spec: dict, mode: str, dev: bool = False) -> None:
    lab_id = spec["lab_id"]
    _seed(spec)
    nb = _nb(lab_id)
    _keep_alive(lab_id)

    st.title("📓 Notebook")
    st.caption(f"Shared kernel · `{mode}` mode · one namespace across all cells "
               f"(`documents` → `chunks` → `vectorstore` → …). "
               f"Kernel {'**running**' if nb['ns'] is not None else 'not started'}.")

    a, b, c, d = st.columns(4)
    if a.button("▶▶ Run all", use_container_width=True):
        with st.spinner("Restart & run all…"):
            _run_all(lab_id, mode)
        st.rerun()
    if b.button("⟳ Restart kernel", use_container_width=True):
        _restart(lab_id)
        st.rerun()
    if c.button("＋ Add cell", use_container_width=True):
        _add_cell(lab_id)
        st.rerun()
    grade_click = d.button("★ Grade notebook", use_container_width=True, type="primary")

    st.divider()

    delete_idx = None
    for i, cell in enumerate(nb["cells"]):
        tag = f" · Task {cell['task_id']}" if cell.get("task_id") else ""
        marker = f"[{cell['n']}]" if cell["n"] else "[ ]"
        st.markdown(f"**`{marker}`**{tag}")
        key = f"nbc_{lab_id}_{cell['uid']}"
        st.session_state.setdefault(key, cell["src"])
        st.text_area("cell", key=key, height=170, label_visibility="collapsed")
        cell["src"] = st.session_state[key]

        r1, r2, r3, _ = st.columns([1, 1, 1, 5])
        if r1.button("▶ Run", key=f"run_{key}"):
            with st.spinner(f"Running cell {i + 1}…"):
                _run_cell(lab_id, i, mode)
            st.rerun()
        if r2.button("＋", key=f"add_{key}", help="Insert a cell below"):
            _add_cell(lab_id, after=i)
            st.rerun()
        if r3.button("✕", key=f"del_{key}", help="Delete this cell",
                     disabled=len(nb["cells"]) <= 1):
            delete_idx = i

        if cell["out"]:
            st.code(cell["out"], language="text")
        if cell["err"]:
            st.markdown("**Error** — real traceback:")
            st.code(cell["err"], language="text")
        st.markdown("<hr style='margin:6px 0;opacity:.25'>", unsafe_allow_html=True)

    if delete_idx is not None:
        nb["cells"].pop(delete_idx)
        st.rerun()

    # ---- grading --------------------------------------------------------- #
    if grade_click:
        if not grader.has_criteria(lab_id, 1):
            st.warning(f"No criterion rubric for `{lab_id}` yet — "
                       "the notebook still runs, but Grade only works for the RAG lab.")
            return
        st.subheader("Grade")
        task_cells = [c for c in nb["cells"] if c.get("task_id") is not None]
        by_task: dict[int, str] = {}
        for c in task_cells:                       # last cell per task wins
            by_task[c["task_id"]] = by_task.get(c["task_id"], "") + "\n" + c["src"]

        total = maxtotal = 0.0
        with st.spinner("Grading — analysing + executing your cells…"):
            for tid in sorted(by_task):
                if not grader.has_criteria(lab_id, tid):
                    continue
                src = _accumulated_task_src(lab_id, tid, mode)
                res = grader.grade_task(tid, by_task[tid], lab_id=lab_id,
                                        accumulated_source=src, mode=mode, dev=dev)
                total += res["score"]
                maxtotal += res["max_score"]
                ok = sum(1 for x in res["criteria"] if x["passed"])
                with st.expander(f"Task {tid} — {res['score']:.0f} / {res['max_score']}  "
                                 f"({ok}/{len(res['criteria'])} criteria)",
                                 expanded=res["score"] < res["max_score"]):
                    for x in res["criteria"]:
                        st.markdown(f"{'✅' if x['passed'] else '❌'} **{x['name']}** "
                                    f"— {x['earned']:g}/{x['points']:g} — {x['reason']}")
                    rt = res.get("runtime", {})
                    if not rt.get("executed"):
                        st.caption(f"⚠ cells did not run to completion "
                                   f"({rt.get('error')}) — runtime checks skipped")
        st.metric("Notebook total", f"{total:.0f} / {maxtotal:.0f}")
        st.caption("Same rubric as the per-task pages. Running successfully is not "
                   "enough — each criterion must be demonstrated by your code.")
