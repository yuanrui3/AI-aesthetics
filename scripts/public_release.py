"""Rebuild the public copy of this repository, check it, and (with --push) publish it.

    .\\.venv\\Scripts\\python.exe scripts/public_release.py           # rebuild public_release/ and check it
    .\\.venv\\Scripts\\python.exe scripts/public_release.py --push    # ... then push it, if every check passes
    .\\.venv\\Scripts\\python.exe scripts/public_release.py --push --dry-run   # all of that except sending

The public copy is a git-filter-repo rewrite of this repository's full history.
- Every `runs/nvidia-*` path is removed. NVIDIA's API Trial Terms (4.2) do not allow
  generated replies to be redistributed.
- Local user names in file paths are replaced as listed in `.tools/release/replacements.txt`.
  That file is git-ignored, because it names them.
- The public remote's URL is read from `.tools/release/remote.txt`, also git-ignored.
- The filter tool lives in `.tools/release-venv`: `uv pip install git-filter-repo`.

The rewrite is deterministic, so a rebuild keeps the hashes of commits already published, and
an update is a plain fast-forward. The push never forces. It goes ahead only if:
- every privacy check passes;
- the head already published is an ancestor of the new head;
- git can authenticate without asking. Prompts are switched off, so an unattended run fails
  instead of waiting for a sign-in.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public_release"
TOOLS = ROOT / ".tools" / "release"
FILTER = ROOT / ".tools" / "release-venv" / "Scripts" / "git-filter-repo.exe"
PLACEHOLDER = ("aesthetics-experiment (local)", "local@invalid")
NO_PROMPT = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}


def git(*args, cwd=OUT, check=True, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=check, env=env)


def _rm_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rebuild() -> None:
    if OUT.exists():
        shutil.rmtree(OUT, onerror=_rm_readonly)
    git("clone", "-q", "--no-local", str(ROOT), str(OUT), cwd=ROOT)
    repl = TOOLS / "replacements.txt"
    subprocess.run([str(FILTER), "--invert-paths", "--path-glob", "runs/nvidia-*", "--replace-text", str(repl),
                    "--replace-message", str(repl), "--force"], cwd=OUT, check=True, capture_output=True)
    git("config", "user.name", PLACEHOLDER[0])
    git("config", "user.email", PLACEHOLDER[1])


def name_patterns() -> list[tuple[str, bool]]:
    """(pattern, is_regex) for each name the replacements file removes."""
    out = []
    for line in (TOOLS / "replacements.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "==>" not in line:
            continue
        left = line.split("==>")[0]
        if left.startswith("regex:"):
            out.append((left[len("regex:"):].replace("(?i)", ""), True))
        elif left.startswith("literal:"):
            out.append((left[len("literal:"):], False))
        else:
            out.append((left, False))
    return out


def grep_all(pattern: str, regex: bool, revs: list[str]) -> list[str]:
    r = git("grep", "-I", "-i", "-l", "-E" if regex else "-F", pattern, *revs, check=False)
    return [x for x in r.stdout.splitlines() if x.strip()]


def checks() -> list[tuple[str, bool, str]]:
    revs = git("rev-list", "--all").stdout.split()
    res = []
    paths = {p for p in git("log", "--all", "--name-only", "--format=").stdout.splitlines() if p.startswith("runs/nvidia-")}
    res.append(("no NVIDIA reply files in any commit", not paths, f"{len(paths)} paths"))
    hits = [h for pat, rx in name_patterns() for h in grep_all(pat, rx, revs)]
    res.append(("no local user name in any file of any commit", not hits, f"{len(hits)} hits"))
    msgs = git("log", "--all", "--format=%B").stdout
    bad_msg = [p for p, rx in name_patterns() if (re.search(p, msgs, re.I) if rx else p.lower() in msgs.lower())]
    res.append(("no local user name in commit messages", not bad_msg, f"{len(bad_msg)} patterns"))
    keys = grep_all(r"nvapi-[A-Za-z0-9_-]{20,}", True, revs)
    res.append(("no key-like strings in any commit", not keys, f"{len(keys)} hits"))
    ids = {line for line in git("log", "--all", "--format=%an <%ae>%n%cn <%ce>").stdout.splitlines() if line.strip()}
    ok_id = ids == {f"{PLACEHOLDER[0]} <{PLACEHOLDER[1]}>"}
    res.append(("only the placeholder identity", ok_id, ", ".join(sorted(ids))))
    return res


def push(dry_run: bool = False) -> int:
    url = (TOOLS / "remote.txt").read_text(encoding="utf-8").strip()
    git("remote", "add", "origin", url)
    ls = git("ls-remote", "origin", "refs/heads/main", check=False, env=NO_PROMPT)
    if ls.returncode != 0:
        print(f"Not pushed: cannot reach the public repository ({ls.stderr.strip()[:200]}).")
        return 3
    published = ls.stdout.split()[0] if ls.stdout.strip() else None
    if published:
        if published == git("rev-parse", "HEAD").stdout.strip():
            print("Nothing to push: the public repository is already up to date.")
            return 0
        if git("merge-base", "--is-ancestor", published, "HEAD", check=False).returncode != 0:
            # Commits were made on GitHub itself (the owner added .zenodo.json there, for example).
            # Keep them: merge them in, so the push stays a fast-forward and nothing on GitHub is lost.
            git("fetch", "-q", "origin", "refs/heads/main:refs/remotes/origin/main", env=NO_PROMPT)
            if git("merge-base", "HEAD", "origin/main", check=False).returncode != 0:
                print("Not pushed: the public repository shares no history with the rebuild.")
                return 4
            m = git("merge", "--no-ff", "--no-edit", "-m", "Merge the changes made on GitHub", "origin/main", check=False)
            if m.returncode != 0:
                git("merge", "--abort", check=False)
                print(f"Not pushed: merging the changes made on GitHub conflicted.\n{(m.stdout + m.stderr).strip()[-400:]}")
                return 4
            bad = [p for p in git("ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines() if p.startswith("runs/nvidia-")]
            if bad:
                print(f"Not pushed: after the merge, {len(bad)} NVIDIA reply files are in the tree.")
                return 4
            print(f"Merged {len(git('rev-list', 'HEAD..origin/main').stdout.split()) or 'the'} GitHub-only commit(s) "
                  f"from {published[:10]}.")
    p = git("push", *(["--dry-run"] if dry_run else []), "origin", "HEAD:refs/heads/main", check=False, env=NO_PROMPT)
    print((p.stdout + p.stderr).strip()[-600:])
    if p.returncode != 0:
        print("Not pushed: git could not push without a sign-in prompt. Push by hand: "
              "git -C public_release push origin HEAD:refs/heads/main")
        return 5
    print("Dry run: a push would succeed; nothing was sent." if dry_run else "Pushed.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--push", action="store_true", help="push to the public repository if every check passes")
    ap.add_argument("--dry-run", action="store_true", help="with --push: do everything except send the commits")
    a = ap.parse_args()
    for need in (FILTER, TOOLS / "replacements.txt", TOOLS / "remote.txt"):
        if not need.exists():
            print(f"Missing {need.relative_to(ROOT)}; see this script's docstring.", file=sys.stderr)
            return 2
    if git("status", "--porcelain", "--untracked-files=no", cwd=ROOT).stdout.strip():
        print("Note: this repository has uncommitted changes to tracked files; the public copy is built from commits only.")
    rebuild()
    n = git("rev-list", "--count", "HEAD").stdout.strip()
    head = git("log", "-1", "--format=%h %s").stdout.strip()
    print(f"Rebuilt public_release/: {n} commits, head {head}")
    ok = True
    for name, passed, detail in checks():
        print(f"  {'PASS' if passed else 'FAIL'}  {name} ({detail})")
        ok &= passed
    if not ok:
        print("Not pushed: a privacy check failed.")
        return 1
    return push(dry_run=a.dry_run) if a.push else 0


if __name__ == "__main__":
    sys.exit(main())
