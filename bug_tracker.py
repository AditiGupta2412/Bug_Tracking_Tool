import datetime
import os
from typing import Any, Dict, Optional, List

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
def get_db_collection(name="bugs"):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[name]

def log_audit_event(action: str, bug_id: Optional[str] = None, details: str = ""):
    collection = get_db_collection("audit_logs")
    collection.insert_one({
        "timestamp": datetime.datetime.utcnow(),
        "user": "admin", # Prototype user
        "action": action,
        "bug_id": bug_id,
        "details": details
    })


# =========================
# Helper Functions
# =========================

def create_bug(
    title: str,
    description: str,
    severity: str,
    priority: str,
    module: str,
    assignee: str = "Unassigned",
    git_commit: Optional[str] = None,
) -> str:
    collection = get_db_collection()
    now = datetime.datetime.utcnow()

    bug_doc: Dict[str, Any] = {
        "title": title,
        "description": description,
        "severity": severity.lower(),
        "priority": priority.lower(),
        "status": "open",
        "module": module,
        "assignee": assignee,
        "git_commit": git_commit or "N/A",
        "created_at": now,
        "updated_at": now,
        "logs": [],
    }

    result = collection.insert_one(bug_doc)
    bug_id = str(result.inserted_id)
    log_audit_event("CREATE_BUG", bug_id, f"Title: {title}")
    return bug_id


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

    if result.modified_count == 1:
        log_audit_event("ADD_ACTIVITY", bug_id, f"Type: {status}")
        return True
    return False


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
    if result.modified_count == 1:
        log_audit_event("UPDATE_STATUS", bug_id, f"New Status: {new_status}")
        return True
    return False


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

def export_bugs_to_csv(bugs: List[Dict[str, Any]]):
    if not bugs:
        return None
    # Clean up bugs for CSV (remove ObjectId)
    clean_bugs = []
    for b in bugs:
        item = b.copy()
        item['_id'] = str(item['_id'])
        clean_bugs.append(item)
    df = pd.DataFrame(clean_bugs)
    return df.to_csv(index=False).encode('utf-8')


# =========================
# Streamlit UI
# =========================

# =========================
# Streamlit UI Configuration
# =========================

