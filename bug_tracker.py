#!/usr/bin/env python3
"""
Bug Tracking Optimization Tool
--------------------------------
Features:
- Create bug reports for web modules
- Add test logs to existing bugs
- List and filter bugs
- Update bug status
- Automatically attach current Git commit hash to each bug

Usage examples:

    # Create a new bug
    python bug_tracker.py create \
        --title "Login button not working" \
        --module "auth" \
        --severity "high" \
        --description "Login button does nothing when clicked"

    # Add a test log to a bug
    python bug_tracker.py add-log \
        --bug-id "<BUG_ID_FROM_DB>" \
        --status "failed" \
        --details "Unit tests failed on /login endpoint"

    # List all open bugs
    python bug_tracker.py list --status "open"

    # Update bug status
    python bug_tracker.py update-status \
        --bug-id "<BUG_ID_FROM_DB>" \
        --status "resolved"

MongoDB:
- Make sure MongoDB is running locally OR change MONGO_URI to your Atlas URI.
"""

import argparse
import datetime
import subprocess
from typing import Optional, Dict, Any

from pymongo import MongoClient
from bson.objectid import ObjectId

# =========================
# MongoDB Configuration
# =========================

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bug_tracker_db"
COLLECTION_NAME = "bugs"


def get_db_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


# =========================
# Git Utilities
# =========================

