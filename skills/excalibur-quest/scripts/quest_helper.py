# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper CLI for excalibur-quest remediation orchestrations."""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time


class QuestDB:
    """Quest tracking database with Dolt primary and local JSON fallback."""

    def __init__(self, db_dir):
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)
        self.json_db = os.path.join(self.db_dir, "quest_db.json")
        self.use_dolt = self._check_dolt()

    def _check_dolt(self):
        try:
            res = subprocess.run(
                ["dolt", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return res.returncode == 0
        except OSError:
            return False

    def load_quest(self, issue_id):
        if self.use_dolt:
            try:
                res = subprocess.run(
                    [
                        "dolt", "sql", "-q",
                        f"SELECT data FROM quests WHERE issue_id = '{issue_id}'",
                        "-r", "json"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if res.returncode == 0 and res.stdout.strip():
                    rows = json.loads(res.stdout)
                    if rows.get("rows"):
                        return json.loads(rows["rows"][0]["data"])
            except Exception as e:
                print(f"Dolt load failed, falling back to JSON: {e}", file=sys.stderr)
        
        if os.path.exists(self.json_db):
            try:
                with open(self.json_db, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(str(issue_id))
            except Exception as e:
                print(f"JSON load failed: {e}", file=sys.stderr)
        return None

    def save_quest(self, issue_id, quest_data):
        if self.use_dolt:
            try:
                subprocess.run(
                    [
                        "dolt", "sql", "-q",
                        "CREATE TABLE IF NOT EXISTS quests "
                        "(issue_id VARCHAR(50) PRIMARY KEY, data TEXT)"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                escaped_data = json.dumps(quest_data).replace("'", "''")
                res = subprocess.run(
                    [
                        "dolt", "sql", "-q",
                        f"REPLACE INTO quests (issue_id, data) "
                        f"VALUES ('{issue_id}', '{escaped_data}')"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if res.returncode == 0:
                    return
            except Exception as e:
                print(f"Dolt write failed, falling back to JSON: {e}", file=sys.stderr)

        data = {}
        if os.path.exists(self.json_db):
            try:
                with open(self.json_db, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data[str(issue_id)] = quest_data
        try:
            with open(self.json_db, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"JSON write failed: {e}", file=sys.stderr)


def acquire_concurrency_slot(lock_dir, max_concurrent=3):
    """Acquires a concurrency slot using file locks or blocks until one is free."""
    os.makedirs(lock_dir, exist_ok=True)
    locks = []
    for i in range(max_concurrent):
        lock_file = os.path.join(lock_dir, f"lock_{i}.lock")
        open(lock_file, "a").close()
        locks.append(open(lock_file, "r+"))

    while True:
        for idx, fh in enumerate(locks):
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print(f"Acquired Roundtable seat {idx + 1} of {max_concurrent}", file=sys.stderr)
                return fh
            except (BlockingIOError, OSError):
                continue
        print("Roundtable seats full. Waiting for slot...", file=sys.stderr)
        time.sleep(1.0)


def run_init(args, db):
    """Initializes remediation quest with beads from review input."""
    beads = []
    if args.reviews_path and os.path.exists(args.reviews_path):
        try:
            with open(args.reviews_path, "r", encoding="utf-8") as f:
                reviews = json.load(f)
                for idx, r in enumerate(reviews.get("findings", [])):
                    beads.append({
                        "id": f"bead-{idx+1}",
                        "title": r.get("title", f"Remediation item {idx+1}"),
                        "severity": r.get("severity", "MEDIUM"),
                        "status": "PENDING"
                    })
        except Exception as e:
            print(f"Failed to load reviews path: {e}", file=sys.stderr)

    if not beads:
        beads = [
            {"id": "bead-1", "title": "Audit source for security vulnerabilities", "severity": "CRITICAL", "status": "PENDING"},
            {"id": "bead-2", "title": "Verify tokio async I/O migrations", "severity": "HIGH", "status": "PENDING"},
            {"id": "bead-3", "title": "Check static analyzer schemas", "severity": "MEDIUM", "status": "PENDING"}
        ]

    quest_data = {
        "issue_id": args.issue_id,
        "status": "ACTIVE",
        "beads": beads,
        "created_at": time.time()
    }
    db.save_quest(args.issue_id, quest_data)
    return quest_data


def run_sync(args, db):
    """Syncs beads database with GitHub issues."""
    quest = db.load_quest(args.issue_id)
    if not quest:
        print(f"Error: Quest for issue {args.issue_id} not initialized.", file=sys.stderr)
        sys.exit(1)

    print(f"Syncing beads status to GitHub repo {args.repo_owner}/{args.repo_name}...", file=sys.stderr)
    
    # Try using gh CLI to add comments on the GitHub issue
    comment_body = f"### Excalibur Quest Sync Update\n\n**Quest Status:** {quest['status']}\n\n**Beads Progress:**\n"
    for b in quest.get("beads", []):
        status_box = "[x]" if b["status"] == "COMPLETED" else "[ ]"
        comment_body += f"- {status_box} **{b['id']}**: {b['title']} ({b['severity']})\n"

    try:
        res = subprocess.run(
            [
                "gh", "issue", "comment", str(args.issue_id),
                "--repo", f"{args.repo_owner}/{args.repo_name}",
                "--body", comment_body
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            print("Successfully synced comment to GitHub.", file=sys.stderr)
            quest["github_synced"] = True
        else:
            print(f"Warning: gh CLI sync failed (continuing locally): {res.stderr.strip()}", file=sys.stderr)
            quest["github_synced"] = False
    except OSError:
        print("Warning: gh CLI not installed. Continuing local-only sync.", file=sys.stderr)
        quest["github_synced"] = False

    db.save_quest(args.issue_id, quest)
    return quest


def run_close(args, db):
    """Closes all beads and marks quest complete."""
    quest = db.load_quest(args.issue_id)
    if not quest:
        print(f"Error: Quest for issue {args.issue_id} not found.", file=sys.stderr)
        sys.exit(1)

    quest["status"] = "COMPLETED"
    for b in quest.get("beads", []):
        b["status"] = "COMPLETED"

    db.save_quest(args.issue_id, quest)
    print(f"Successfully closed quest {args.issue_id}.", file=sys.stderr)
    return quest


def main():
    parser = argparse.ArgumentParser(description="Excalibur Quest remediation coordinator.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Subcommand: init ---
    p_init = subparsers.add_parser("init", help="Initialize remediation beads database")
    p_init.add_argument("--issue-id", required=True, type=int, help="Target GitHub issue number")
    p_init.add_argument("--reviews-path", help="Path to JSON review findings file")
    p_init.add_argument("--output", required=True, help="Output JSON status file path")

    # --- Subcommand: sync ---
    p_sync = subparsers.add_parser("sync", help="Sync local beads state to GitHub")
    p_sync.add_argument("--issue-id", required=True, type=int, help="Target GitHub issue number")
    p_sync.add_argument("--repo-owner", required=True, help="GitHub repository owner")
    p_sync.add_argument("--repo-name", required=True, help="GitHub repository name")
    p_sync.add_argument("--output", required=True, help="Output JSON status file path")

    # --- Subcommand: close ---
    p_close = subparsers.add_parser("close", help="Close beads and finalize quest")
    p_close.add_argument("--issue-id", required=True, type=int, help="Target GitHub issue number")
    p_close.add_argument("--output", required=True, help="Output JSON status file path")

    args = parser.parse_args()

    # Locate repository root / workspace directory to store locks and db safely
    try:
        workspace_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        workspace_root = os.getcwd()

    lock_dir = os.path.join(workspace_root, ".excalibur_locks")
    lock_fh = acquire_concurrency_slot(lock_dir)

    try:
        db = QuestDB(os.path.join(workspace_root, ".excalibur_quest"))
        if args.command == "init":
            res = run_init(args, db)
        elif args.command == "sync":
            res = run_sync(args, db)
        elif args.command == "close":
            res = run_close(args, db)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)

        # Write output file
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)
            print(f"Success! Data written to: {args.output}")
        except OSError as e:
            print(f"Error writing output to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)

    finally:
        lock_fh.close()


if __name__ == "__main__":
    main()
