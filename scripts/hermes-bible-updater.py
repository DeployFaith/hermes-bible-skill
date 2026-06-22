#!/usr/bin/env python3
"""
Hermes Bible Skill Self-Updater

Fetches the latest llms.txt and llms-full.txt from hermesbible.com, compares generated reference
files against the current skill references, and updates when requested.

Safe defaults:
    - no arguments: dry-run / report only
    - --write: update files, but do not commit or push
    - --commit: write files and create a git commit
    - --push: requires --commit and pushes after committing

Usage:
    python3 scripts/hermes-bible-updater.py --dry-run --verbose
    python3 scripts/hermes-bible-updater.py --write
    python3 scripts/hermes-bible-updater.py --commit
    python3 scripts/hermes-bible-updater.py --commit --push
"""

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

LLMS_TXT_URL = "https://www.hermesbible.com/llms.txt"
LLMS_FULL_TXT_URL = "https://www.hermesbible.com/llms-full.txt"


def default_repo_dir() -> Path:
    """Return the repository/root directory inferred from this script path."""
    return Path(__file__).resolve().parent.parent


def default_hermes_home() -> Path:
    """Return HERMES_HOME or the conventional ~/.hermes directory."""
    return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser()


def default_skill_dir(repo_dir: Path) -> Path:
    """Pick a safe default skill directory.

    When the script is run from a cloned repo, update that repo. When the script
    has been copied into a Hermes scripts directory for cron, fall back to the
    installed skill under HERMES_HOME/skills/hermes-bible.
    """
    if (repo_dir / "SKILL.md").is_file() and (repo_dir / "references").is_dir():
        return repo_dir
    return default_hermes_home() / "skills" / "hermes-bible"


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path, Path]:
    """Resolve repo, skill, index, flows, and full-corpus paths.

    Defaults to the repo containing this script when run from a clone. If the
    script was copied elsewhere for cron, default to the installed skill under
    HERMES_HOME. `--skill-dir` / `HERMES_BIBLE_SKILL_DIR` and `--repo-dir` /
    `HERMES_BIBLE_REPO_DIR` override those defaults.
    """
    repo_dir = Path(args.repo_dir or os.environ.get("HERMES_BIBLE_REPO_DIR") or default_repo_dir()).expanduser().resolve()
    skill_dir = Path(args.skill_dir or os.environ.get("HERMES_BIBLE_SKILL_DIR") or default_skill_dir(repo_dir)).expanduser().resolve()
    index_file = skill_dir / "references" / "index.md"
    flows_file = skill_dir / "references" / "flows-catalog.md"
    full_file = skill_dir / "references" / "llms-full.md"
    return repo_dir, skill_dir, index_file, flows_file, full_file


def fetch_url(url: str) -> str | None:
    """Fetch a text URL from hermesbible.com."""
    try:
        req = Request(url, headers={"User-Agent": "Hermes-Bible-Skill/1.1"})
        with urlopen(req, timeout=60) as response:
            return response.read().decode("utf-8")
    except (URLError, TimeoutError) as e:
        print(f"ERROR: Failed to fetch {url}: {e}")
        return None


def fetch_llms_txt() -> str | None:
    """Fetch the latest llms.txt from hermesbible.com."""
    return fetch_url(LLMS_TXT_URL)


def fetch_llms_full_txt() -> str | None:
    """Fetch the latest llms-full.txt from hermesbible.com."""
    return fetch_url(LLMS_FULL_TXT_URL)


def normalize_url(url: str) -> str:
    """Convert hermesbible absolute URLs to site-relative URLs."""
    return url.replace("https://hermesbible.com", "").replace("https://www.hermesbible.com", "")


def parse_llms_txt(content: str) -> tuple[list[dict], list[dict]]:
    """Parse llms.txt into structured docs and flows."""
    docs: list[dict] = []
    flows: list[dict] = []
    current_section = None

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("### "):
            current_section = line[4:].strip()
            continue

        # Flow entries: - [Title](URL) (by Author): Description
        flow_match = re.match(r"^- \[(.+?)\]\((.+?)\)\s+\(by .+?\):\s*(.*)", line)
        if flow_match and current_section:
            title, url, desc = flow_match.groups()
            flows.append(
                {
                    "title": title.strip(),
                    "url": normalize_url(url).strip(),
                    "description": desc.strip()[:120],
                    "category": current_section,
                }
            )
            continue

        # Doc entries: - [Title](URL): Description
        doc_match = re.match(r"^- \[(.+?)\]\((.+?)\):\s*(.*)", line)
        if doc_match and current_section:
            title, url, desc = doc_match.groups()
            docs.append(
                {
                    "title": title.strip(),
                    "url": normalize_url(url).strip(),
                    "description": desc.strip()[:100],
                    "section": current_section,
                }
            )
            continue

    return docs, flows


