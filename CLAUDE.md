# Working rules for this project

The owner set these rules. Every session follows them. The full brief is
`C:\Users\USER\Downloads\aesthetics-claude-code-prompt.md`, outside the repo; re-read it
at the start of a session.

## Working with the owner

- **The owner does not micromanage.** Make reasonable calls yourself and record each in
  `LOG.md` with one line of reasoning. Stop and ask only at the gates, or when a decision is
  genuinely the owner's: spending money, pushing, discarding data, or changing an approved
  report.
- **Talk to the owner in English.** Any Chinese you write must read as natural native Chinese,
  never as a translation.
- **Honest results matter more than positive ones.** Report failures, your own bugs found
  after the fact, and caveats plainly, in `LOG.md` and the reports.
- **If the facts change after an approval, ask again.** For example, when an approval to set
  data aside was given for an hour of runs and it turns out to be twenty hours.

## Ground rules from the brief

- **Shared machine.**
  - Work only inside the project folder. Change nothing system-wide, install no drivers, and
    ask before anything that needs administrator rights.
  - Leave no servers or background jobs running.
  - Never change PowerShell's execution policy.
- **GPU** (RTX 4090 Laptop, 16 GB). Check free memory first. Run one model at a time: two
  models filling 16 GB made both 7 to 28 times slower. Make every long job resumable.
- **Stimuli are generated in code only.** No reproductions of artworks or real designs,
  public-domain ones included.
- **Spend: zero by default.** Paid API use needs the owner's explicit approval. Tier 2
  (Claude models) is unconfirmed: never look for `ANTHROPIC_API_KEY`.
- **Secrets.**
  - Read keys from the environment or a hidden prompt. Never write them to disk, logs,
    shell history or commits.
  - Never use a key you happen to see on screen.
- **No tuning on test stimuli.** Develop on dev seeds, freeze, then run fresh seeds once.
- **Repo.** One local git repo, never pushed without the owner's say. Commits use the
  repo-local placeholder identity.
- **Reproducibility.** Fixed seeds, pinned model versions, and one command per reported
  number.
- **Out of scope:** real artworks, new human data, fine-tuning, image-generation models, and
  any claim about which model has better taste.

## Pre-registration discipline

- `PLAN.md` holds the pre-registration and its amendments. Each amendment must be made
  before the data it concerns are opened, and must say what had been seen.
- `FROZEN.json` (main run) and `FROZEN_API.json` (NVIDIA addendum) pin the code. Test
  commands refuse to run if a frozen path (`aesx.freeze.FROZEN_PATHS`, or `API_PATHS` in
  `scripts/run_api.py`) has changed. Put extensions in new files. If a frozen file must
  change, amend `PLAN.md`, re-freeze, and log why.
- Exploratory work is labelled post hoc, and it never replaces a pre-registered number or
  verdict. `reports/main.md` is approved (Gate 3); changes to it are the owner's call.
- **NVIDIA addendum:** do not read replies in `runs/nvidia-test/` until the owner says the
  run has stopped. While it runs, look only at counts, timestamps, retries and rate-limit
  waits. `runs/nvidia-test-seedcoupled/` holds an invalid earlier run, set aside unopened;
  never analyse it.

## Environment

- **Windows 11, PowerShell 5.1.**
  - In Claude's shell, run `. .\scripts\env.ps1` first. It sets up the project-local uv,
    CPython and caches.
  - The owner's terminal blocks `.ps1` scripts, so give the owner commands that call
    `.\.venv\Scripts\python.exe` directly.
- **Edit files with the Edit/Write tools,** never through Get-Content/Set-Content (encoding
  damage).
- **`python -c` quoting breaks in PowerShell 5.1.** Write a small script in the scratchpad
  instead.

## NVIDIA free API (Tier 2 addendum)

- **The key is the owner's and is never stored.** The scripts ask for it at a hidden prompt.
  - The owner pastes it once with right-click in a terminal tab Claude opens with
    `run_in_terminal`, then checks for "Key received: 70 characters".
  - Each new process asks again, so batch work into one command where possible.
- **NVIDIA honours request seeds,** so every request needs its own seed. `scripts/run_api.py`
  derives one from SHA-256 (seed check, 2026-11-19).
- **The free tier throttles the account** to about 4 to 10 requests a minute after heavy use.
  - The test run retries skipped requests and pauses through rate limits and outages, and it
    stops itself at its fixed stop time (2026-11-28 00:00 UTC).
  - If it stops early (Ctrl+C, a reboot), the same command resumes it.
  - Check on it now and then with timing fields only: a stopped run once went unnoticed for
    60 hours.
- **Trial terms:** evaluation only, not production. Do not distribute generated replies:
  they stay in this local repo, and reports give aggregates. NVIDIA may withdraw a model at
  any time.