def get_current_git_commit() -> Optional[str]:
    """
    Returns the current Git commit hash if inside a Git repo.
    Otherwise returns None.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()
        return commit_hash if commit_hash else None
    except Exception:
        return None


# =========================
# Core Operations
# =========================

def create_bug(
    title: str,
    description: str,
    severity: str,
    module: str
) -> str:
    """
    Create a new bug report document in MongoDB.
    Returns the inserted bug ID as a string.
    """
    collection = get_db_collection()
    now = datetime.datetime.utcnow()

    bug_doc: Dict[str, Any] = {
        "title": title,
        "description": description,
        "severity": severity.lower(),  # e.g., low, medium, high, critical
        "status": "open",              # default
        "module": module,
        "git_commit": get_current_git_commit(),
        "created_at": now,
        "updated_at": now,
        "logs": []  # list of test logs
    }

    result = collection.insert_one(bug_doc)
    return str(result.inserted_id)


def add_test_log(
    bug_id: str,
    status: str,
    details: str
) -> bool:
    """
    Add a test log entry to an existing bug.
    status: e.g., "passed", "failed"
    """
    collection = get_db_collection()
    log_entry = {
        "timestamp": datetime.datetime.utcnow(),
        "status": status.lower(),
        "details": details
    }

    result = collection.update_one(
        {"_id": ObjectId(bug_id)},
        {
            "$push": {"logs": log_entry},
            "$set": {"updated_at": datetime.datetime.utcnow()}
        }
    )

    return result.modified_count == 1


def list_bugs(
    status: Optional[str] = None,
    module: Optional[str] = None,
    severity: Optional[str] = None
):
    """
    List bugs with optional filters.
    """
    collection = get_db_collection()
    query: Dict[str, Any] = {}

    if status:
        query["status"] = status.lower()
    if module:
        query["module"] = module
    if severity:
        query["severity"] = severity.lower()

    cursor = collection.find(query).sort("created_at", -1)

    print("=== Bug List ===")
    for bug in cursor:
        print(f"ID         : {bug['_id']}")
        print(f"Title      : {bug['title']}")
        print(f"Module     : {bug['module']}")
        print(f"Severity   : {bug['severity']}")
        print(f"Status     : {bug['status']}")
        print(f"Git Commit : {bug.get('git_commit', 'N/A')}")
        print(f"Created At : {bug['created_at']}")
        print(f"Updated At : {bug['updated_at']}")
        print(f"Logs Count : {len(bug.get('logs', []))}")
        print("-" * 40)


def update_bug_status(
    bug_id: str,
    new_status: str
) -> bool:
    """
    Update the status of a bug.
    e.g., open -> in-progress -> resolved -> closed
    """
    collection = get_db_collection()
    result = collection.update_one(
        {"_id": ObjectId(bug_id)},
        {
            "$set": {
                "status": new_status.lower(),
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    return result.modified_count == 1


def show_bug_details(bug_id: str):
    """
    Display full details of a single bug, including logs.
    """
    collection = get_db_collection()
    bug = collection.find_one({"_id": ObjectId(bug_id)})

    if not bug:
        print("No bug found with that ID.")
        return

    print("=== Bug Details ===")
    print(f"ID         : {bug['_id']}")
    print(f"Title      : {bug['title']}")
    print(f"Description: {bug['description']}")
    print(f"Module     : {bug['module']}")
    print(f"Severity   : {bug['severity']}")
    print(f"Status     : {bug['status']}")
    print(f"Git Commit : {bug.get('git_commit', 'N/A')}")
    print(f"Created At : {bug['created_at']}")
    print(f"Updated At : {bug['updated_at']}")
    print("\nTest Logs:")
    logs = bug.get("logs", [])
    if not logs:
        print("  No logs yet.")
    else:
        for i, log in enumerate(logs, start=1):
            print(f"  Log #{i}")
            print(f"    Time   : {log['timestamp']}")
            print(f"    Status : {log['status']}")
            print(f"    Details: {log['details']}")
            print("-" * 30)


# =========================
# CLI (argparse)
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="Bug Tracking Optimization Tool (Python + MongoDB + Git)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # create bug
    create_parser = subparsers.add_parser("create", help="Create a new bug report")
    create_parser.add_argument("--title", required=True, help="Bug title")
    create_parser.add_argument("--description", required=True, help="Bug description")
    create_parser.add_argument("--severity", required=True,
                               choices=["low", "medium", "high", "critical"],
                               help="Bug severity")
    create_parser.add_argument("--module", required=True, help="Module name")

    # add-log
    log_parser = subparsers.add_parser("add-log", help="Add a test log to a bug")
    log_parser.add_argument("--bug-id", required=True, help="Bug ID")
    log_parser.add_argument("--status", required=True,
                            choices=["passed", "failed"],
                            help="Test status")
    log_parser.add_argument("--details", required=True, help="Details of the test log")

    # list bugs
    list_parser = subparsers.add_parser("list", help="List bugs with optional filters")
    list_parser.add_argument("--status", help="Filter by status (open, in-progress, resolved, closed)")
    list_parser.add_argument("--module", help="Filter by module")
    list_parser.add_argument("--severity", help="Filter by severity (low, medium, high, critical)")

    # update-status
    status_parser = subparsers.add_parser("update-status", help="Update status of a bug")
    status_parser.add_argument("--bug-id", required=True, help="Bug ID")
    status_parser.add_argument("--status", required=True,
                               choices=["open", "in-progress", "resolved", "closed"],
                               help="New status")

    # show-bug
    show_parser = subparsers.add_parser("show", help="Show full bug details")
    show_parser.add_argument("--bug-id", required=True, help="Bug ID")

    args = parser.parse_args()

    if args.command == "create":
        bug_id = create_bug(
            title=args.title,
            description=args.description,
            severity=args.severity,
            module=args.module
        )
        print(f"✅ Bug created with ID: {bug_id}")

    elif args.command == "add-log":
        ok = add_test_log(
            bug_id=args.bug_id,
            status=args.status,
            details=args.details
        )
        if ok:
            print("✅ Test log added successfully.")
        else:
            print("❌ Failed to add test log. Check Bug ID.")

    elif args.command == "list":
        list_bugs(
            status=args.status,
            module=args.module,
            severity=args.severity
        )

    elif args.command == "update-status":
        ok = update_bug_status(
            bug_id=args.bug_id,
            new_status=args.status
        )
        if ok:
            print("✅ Bug status updated successfully.")
        else:
            print("❌ Failed to update status. Check Bug ID.")

    elif args.command == "show":
        show_bug_details(args.bug_id)


if __name__ == "__main__":
    main()