st.set_page_config(
    page_title="BugTracker Pro | Enterprise Dashboard",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional Custom CSS
st.markdown("""
<style>
    /* Main Background and Font */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #00d4ff !important;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e3440,#2e3440);
        color: white;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
    }
    
    /* Glassmorphism Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 10px !important;
    }
    
    /* Gradient Header */
    .main-header {
        background: linear-gradient(90deg, #00d4ff 0%, #0072ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Authentication Layer
# =========================

def login_form():
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column;'>
            <div style='background: rgba(255, 255, 255, 0.05); padding: 3rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1); width: 400px; text-align: center;'>
                <h1 style='color: #00d4ff; font-size: 3rem; margin-bottom: 0px;'>🐞</h1>
                <h2 style='margin-bottom: 2rem; color: #fff;'>BugTracker Pro</h2>
                <p style='color: #888; margin-bottom: 2rem;'>Enterprise-Grade Issue Tracking</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        _, center, _ = st.columns([1, 1, 1])
        with center:
            user = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            if st.button("Login", type="primary", use_container_width=True):
                # Simple mock auth for professional prototype
                if user == "admin" and password == "admin": 
                    st.session_state["authenticated"] = True
                    st.success("Access Granted")
                    st.rerun()
                else:
                    st.error("Invalid Credentials. Please use admin/admin for prototype access.")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_form()
    st.stop()

# Logout button in sidebar
if st.sidebar.button("🚪 Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# Sidebar Header
st.sidebar.markdown("<h2 style='text-align: center; color: #00d4ff;'>🐞 BugTracker Pro</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align: center; color: #888;'>User: <b>Admin</b></p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "NAVIGATION",
    ["📊 Executive Analytics", "📝 Create Bug", "🔍 View & Manage", "⚙️ Quick Actions"],
)


# --------- Page: Analytics ---------
if menu == "📊 Executive Analytics":
    st.markdown("<div class='main-header'>Executive Overview</div>", unsafe_allow_html=True)
    st.caption("Real-time project health and bug distribution metrics.")
    st.markdown("---")

    bugs = list_bugs()  # Fetch all bugs for analytics
    if not bugs:
        st.info("No data available for analytics yet. Create your first bug to see insights!")
    else:
        df = pd.DataFrame(bugs)
        
        # High Level Metrics
        total_bugs = len(df)
        open_bugs = len(df[df['status'] == 'open'])
        critical_bugs = len(df[df['severity'] == 'critical'])
        resolved_bugs = len(df[df['status'].isin(['resolved', 'closed'])])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Reported", total_bugs)
        m2.metric("Active Issues", open_bugs, delta_color="inverse")
        m3.metric("Critical Blocks", critical_bugs)
        m4.metric("Resolved Rate", f"{(resolved_bugs/total_bugs)*100:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_fig1, col_fig2 = st.columns(2)
        
        with col_fig1:
            st.subheader("Severity Distribution")
            fig_sev = px.pie(
                df, names='severity', 
                color='severity',
                color_discrete_map={'critical': '#ff4b4b', 'high': '#ffa500', 'medium': '#00d4ff', 'low': '#00ff00'},
                hole=0.4
            )
            fig_sev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_sev, use_container_width=True)
            
        with col_fig2:
            st.subheader("Status Breakdown")
            fig_stat = px.bar(
                df.groupby('status').size().reset_index(name='counts'),
                x='status', y='counts',
                color='status',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_stat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_stat, use_container_width=True)

        st.subheader("Bug Reporting Trend")
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        trend_df = df.groupby('date').size().reset_index(name='count')
        fig_trend = px.line(trend_df, x='date', y='count', markers=True)
        fig_trend.update_traces(line_color='#00d4ff', line_width=3)
        fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_trend, use_container_width=True)


# --------- Page: Create Bug ---------
elif menu == "📝 Create Bug":
    st.markdown("<div class='main-header'>File New Bug</div>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Bug Title")
        module = st.text_input("Module (e.g., auth, dashboard, api)")
        severity = st.selectbox(
            "Severity",
            ["low", "medium", "high", "critical"],
            index=2,
        )
        priority = st.selectbox(
            "Priority",
            ["P0 - Immediate", "P1 - High", "P2 - Normal", "P3 - Low"],
            index=2,
        )
    with col2:
        assignee = st.text_input("Assignee (Name/Email)", placeholder="e.g. aditi@example.com")
        git_commit = st.text_input(
            "Git Commit (optional)",
            help="Paste commit hash if you want to link this bug to a specific version.",
        )
        description = st.text_area("Description")

    if st.button("Create Bug", type="primary"):
        if not title or not description or not module:
            st.error("Please fill in Title, Description, and Module.")
        else:
            with st.spinner("Filing report in database..."):
                try:
                    bug_id = create_bug(
                        title=title,
                        description=description,
                        severity=severity,
                        priority=priority.split(' - ')[0], # Extract P0, P1, etc.
                        module=module,
                        assignee=assignee or "Unassigned",
                        git_commit=git_commit or None,
                    )
                    st.success(f"✅ Bug report filed successfully! Tracking ID: {bug_id}")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Failed to create bug: {str(e)}")


# --------- Page: View Bugs ---------
elif menu == "🔍 View & Manage":
    st.markdown("<div class='main-header'>Issue Explorer</div>", unsafe_allow_html=True)
    st.markdown("---")

    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
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
        priority_filter = st.selectbox(
            "Priority",
            ["All", "p0", "p1", "p2", "p3"]
        )
    with col_filter4:
        assignee_filter = st.text_input("Assignee")
    
    search_query = st.text_input("🔍 Global Search (Title, Description, or Module)", placeholder="Type to search...")

    bugs = list_bugs(
        status=status_filter,
        severity=severity_filter,
    )
    
    # Client-side filtering for priority, assignee, and search
    if priority_filter != "All":
        bugs = [b for b in bugs if b.get('priority') == priority_filter]
    if assignee_filter:
        bugs = [b for b in bugs if assignee_filter.lower() in b.get('assignee', '').lower()]
    if search_query:
        q = search_query.lower()
        bugs = [b for b in bugs if q in b['title'].lower() or q in b['description'].lower() or q in b['module'].lower()]

    st.write(f"Found **{len(bugs)}** bugs.")
    
    if bugs:
        csv_data = export_bugs_to_csv(bugs)
        st.download_button(
            label="📄 Export Results to CSV",
            data=csv_data,
            file_name=f"bug_report_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    if not bugs:
        st.info("No bugs match your filters.")
    else:
        for bug in bugs:
            with st.expander(
                f"[{bug['status'].upper()}] {bug['title']}  —  {bug['module']} ({bug['severity']})"
            ):
                st.markdown(f"**ID:** `{bug['_id']}`")
                
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Module:** `{bug['module']}`")
                c1.markdown(f"**Severity:** `{bug['severity'].upper()}`")
                
                c2.markdown(f"**Priority:** `{bug.get('priority', 'N/A').upper()}`")
                c2.markdown(f"**Assignee:** `{bug.get('assignee', 'Unassigned')}`")
                
                c3.markdown(f"**Status:** `{bug['status'].upper()}`")
                c3.markdown(f"**Git Commit:** `{bug.get('git_commit', 'N/A')}`")
                st.markdown(f"**Created At:** {bug['created_at']}")
                st.markdown(f"**Updated At:** {bug['updated_at']}")
                st.markdown("**Description:**")
                st.write(bug["description"])

                st.markdown("---")
                col_actions, col_logs = st.columns([1, 2])
                
                with col_actions:
                    st.markdown("**Add Update/Comment**")
                    comment_text = st.text_area("Update Details", key=f"comment_{bug['_id']}", height=100)
                    comment_status = st.selectbox("Type", ["Comment", "Resolved", "Failed Test", "Blocked"], key=f"type_{bug['_id']}")
                    if st.button("Post Update", key=f"btn_{bug['_id']}"):
                        if comment_text.strip():
                            with st.spinner("Posting update..."):
                                try:
                                    if add_test_log(str(bug['_id']), comment_status, comment_text):
                                        st.toast("Update posted successfully!", icon="✅")
                                        # Use a slight delay or session state to ensure toast is seen
                                        import time
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to post update.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        else:
                            st.warning("Please enter some text.")

                with col_logs:
                    logs = bug.get("logs", [])
                    st.markdown("**Activity History**")
                    if not logs:
                        st.write("_No activity logs recorded yet._")
                    else:
                        for i, log in enumerate(reversed(logs), start=1):
                            icon = "💬" if log['status'] == "comment" else "✅" if log['status'] == "resolved" else "❌"
                            st.markdown(f"{icon} **{log['status'].upper()}** | {log['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                            st.caption(log['details'])
                            st.markdown("---")


# --------- Page: Update Status / Add Log ---------
elif menu == "⚙️ Quick Actions":
    st.markdown("<div class='main-header'>Maintenance Console</div>", unsafe_allow_html=True)
    st.markdown("---")

    bug_id_input = st.text_input("Enter Bug ID to manage")

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
                        with st.spinner("Saving log..."):
                            try:
                                if add_test_log(bug_id_input, log_status, log_details):
                                    st.success("✅ Test log added successfully.")
                                else:
                                    st.error("❌ Failed to add log. Check Bug ID.")
                            except Exception as e:
                                st.error(f"Error saving log: {str(e)}")
        else:
            st.info("Enter a valid Bug ID to load details.")
    else:
        st.info("Paste a Bug ID above to manage it.")
