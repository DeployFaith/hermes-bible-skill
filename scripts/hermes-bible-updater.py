#!/usr/bin/env python3
"""
Hermes Bible Skill Self-Updater

Fetches the latest llms.txt from hermesbible.com, compares against
the current skill references, and updates if there are changes.

Usage:
    python3 update-hermes-bible.py [--dry-run] [--verbose]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Paths
SKILL_DIR = Path.home() / ".hermes" / "profiles" / "katana" / "skills" / "hermes-bible"
REPO_DIR = Path.home() / "hermes-bible-skill"
LLMS_TXT_URL = "https://www.hermesbible.com/llms.txt"
INDEX_FILE = SKILL_DIR / "references" / "index.md"
FLOWS_FILE = SKILL_DIR / "references" / "flows-catalog.md"

def fetch_llms_txt():
    """Fetch the latest llms.txt from hermesbible.com."""
    try:
        req = Request(LLMS_TXT_URL, headers={"User-Agent": "Hermes-Bible-Skill/1.0"})
        with urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
    except (URLError, TimeoutError) as e:
        print(f"ERROR: Failed to fetch llms.txt: {e}")
        return None

def parse_llms_txt(content):
    """Parse llms.txt into structured docs and flows."""
    docs = []
    flows = []
    current_section = None
    
    for line in content.split("\n"):
        line = line.strip()
        
        # Section headers
        if line.startswith("### "):
            current_section = line[4:].strip()
            continue
        
        # Flow entries (check BEFORE docs since flow format is more specific)
        # - [Title](URL) (by Author): Description
        flow_match = re.match(r'^- \[(.+?)\]\((.+?)\)\s+\(by .+?\):\s*(.*)', line)
        if flow_match and current_section:
            title, url, desc = flow_match.groups()
            url = url.replace("https://hermesbible.com", "").replace("https://www.hermesbible.com", "")
            flows.append({
                "title": title.strip(),
                "url": url.strip(),
                "description": desc.strip()[:120],
                "category": current_section
            })
            continue
        
        # Doc entries: - [Title](URL): Description
        doc_match = re.match(r'^- \[(.+?)\]\((.+?)\):\s*(.*)', line)
        if doc_match and current_section:
            title, url, desc = doc_match.groups()
            # Clean up URL - make relative
            url = url.replace("https://hermesbible.com", "").replace("https://www.hermesbible.com", "")
            docs.append({
                "title": title.strip(),
                "url": url.strip(),
                "description": desc.strip()[:100],
                "section": current_section
            })
            continue
    
    return docs, flows

def parse_current_index():
    """Parse the current index.md to extract existing URLs."""
    urls = set()
    if not INDEX_FILE.exists():
        return urls
    
    content = INDEX_FILE.read_text()
    # Match markdown links: [text](url)
    for match in re.finditer(r'\]\((/docs/[^\)]+)\)', content):
        urls.add(match.group(1))
    # Also match bare URLs in backticks: `/docs/...`
    for match in re.finditer(r'`(/docs/[^`]+)`', content):
        urls.add(match.group(1))
    return urls

def parse_current_flows():
    """Parse the current flows-catalog.md to extract existing URLs."""
    urls = set()
    if not FLOWS_FILE.exists():
        return urls
    
    content = FLOWS_FILE.read_text()
    # Match markdown links: [text](url) or just /flows/... in table cells
    for match in re.finditer(r'\]\((/flows/[^\)]+)\)', content):
        urls.add(match.group(1))
    # Also match bare URLs in table cells
    for match in re.finditer(r'`(/flows/[^`]+)`', content):
        urls.add(match.group(1))
    return urls

def generate_index_md(docs):
    """Generate the full index.md content from parsed docs."""
    sections = {}
    for doc in docs:
        section = doc["section"]
        if section not in sections:
            sections[section] = []
        sections[section].append(doc)
    
    lines = [
        "# Full Documentation Index",
        "",
        f"Source: https://www.hermesbible.com",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        ""
    ]
    
    for section, section_docs in sections.items():
        # Count pages in section
        lines.append(f"## {section} ({len(section_docs)} pages)")
        lines.append("")
        lines.append("| Page | URL |")
        lines.append("|------|-----|")
        for doc in section_docs:
            lines.append(f"| {doc['title']} | `{doc['url']}` |")
        lines.append("")
    
    return "\n".join(lines)

def generate_flows_md(flows):
    """Generate the flows-catalog.md content from parsed flows."""
    categories = {}
    for flow in flows:
        cat = flow["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(flow)
    
    lines = [
        "# Flows Catalog — Real Hermes Workflows",
        "",
        "Source: https://www.hermesbible.com/flows",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d')}",
        "Community-built workflows, organized by category and intent.",
        "",
        "---",
        ""
    ]
    
    for cat, cat_flows in categories.items():
        lines.append(f"## {cat}")
        lines.append("")
        lines.append("| Flow | Summary | URL |")
        lines.append("|------|---------|-----|")
        for flow in cat_flows:
            # Truncate description for table
            desc = flow["description"][:80] + "..." if len(flow["description"]) > 80 else flow["description"]
            lines.append(f"| {flow['title']} | {desc} | `{flow['url']}` |")
        lines.append("")
    
    return "\n".join(lines)

def copy_to_repo():
    """Copy updated files from skill dir to repo dir."""
    import shutil
    
    # Copy SKILL.md
    shutil.copy2(SKILL_DIR / "SKILL.md", REPO_DIR / "SKILL.md")
    
    # Copy references
    refs_src = SKILL_DIR / "references"
    refs_dst = REPO_DIR / "references"
    refs_dst.mkdir(exist_ok=True)
    
    for f in refs_src.glob("*.md"):
        shutil.copy2(f, refs_dst / f.name)

def git_commit_and_push(message):
    """Commit and push changes to GitHub."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True, capture_output=True)
        
        # Check if there are changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True)
        if not result.stdout.strip():
            print("No changes to commit.")
            return False
        
        subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True, capture_output=True)
        print(f"Committed and pushed: {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git operation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Update Hermes Bible skill from llms.txt")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Hermes Bible Self-Updater")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Fetch latest llms.txt
    print("\n[1/5] Fetching llms.txt...")
    content = fetch_llms_txt()
    if not content:
        sys.exit(1)
    
    if args.verbose:
        print(f"  Fetched {len(content)} bytes")
    
    # 2. Parse into docs and flows
    print("[2/5] Parsing content...")
    docs, flows = parse_llms_txt(content)
    print(f"  Found {len(docs)} doc pages, {len(flows)} flows")
    
    # 3. Compare with current
    print("[3/5] Comparing with current...")
    current_doc_urls = parse_current_index()
    current_flow_urls = parse_current_flows()
    
    new_docs = [d for d in docs if d["url"] not in current_doc_urls]
    new_flows = [f for f in flows if f["url"] not in current_flow_urls]
    
    removed_docs = current_doc_urls - {d["url"] for d in docs}
    removed_flows = current_flow_urls - {f["url"] for f in flows}
    
    print(f"  New docs: {len(new_docs)}")
    print(f"  New flows: {len(new_flows)}")
    print(f"  Removed docs: {len(removed_docs)}")
    print(f"  Removed flows: {len(removed_flows)}")
    
    if not new_docs and not new_flows and not removed_docs and not removed_flows:
        print("\n✅ No changes detected. Skill is up to date.")
        return
    
    # Show what's new
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
    
    if args.dry_run:
        print("\n[DRY RUN] No changes applied.")
        return
    
    # 4. Generate updated files
    print("\n[4/5] Generating updated reference files...")
    
    # Update index.md
    new_index = generate_index_md(docs)
    INDEX_FILE.write_text(new_index)
    print(f"  Updated: {INDEX_FILE}")
    
    # Update flows-catalog.md
    new_flows_md = generate_flows_md(flows)
    FLOWS_FILE.write_text(new_flows_md)
    print(f"  Updated: {FLOWS_FILE}")
    
    # 5. Copy to repo and push
    print("[5/5] Syncing to repo and pushing...")
    copy_to_repo()
    
    # Build commit message
    changes = []
    if new_docs:
        changes.append(f"{len(new_docs)} new docs")
    if new_flows:
        changes.append(f"{len(new_flows)} new flows")
    if removed_docs:
        changes.append(f"{len(removed_docs)} docs removed")
    if removed_flows:
        changes.append(f"{len(removed_flows)} flows removed")
    
    commit_msg = f"chore: auto-update from hermesbible.com — {', '.join(changes)}"
    
    if git_commit_and_push(commit_msg):
        print("\n✅ Update complete!")
        
        # Summary for notification
        summary = {
            "timestamp": datetime.now().isoformat(),
            "new_docs": len(new_docs),
            "new_flows": len(new_flows),
            "removed_docs": len(removed_docs),
            "removed_flows": len(removed_flows),
            "total_docs": len(docs),
            "total_flows": len(flows),
            "changes": changes
        }
        
        # Print summary as JSON for cron job notification
        print("\n--- UPDATE SUMMARY ---")
        print(json.dumps(summary, indent=2))
    else:
        print("\n⚠️  Update generated but git push failed.")

if __name__ == "__main__":
    main()
