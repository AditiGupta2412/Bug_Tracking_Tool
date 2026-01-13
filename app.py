import datetime
import os
from typing import Any, Dict, Optional, List

import streamlit as st
from bson.objectid import ObjectId
from pymongo import MongoClient

# =========================
# MongoDB Configuration
# (Same as bug_tracker.py)
# =========================

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "bug_tracker_db"
COLLECTION_NAME = "bugs"


@st.cache_resource
def get_db_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


# =========================
# Helper Functions
# =========================

def create_bug(
    title: str,
    description: str,
    severity: str,
    module: str,
    git_commit: Optional[str] = None,
) -> str:
    collection = get_db_collection()
    now = datetime.datetime.utcnow()

    bug_doc: Dict[str, Any] = {
        "title": title,
        "description": description,
        "severity": severity.lower(),
        "status": "open",
        "module": module,
        "git_commit": git_commit or "N/A",
        "created_at": now,
        "updated_at": now,
        "logs": [],
    }

    result = collection.insert_one(bug_doc)
    return str(result.inserted_id)


def add_test_log(
    bug_id: str,
    status: str,
    details: str,
) -> bool:
    collection = get_db_collection()
    log_entry = {
        "timestamp": datetime.datetime.utcnow(),
        "status": status.lower(),
        "details": details,
    }

    result = collection.update_one(
        {"_id": ObjectId(bug_id)},
        {
            "$push": {"logs": log_entry},
            "$set": {"updated_at": datetime.datetime.utcnow()},
        },
    )

    return result.modified_count == 1


def update_bug_status(bug_id: str, new_status: str) -> bool:
    collection = get_db_collection()
    result = collection.update_one(
        {"_id": ObjectId(bug_id)},
        {
            "$set": {
                "status": new_status.lower(),
                "updated_at": datetime.datetime.utcnow(),
            }
        },
    )
    return result.modified_count == 1


def list_bugs(
    status: Optional[str] = None,
    module: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[Dict[str, Any]]:
    collection = get_db_collection()
    query: Dict[str, Any] = {}

    if status and status != "All":
        query["status"] = status.lower()
    if module:
        query["module"] = module
    if severity and severity != "All":
        query["severity"] = severity.lower()

    cursor = collection.find(query).sort("created_at", -1)
    return list(cursor)


def get_bug_by_id(bug_id: str) -> Optional[Dict[str, Any]]:
    collection = get_db_collection()
    return collection.find_one({"_id": ObjectId(bug_id)})


# =========================
# Streamlit UI
# =========================

st.set_page_config(page_title="Bug Tracking Tool", page_icon="🐞", layout="wide")

st.title("🐞 Bug Tracking Optimization Tool")
st.caption("Python · MongoDB · Streamlit")

menu = st.sidebar.radio(
    "Navigation",
    ["Create Bug", "View Bugs", "Update Status / Add Log"],
)


# --------- Page: Create Bug ---------
if menu == "Create Bug":
    st.subheader("Create a New Bug Report")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Bug Title")
        module = st.text_input("Module (e.g., auth, dashboard, api)")
        severity = st.selectbox(
            "Severity",
            ["low", "medium", "high", "critical"],
            index=2,
        )
    with col2:
        git_commit = st.text_input(
            "Git Commit (optional)",
            help="Paste commit hash if you want to link this bug to a specific version.",
        )
        description = st.text_area("Description")

    if st.button("Create Bug", type="primary"):
        if not title or not description or not module:
            st.error("Please fill in Title, Description, and Module.")
        else:
            bug_id = create_bug(
                title=title,
                description=description,
                severity=severity,
                module=module,
                git_commit=git_commit or None,
            )
            st.success(f"Bug created successfully! ID: {bug_id}")


# --------- Page: View Bugs ---------
elif menu == "View Bugs":
    st.subheader("View & Filter Bugs")

    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        status_filter = st.selectbox(
            "Status",
            ["All", "open", "in-progress", "resolved", "closed"],
        )
    with col_filter2:
        severity_filter = st.selectbox(
            "Severity",
            ["All", "low", "medium", "high", "critical"],
        )
    with col_filter3:
        module_filter = st.text_input("Module (optional)")

    bugs = list_bugs(
        status=status_filter,
        module=module_filter or None,
        severity=severity_filter,
    )

    st.write(f"Found **{len(bugs)}** bugs.")
    if not bugs:
        st.info("No bugs match your filters.")
    else:
        for bug in bugs:
            with st.expander(
                f"[{bug['status'].upper()}] {bug['title']}  —  {bug['module']} ({bug['severity']})"
            ):
                st.markdown(f"**ID:** `{bug['_id']}`")
                st.markdown(f"**Module:** `{bug['module']}`")
                st.markdown(f"**Severity:** `{bug['severity']}`")
                st.markdown(f"**Status:** `{bug['status']}`")
                st.markdown(f"**Git Commit:** `{bug.get('git_commit', 'N/A')}`")
                st.markdown(f"**Created At:** {bug['created_at']}")
                st.markdown(f"**Updated At:** {bug['updated_at']}")
                st.markdown("**Description:**")
                st.write(bug["description"])

                logs = bug.get("logs", [])
                st.markdown("**Test Logs:**")
                if not logs:
                    st.write("_No logs yet._")
                else:
                    for i, log in enumerate(logs, start=1):
                        st.write(
                            f"{i}. **{log['status'].upper()}** at {log['timestamp']}: {log['details']}"
                        )


# --------- Page: Update Status / Add Log ---------
elif menu == "Update Status / Add Log":
    st.subheader("Update Bug Status or Add Test Log")

    bug_id_input = st.text_input("Bug ID")

    if bug_id_input:
        bug = None
        try:
            bug = get_bug_by_id(bug_id_input)
        except Exception:
            st.error("Invalid Bug ID format.")

        if bug:
            st.markdown(f"**Title:** {bug['title']}")
            st.markdown(f"**Current Status:** `{bug['status']}`")
            st.markdown(f"**Module:** `{bug['module']}`")
            st.markdown(f"**Severity:** `{bug['severity']}`")

            tab1, tab2 = st.tabs(["Update Status", "Add Test Log"])

            with tab1:
                new_status = st.selectbox(
                    "New Status",
                    ["open", "in-progress", "resolved", "closed"],
                    index=["open", "in-progress", "resolved", "closed"].index(
                        bug["status"]
                    )
                    if bug["status"] in ["open", "in-progress", "resolved", "closed"]
                    else 0,
                )
                if st.button("Update Status"):
                    if update_bug_status(bug_id_input, new_status):
                        st.success("Status updated successfully.")
                    else:
                        st.error("Failed to update status.")

            with tab2:
                log_status = st.selectbox("Test Status", ["passed", "failed"])
                log_details = st.text_area("Test Log Details")

                if st.button("Add Test Log"):
                    if not log_details.strip():
                        st.error("Please enter log details.")
                    else:
                        if add_test_log(bug_id_input, log_status, log_details):
                            st.success("Test log added successfully.")
                        else:
                            st.error("Failed to add log.")
        else:
            st.info("Enter a valid Bug ID to load details.")
    else:
        st.info("Paste a Bug ID above to manage it.")
