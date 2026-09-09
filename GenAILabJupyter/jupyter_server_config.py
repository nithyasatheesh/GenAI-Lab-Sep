"""JupyterLab server config for the hosted lab.

Single-container deployment: fine for a demo, a class working one-at-a-time, or
a per-learner container spawned by JupyterHub. For a real multi-learner
assessment with isolation + LTI, front this image with JupyterHub
(see BROWSER_CODING_ENV_DESIGN.md).
"""
import os

c = get_config()  # noqa: F821  (injected by jupyter)

c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = int(os.environ.get("PORT", "8888"))
c.ServerApp.open_browser = False
c.ServerApp.root_dir = "/home/learner/work"

# Access control: token from the platform secret JUPYTER_TOKEN.
# "" = no token — only acceptable when the hosting platform already gates access
# (e.g. a private Hugging Face Space) or for local use.
c.ServerApp.token = os.environ.get("JUPYTER_TOKEN", "")
c.ServerApp.password = ""

# Behind a reverse proxy (HF Spaces / Render / Railway all proxy the port):
c.ServerApp.allow_origin = "*"
c.ServerApp.allow_remote_access = True
c.ServerApp.trust_xheaders = True
c.ServerApp.tornado_settings = {"headers": {"Content-Security-Policy": "frame-ancestors 'self' *"}}

# Keep learners inside the work dir; don't let the tab sit idle forever.
c.ContentsManager.allow_hidden = False
c.MappingKernelManager.cull_idle_timeout = int(os.environ.get("CULL_IDLE", "3600"))
c.MappingKernelManager.cull_interval = 300
c.MappingKernelManager.cull_connected = True

# Default the kernel to Mock mode so nothing needs an API key.
os.environ.setdefault("SANDBOX_MODE", "mock")
