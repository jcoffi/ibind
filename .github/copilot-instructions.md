Repository onboarding guide for Copilot agents

Purpose
- Give you everything you need to make high‑quality changes quickly, without trial‑and‑error or excessive searching.
- Keep CI green by mirroring the project’s validation steps exactly.
- Trust these instructions first. Only search the repo if information here is incomplete or demonstrably incorrect.

1) What this repository is
- Name: ibind (unofficial Python client for Interactive Brokers Client Portal Web API a.k.a. Web API 1.0/CPAPI 1.0).
- Functionality: Provides REST and WebSocket client classes plus helpers for headless OAuth 1.0a auth. Two main entry points:
  - IbkrClient (REST)
  - IbkrWsClient (WebSocket)
- Status: Beta. Packaging published to PyPI (dist/ contains historical wheels/tars).
- Primary languages and tooling
  - Python library targeting Python 3.8+ (CI runs 3.10–3.13 on Ubuntu and Windows).
  - Linting via Ruff; security scanning via Bandit.
  - Packaging via setuptools/pyproject; docs via pydoc‑markdown (optional, not part of CI).
- Repo size: ~57 MB (includes many built artifacts in dist/).

2) High‑level layout and key files
- Root
  - README.md: overview, examples, badges, links to wiki.
  - Makefile: install, lint, scan, clean. Note: there is no "format" target.
  - pyproject.toml: project metadata, dependencies, Ruff configuration, build backend.
  - requirements.txt, requirements-oauth.txt, requirements-dev.txt: runtime, OAuth, and dev deps.
  - setup.cfg/setup.py: legacy packaging bits.
  - examples/: runnable REST/WS examples (require valid IBKR connectivity/credentials).
  - ibind/: library source
    - base/: core REST/WebSocket and queue/subscription utilities
    - client/: IbkrClient, IbkrWsClient, mixins, definitions, utils
    - oauth/: OAuth 1.0a implementation and config dataclasses
    - support/: logging, errors, parallel execution, misc utils
    - var.py: environment-backed configuration (IBIND_* variables)
  - test/: helper utilities for logging assertions (no CI test step configured).
  - .workflows/ci.yml: CI runs make install → make lint → make scan on master and PRs.

3) How to set up your environment (bootstrap) — always do this first
- Python: use 3.10–3.13 to match CI. Create/activate a virtualenv.
- Install dependencies (this is required before any lint/scan targets will work):
  - make install
  - This runs:
    - pip install -r requirements.txt
    - pip install -r requirements-oauth.txt
    - pip install -r requirements-dev.txt
  - Notes:
    - Linting will fail with "ruff: No such file or directory" until dev deps are installed.
    - OAuth features require pycryptodome; installed via requirements-oauth.txt.

4) Build, validate, and package
- Lint (Ruff)
  - Command: make lint
  - Behavior: runs ruff check --fix. It may auto-fix issues; re-run to confirm clean.
  - Preconditions: run make install first.
- Security scan (Bandit)
  - Command: make scan
  - Behavior: bandit -r . -ll -x site-packages
  - Preconditions: run make install first.
- Combined checks
  - DO NOT use make check-all. It depends on a missing format target and will error after lint/scan.
- Clean
  - Command: make clean
  - Behavior: removes pyc/__pycache__.
- Build package artifacts
  - Command sequence:
    - python -m pip install --upgrade build
    - python -m build
  - Outputs: sdist and wheel in dist/.
- Editable install (for local dev)
  - Command: pip install -e .
- Import smoke test (quick sanity)
  - Python snippet:
    - import ibind; from ibind import IbkrClient; c = IbkrClient(use_oauth=False); print(c.base_url)

5) Running examples and the library (runtime expectations)
- Network backends
  - REST defaults (if not using OAuth): https://127.0.0.1:5000/v1/api/ (constructed from host/port/base_route in IbkrClient).
  - If you see "400 Bad Request: no bridge", call client.initialize_brokerage_session() first (CP Gateway requirement) or enable proper OAuth.
- OAuth 1.0a (headless)
  - Requires environment variables and key files. Install OAuth deps (requirements-oauth.txt).
  - Set IBIND_USE_OAUTH=true and provide OAuth 1.0a values (see Section 6). The client will:
    - Generate and validate a live session token.
    - Optionally start a tickler to keep the session alive.
    - Optionally initialize the brokerage session.
- Examples directory
  - examples/rest_*.py and examples/ws_*.py demonstrate basic to advanced usage.
  - Prerequisites: Working REST/WS URLs and credentials (OAuth or CP Gateway). Without them, network calls will fail.

6) Configuration via environment variables (ibind/var.py)
- General
  - IBIND_USE_SESSION (default True): persistent session for REST.
  - IBIND_AUTO_REGISTER_SHUTDOWN (default True): auto register shutdown handler.
- Logging
  - IBIND_LOG_TO_CONSOLE (default True), IBIND_LOG_TO_FILE (default True), IBIND_LOG_LEVEL (default INFO), IBIND_LOG_FORMAT, IBIND_LOGS_DIR.
  - Use ibind.support.logs.ibind_logs_initialize to configure logging; file handler rotates daily.
