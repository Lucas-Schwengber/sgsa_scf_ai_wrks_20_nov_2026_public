---
title: SGSA/SCF AI workshop 11-20-2026
created: 2026-11-19
updated: 2026-11-19
authors: Lucas da Rocha Schwengber (L), CLAUDE (C)
---

This repo contain the materials for the tutorial and discussion of the SGSA/SCF AI workshop on 11-20-2026.

## Tutorial files (L)

`tutorial/` contains the discussion and the brief recap of skills and hooks.

## Instructions + repo after run (L)

`notes/threads/benchmark_gt/instructions.md` contains a short note providing instructions for the model to execute. Switch to the `after_run` branch to see what the outputs look like. 

## Repository structure (L+C)

| Directory | Contents |
|---|---|
| `src/` | All code, split into the subdirectories below.
| `src/global/` | Reusable code. Nothing in it refers to a specific study. May include packages and general utility scripts.
| `src/experiments/` | Code for specific studies/tasks.
| `src/tests/` | Unit tests for code.
| `data/` | Raw inputs data from diverse sources.
| `outputs/` | Everything the code produces, split into the subdirectories below.
| `outputs/runs/` | Heavy run artifacts (raw arrays, checkpoints, logs), one directory per run (naming below).
| `outputs/summaries/` | Light, final products (summary tables, figures).
| `notes/` | Plans, reports and other notes, organized by threads (see below).

Extras:

| Directory | Contents |
|---|---|
| `overleaf/` | Gitignored directory linked with overleaf git.

`src/experiments/`, `outputs/runs/` and `outputs/summaries/` should save files with a structure mirroring the structure of `notes/threads/` for ease of navigation.

- **Run naming:** a run is saved in `outputs/runs/<thread>/<sub_thread>/YYYY-MM-DD_<slug>/`, with its raw results and a `config.json` (parameters, seeds, git commit). `outputs/runs/` is gitignored; `outputs/summaries/` is tracked.
- **Reusable package:** `src/global/ot_1d/` is installed in editable mode and imported as `import ot_1d` (`global` is a Python keyword, so `src.global` cannot be imported).

### Environment (L+C)

The code runs in a virtual environment in `.venv/` (gitignored, prompt `ot_1d`). To set it up:

```bash
python3 -m venv --prompt ot_1d .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

Tests: `.venv/bin/pytest`. After adding a dependency, list it in `pyproject.toml` and re-export with `.venv/bin/pip freeze --exclude-editable > requirements.txt`.

### Threads 

`notes/threads` contains major tasks/topics being pursued in the repo. The overall structure is:

```
notes/
  threads/<thread>/
    <sub_thread>/               optional: a piece of work with its own plan.md and report.md
```

- **Tables and figures:** in `outputs/summaries/<thread>/<sub_thread>/`, not in `notes/`.