def extract_urls(path: Path, prefix: str) -> set[str]:
    """Extract site-relative URLs from markdown links and backticked table cells."""
    urls: set[str] = set()
    if not path.exists():
        return urls

    content = path.read_text(encoding="utf-8")
    escaped = re.escape(prefix)
    for match in re.finditer(rf"\]\(({escaped}[^\)]+)\)", content):
        urls.add(match.group(1))
    for match in re.finditer(rf"`({escaped}[^`]+)`", content):
        urls.add(match.group(1))
    return urls


def generate_index_md(docs: list[dict], today: str | None = None) -> str:
    """Generate the full index.md content from parsed docs."""
    today = today or datetime.now().strftime("%Y-%m-%d")
    sections: dict[str, list[dict]] = {}
    for doc in docs:
        sections.setdefault(doc["section"], []).append(doc)

    lines = [
        "# Full Documentation Index",
        "",
        "Source: https://www.hermesbible.com",
        f"Last updated: {today}",
        "",
        "---",
        "",
    ]

    for section, section_docs in sections.items():
        lines.append(f"## {section} ({len(section_docs)} pages)")
        lines.append("")
        lines.append("| Page | URL |")
        lines.append("|------|-----|")
        for doc in section_docs:
            lines.append(f"| {doc['title']} | `{doc['url']}` |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_flows_md(flows: list[dict], today: str | None = None) -> str:
    """Generate the flows-catalog.md content from parsed flows."""
    today = today or datetime.now().strftime("%Y-%m-%d")
    categories: dict[str, list[dict]] = {}
    for flow in flows:
        categories.setdefault(flow["category"], []).append(flow)

    lines = [
        "# Flows Catalog — Real Hermes Workflows",
        "",
        "Source: https://www.hermesbible.com/flows",
        f"Last updated: {today}",
        "Community-built workflows, organized by category and intent.",
        "",
        "---",
        "",
    ]

    for cat, cat_flows in categories.items():
        lines.append(f"## {cat}")
        lines.append("")
        lines.append("| Flow | Summary | URL |")
        lines.append("|------|---------|-----|")
        for flow in cat_flows:
            desc = flow["description"][:80] + "..." if len(flow["description"]) > 80 else flow["description"]
            lines.append(f"| {flow['title']} | {desc} | `{flow['url']}` |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def normalize_text(text: str) -> str:
    """Normalize line endings and trailing whitespace for stable comparison."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def redact_secret_like_values(text: str) -> str:
    """Redact credential-like assignment values before storing mirrored corpus text.

    The upstream public corpus includes examples for tokens, API keys, passwords,
    and secrets. Keep the documentation useful while ensuring this repo does not
    preserve credential-looking values verbatim.
    """
    assignment = re.compile(
        r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b(\s*[:=]\s*)([\"']?)([^\"'\s`]+)([\"']?)"
    )

    def repl(match: re.Match) -> str:
        key, sep, open_quote, value, close_quote = match.groups()
        normalized = value.strip().lower()
        safe_placeholders = {
            "***",
            "[redacted]",
            "example",
            "dummy",
            "test",
            "changeme",
            "your-token",
            "your_token",
            "your-api-key",
            "your_api_key",
            "your-secret",
            "your_secret",
            "your-password",
            "your_password",
        }
        if normalized in safe_placeholders or normalized.startswith(("your", "example", "dummy", "test")):
            return match.group(0)
        return f"{key}{sep}{open_quote}[REDACTED]{close_quote}"

    return assignment.sub(repl, text)


def read_text_or_empty(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def file_status(path: Path, new_content: str) -> str:
    if not path.exists():
        return "changed"
    return "changed" if normalize_text(read_text_or_empty(path)) != normalize_text(new_content) else "unchanged"


def reference_file_statuses(
    index_file: Path,
    flows_file: Path,
    full_file: Path,
    new_index: str,
    new_flows_md: str,
    new_full_md: str | None,
) -> dict[str, str]:
    statuses = {
        str(index_file): file_status(index_file, new_index),
        str(flows_file): file_status(flows_file, new_flows_md),
    }
    if new_full_md is not None:
        statuses[str(full_file)] = file_status(full_file, new_full_md)
    return statuses


def changed_files(index_file: Path, flows_file: Path, new_index: str, new_flows_md: str) -> list[str]:
    statuses = {
        str(index_file): file_status(index_file, new_index),
        str(flows_file): file_status(flows_file, new_flows_md),
    }
    return [path for path, status in statuses.items() if status == "changed"]


def print_diff(path: Path, new_content: str, max_lines: int = 120) -> None:
    old_content = read_text_or_empty(path)
    diff = list(
        difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=str(path),
            tofile=f"{path} (generated)",
            lineterm="",
        )
    )
    if not diff:
        return
    print(f"\n  Diff preview for {path}:")
    for line in diff[:max_lines]:
        print(f"    {line}")
    if len(diff) > max_lines:
        print(f"    ... {len(diff) - max_lines} more diff lines omitted")


def ensure_clean_repo(repo_dir: Path, force: bool) -> None:
    """Stop before committing into a dirty repo unless explicitly forced."""
    result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True, check=True)
    if result.stdout.strip() and not force:
        print("ERROR: Repository has uncommitted changes. Commit/stash them or pass --force.")
        print(result.stdout.strip())
        sys.exit(2)


def atomic_write(path: Path, content: str) -> None:
    """Write content via temporary file + replace to avoid partial refs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def write_generated_files(
    index_file: Path,
    flows_file: Path,
    full_file: Path,
    new_index: str,
    new_flows_md: str,
    new_full_md: str | None,
) -> list[str]:
    """Write generated reference files and return files written."""
    written: list[str] = []

    if file_status(index_file, new_index) == "changed":
        atomic_write(index_file, new_index)
        written.append(str(index_file))
    if file_status(flows_file, new_flows_md) == "changed":
        atomic_write(flows_file, new_flows_md)
        written.append(str(flows_file))
    if new_full_md is not None and file_status(full_file, new_full_md) == "changed":
        atomic_write(full_file, new_full_md)
        written.append(str(full_file))
    return written


def sync_skill_refs_to_repo(skill_dir: Path, repo_dir: Path) -> list[str]:
    """Copy generated reference files into repo_dir when updating an installed skill."""
    if skill_dir == repo_dir:
        return []

    copied: list[str] = []
    refs_src = skill_dir / "references"
    refs_dst = repo_dir / "references"
    refs_dst.mkdir(parents=True, exist_ok=True)
    for name in ("index.md", "flows-catalog.md", "llms-full.md"):
        src = refs_src / name
        dst = refs_dst / name
        if src.exists() and normalize_text(read_text_or_empty(dst)) != normalize_text(src.read_text(encoding="utf-8")):
            atomic_write(dst, src.read_text(encoding="utf-8"))
            copied.append(str(dst))
    return copied


def git_info(repo_dir: Path) -> dict[str, str | None]:
    """Return best-effort git metadata for summaries."""
    info: dict[str, str | None] = {"branch": None, "sha_before": None, "sha_after": None, "remote": None}
    try:
        info["branch"] = subprocess.run(["git", "branch", "--show-current"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip() or None
        info["sha_before"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip() or None
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=repo_dir, capture_output=True, text=True)
        info["remote"] = remote.stdout.strip() or None if remote.returncode == 0 else None
    except (OSError, subprocess.CalledProcessError):
        pass
    return info


def update_sha_after(repo_dir: Path, info: dict) -> dict:
    try:
        info["sha_after"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        info["sha_after"] = info.get("sha_before")
    return info


def paths_for_git(repo_dir: Path, paths: list[str]) -> list[str]:
    """Return paths that are inside repo_dir, relative to repo_dir."""
    out: list[str] = []
    repo = repo_dir.resolve()
    for value in paths:
        path = Path(value).resolve()
        try:
            out.append(str(path.relative_to(repo)))
        except ValueError:
            continue
    return sorted(set(out))


def git_commit(repo_dir: Path, message: str, paths: list[str]) -> bool:
    """Commit known generated files. Returns True if a commit was created."""
    rel_paths = paths_for_git(repo_dir, paths)
    if not rel_paths:
        print("No generated repo files to commit.")
        return False
    subprocess.run(["git", "add", *rel_paths], cwd=repo_dir, check=True)
    result = subprocess.run(["git", "status", "--porcelain", "--", *rel_paths], cwd=repo_dir, capture_output=True, text=True, check=True)
    if not result.stdout.strip():
        print("No changes to commit.")
        return False
    subprocess.run(["git", "commit", "-m", message], cwd=repo_dir, check=True)
    return True


def git_push(repo_dir: Path) -> None:
    subprocess.run(["git", "push"], cwd=repo_dir, check=True)


def build_summary(
    *,
    docs: list[dict],
    flows: list[dict],
    new_docs: list[dict],
    new_flows: list[dict],
    removed_docs: set[str],
    removed_flows: set[str],
    changed: list[str],
    written: list[str],
    copied: list[str],
    committed: bool,
    pushed: bool,
    mode: str,
    repo_dir: Path,
    skill_dir: Path,
    file_statuses: dict[str, str],
    git_metadata: dict[str, str | None],
    args: argparse.Namespace,
) -> dict:
    return {
        "ok": True,
        "timestamp": datetime.now().isoformat(),
        "source_url": LLMS_TXT_URL,
        "full_source_url": LLMS_FULL_TXT_URL,
        "mode": mode,
        "dry_run": mode == "dry-run",
        "write": bool(args.write or args.commit),
        "commit": bool(args.commit),
        "push": bool(args.push),
        "hermes_home": str(default_hermes_home()),
        "repo_dir": str(repo_dir),
        "skill_dir": str(skill_dir),
        "new_docs": len(new_docs),
        "new_flows": len(new_flows),
        "removed_docs": len(removed_docs),
        "removed_flows": len(removed_flows),
        "total_docs": len(docs),
        "total_flows": len(flows),
        "file_statuses": file_statuses,
        "changed_files": changed,
        "written_files": written,
        "copied_files": copied,
        "committed": committed,
        "pushed": pushed,
        "branch": git_metadata.get("branch"),
        "commit_sha_before": git_metadata.get("sha_before"),
        "commit_sha_after": git_metadata.get("sha_after"),
        "remote": git_metadata.get("remote"),
        "warnings": [],
        "errors": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Hermes Bible skill references from llms.txt")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying (default when no write/commit/push flag is set)")
    parser.add_argument("--write", action="store_true", help="Write generated reference files without committing")
    parser.add_argument("--commit", action="store_true", help="Write generated files and create a git commit")
    parser.add_argument("--push", action="store_true", help="Push after committing (requires --commit)")
    parser.add_argument("--force", action="store_true", help="Allow commit when repo has pre-existing uncommitted changes")
    parser.add_argument("--skill-dir", help="Installed skill directory to update; defaults to repo dir or HERMES_BIBLE_SKILL_DIR")
    parser.add_argument("--repo-dir", help="Repo directory for commits; defaults to this script's parent repo or HERMES_BIBLE_REPO_DIR")
    parser.add_argument("--skip-full", action="store_true", help="Skip fetching/updating references/llms-full.md")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    if args.push and not args.commit:
        print("ERROR: --push requires --commit.")
        sys.exit(2)

    repo_dir, skill_dir, index_file, flows_file, full_file = resolve_paths(args)
    should_write = args.write or args.commit
    dry_run = args.dry_run or not should_write
    mode = "dry-run" if dry_run else "commit" if args.commit else "write"

    print("=" * 60)
    print("Hermes Bible Self-Updater")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    if args.verbose:
        print(f"Repo dir:  {repo_dir}")
        print(f"Skill dir: {skill_dir}")
        print(f"Mode:      {mode}")

    print("\n[1/5] Fetching llms.txt...")
    content = fetch_llms_txt()
    if not content:
        sys.exit(1)
    if args.verbose:
        print(f"  Fetched {len(content)} bytes")

    full_content: str | None = None
    if not args.skip_full:
        print("  Fetching llms-full.txt...")
        full_content = fetch_llms_full_txt()
        if full_content is None:
            sys.exit(1)
        if args.verbose:
            print(f"  Fetched {len(full_content)} full-corpus bytes")

    print("[2/5] Parsing content...")
    docs, flows = parse_llms_txt(content)
    print(f"  Found {len(docs)} doc pages, {len(flows)} flows")

    print("[3/5] Comparing with current...")
    current_doc_urls = extract_urls(index_file, "/docs/")
    current_flow_urls = extract_urls(flows_file, "/flows/")
    new_docs = [d for d in docs if d["url"] not in current_doc_urls]
    new_flows = [f for f in flows if f["url"] not in current_flow_urls]
    removed_docs = current_doc_urls - {d["url"] for d in docs}
    removed_flows = current_flow_urls - {f["url"] for f in flows}

    new_index = generate_index_md(docs)
    new_flows_md = generate_flows_md(flows)
    new_full_md = normalize_text(redact_secret_like_values(full_content)) if full_content is not None else None
    file_statuses = reference_file_statuses(index_file, flows_file, full_file, new_index, new_flows_md, new_full_md)
    changed = [path for path, status in file_statuses.items() if status == "changed"]
    git_metadata = git_info(repo_dir)

    print(f"  New docs: {len(new_docs)}")
    print(f"  New flows: {len(new_flows)}")
    print(f"  Removed docs: {len(removed_docs)}")
    print(f"  Removed flows: {len(removed_flows)}")
    print(f"  Changed files: {len(changed)}")

    if new_docs:
        print("\n  New documentation pages:")
        for doc in new_docs[:10]:
            print(f"    + {doc['title']} ({doc['section']})")
        if len(new_docs) > 10:
            print(f"    ... and {len(new_docs) - 10} more")

    if new_flows:
        print("\n  New flows:")
        for flow in new_flows[:10]:
            print(f"    + {flow['title']} ({flow['category']})")
        if len(new_flows) > 10:
            print(f"    ... and {len(new_flows) - 10} more")

    if args.verbose and changed:
        if str(index_file) in changed:
            print_diff(index_file, new_index)
        if str(flows_file) in changed:
            print_diff(flows_file, new_flows_md)
        if str(full_file) in changed:
            print(f"\n  Diff preview for {full_file}: full corpus changed; diff omitted because the file is large.")

    written: list[str] = []
    copied: list[str] = []
    committed = False
    pushed = False

    if not changed:
        print("\n✅ No changes detected. Skill is up to date.")
    elif dry_run:
        print("\n[DRY RUN] No changes applied. Re-run with --write to update files.")
    else:
        if args.commit:
            ensure_clean_repo(repo_dir, args.force)

        print("\n[4/5] Writing generated reference files...")
        written = write_generated_files(index_file, flows_file, full_file, new_index, new_flows_md, new_full_md)
        for path in written:
            print(f"  Updated: {path}")

        copied = sync_skill_refs_to_repo(skill_dir, repo_dir)
        for path in copied:
            print(f"  Synced to repo: {path}")

        if args.commit:
            print("[5/5] Committing changes...")
            parts = []
            if new_docs:
                parts.append(f"{len(new_docs)} new docs")
            if new_flows:
                parts.append(f"{len(new_flows)} new flows")
            if removed_docs:
                parts.append(f"{len(removed_docs)} docs removed")
            if removed_flows:
                parts.append(f"{len(removed_flows)} flows removed")
            if changed and not parts:
                parts.append(f"{len(changed)} reference files changed")
            commit_msg = f"chore: auto-update from hermesbible.com — {', '.join(parts)}"
            commit_paths = written + copied
            committed = git_commit(repo_dir, commit_msg, commit_paths)
            git_metadata = update_sha_after(repo_dir, git_metadata)
            if args.push and committed:
                print("Pushing changes...")
                git_push(repo_dir)
                pushed = True
        else:
            print("[5/5] Skipping commit/push; pass --commit and optionally --push to publish.")

    git_metadata = update_sha_after(repo_dir, git_metadata)
    summary = build_summary(
        docs=docs,
        flows=flows,
        new_docs=new_docs,
        new_flows=new_flows,
        removed_docs=removed_docs,
        removed_flows=removed_flows,
        changed=changed,
        written=written,
        copied=copied,
        committed=committed,
        pushed=pushed,
        mode=mode,
        repo_dir=repo_dir,
        skill_dir=skill_dir,
        file_statuses=file_statuses,
        git_metadata=git_metadata,
        args=args,
    )
    print("\n--- UPDATE SUMMARY ---")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