- IBKR endpoints and behavior
  - IBIND_REST_URL, IBIND_WS_URL: base URLs (non‑OAuth flows).
  - IBIND_ACCOUNT_ID: account id used in requests.
  - IBIND_CACERT: path to CA certificate, or False to disable SSL verification.
  - WS tuning: IBIND_WS_PING_INTERVAL, IBIND_WS_MAX_PING_INTERVAL, IBIND_WS_TIMEOUT, IBIND_WS_SUBSCRIPTION_RETRIES, IBIND_WS_SUBSCRIPTION_TIMEOUT, IBIND_WS_LOG_RAW_MESSAGES.
- OAuth common toggles
  - IBIND_USE_OAUTH (default False)
  - IBIND_INIT_OAUTH (default True)
  - IBIND_INIT_BROKERAGE_SESSION (default True)
  - IBIND_MAINTAIN_OAUTH (default True)
  - IBIND_SHUTDOWN_OAUTH (default True)
  - IBIND_TICKLER_INTERVAL (seconds)
- OAuth 1.0a specifics (ibind/oauth/oauth1a.py)
  - IBIND_OAUTH1A_REST_URL (default https://api.ibkr.com/v1/api/)
  - IBIND_OAUTH1A_WS_URL (wss URL)
  - IBIND_OAUTH1A_LIVE_SESSION_TOKEN_ENDPOINT (default oauth/live_session_token)
  - IBIND_OAUTH1A_ACCESS_TOKEN
  - IBIND_OAUTH1A_ACCESS_TOKEN_SECRET
  - IBIND_OAUTH1A_CONSUMER_KEY
  - IBIND_OAUTH1A_DH_PRIME (hex)
  - IBIND_OAUTH1A_ENCRYPTION_KEY_FP (path to private key)
  - IBIND_OAUTH1A_SIGNATURE_KEY_FP (path to private key)
  - IBIND_OAUTH1A_DH_GENERATOR
  - IBIND_OAUTH1A_REALM (e.g., limited_poa or test_realm)
  - All required fields are validated; missing values or missing key files raise clear errors.

7) CI expectations and how to keep PRs green
- Workflow: .workflows/ci.yml
  - Matrix: Python [3.10, 3.11, 3.12, 3.13] on ubuntu-latest and windows-latest.
  - Steps: actions/checkout → make install → make lint → make scan.
- What this means for you:
  - Always run make install first; then make lint and make scan locally before pushing.
  - Do not introduce code that fails Ruff or Bandit; prefer using pathlib and avoid platform‑specific paths.
  - Avoid relying on non‑Windows shell behaviors in code or tooling; CI runs on Windows too.

8) Known pitfalls and mitigations
- make lint without prior install fails (ruff missing). Fix: run make install first.
- make check-all fails due to missing "format" target. Avoid it; run make lint and make scan separately.
- Docs build (build_docs.sh) is optional and will fail/hang unless you install the CLI:
  - pip install pydoc-markdown mkdocs && ./build_docs.sh
- Network operations require valid IBKR endpoints and credentials. Without these, examples and some client methods will fail at runtime.
- When using OAuth 1.0a, ensure pycryptodome is installed and key files exist at the configured paths; otherwise initialization will raise.

9) Where to change things (fast navigation)
- Core clients
  - ibind/client/ibkr_client.py: REST client; OAuth init; request header handling; helpful error mapping.
  - ibind/client/ibkr_ws_client.py: WebSocket client; IbkrWsKey enum; subscription and queue management.
  - ibind/client/ibkr_client_mixins/: REST endpoint groupings (accounts, marketdata, orders, portfolio, session, etc.).
  - ibind/client/ibkr_utils.py: helpers (StockQuery, order request building, question/answer automation, tickler, etc.).
- Shared infrastructure
  - ibind/base/rest_client.py: base REST client, retry/timeout/session, daily rotating file logger.
  - ibind/base/ws_client.py: base WS client (lifecycle, ping, reconnection) used by IbkrWsClient.
  - ibind/base/subscription_controller.py, ibind/base/queue_controller.py: subscription orchestration and queue wrappers.
  - ibind/support/*.py: logging, parallel execution, enums/utilities, error types.
  - ibind/var.py: all IBIND_* env vars with defaults.
- Config and pipelines
  - pyproject.toml: Ruff rules (E/W/S/N/PL) with ignores (line length, magic values, etc.), line length 150; formatter preferences.
  - .workflows/ci.yml: exact CI steps to replicate locally.
  - Makefile: canonical local commands (install, lint, scan, clean).

10) Minimal local validation checklist before committing
- make install
- make lint
- make scan
- Optional quick runtime check (no network):
  - python -c "import ibind; from ibind import IbkrClient; IbkrClient(use_oauth=False)"

Trust these instructions first. Search the repo for details only if a step here is missing for your task or demonstrably incorrect.
