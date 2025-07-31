# scrapper_gui_enhanced.py

import streamlit as st
import os
import json
import threading
import time
import traceback
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import platform

# --- Scraper Import ---
# This will import the placeholder scraper.py file provided below.
try:
    # We pass the stop_event to the scraper to allow for graceful termination
    from scrapper import EnhancedPaperScraper, DOWNLOAD_FOLDER, setup_scraper_logging
except ImportError:
    st.error("Fatal: Could not import scrapper.py. Make sure it's in the same directory as this GUI file.")
    st.info("A placeholder `scrapper.py` file has been provided for you to use or adapt.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Academic Paper Scraper Pro+",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced CSS with Theme Variables for Dark Mode ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* General Styles */
    body {
        font-family: 'Inter', sans-serif;
    }

    /* Use Streamlit's theme variables for color */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1rem;
    }

    .subtitle {
        text-align: center;
        color: var(--text-color);
        opacity: 0.7;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Box Styles with RGBA for theme adaptability */
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left-width: 5px;
        border-left-style: solid;
        color: var(--text-color); /* Ensure text is readable */
    }

    .success-box {
        background-color: rgba(40, 167, 69, 0.15);
        border-left-color: #28a745;
    }
    .warning-box {
        background-color: rgba(255, 193, 7, 0.15);
        border-left-color: #ffc107;
    }
    .error-box {
        background-color: rgba(220, 53, 69, 0.15);
        border-left-color: #dc3545;
    }
    .info-box {
        background-color: rgba(23, 162, 184, 0.15);
        border-left-color: #17a2b8;
    }
     .debug-box {
        background-color: rgba(108, 117, 125, 0.15);
        border-left-color: #6c757d;
    }

    /* Metric Card - Reworked for theming */
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid var(--gray-200);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%; /* For consistent height in columns */
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: var(--primary-color);
    }
    .metric-label {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Log Container */
    .log-container {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }
    .status-running { background-color: #28a745; animation: pulse 1.5s infinite; }
    .status-idle { background-color: #6c757d; }
    .status-completed { background-color: #17a2b8; }
    .status-failed { background-color: #dc3545; }
    .status-stopped { background-color: #ffc107; }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
        100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
def initialize_session_state():
    """Initialize all required session state variables."""
    defaults = {
        'scraper_status': 'Idle',  # Idle, Running, Completed, Failed, Stopped
        'scraper_results': [],
        'logs': [],
        'downloaded_count': 0,
        'search_history': [],
        'last_scrape_time': None,
        'scraper_start_time': None,
        'stop_event': None,
        'advanced_mode': False,
        'debug_mode': False,
        'favorite_queries': [],
        'current_file_page': 1
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Helper Functions ---
def log_message(message: str, level: str = "INFO"):
    """Add a formatted log message to the session state."""
    timestamp = datetime.now()
    st.session_state.logs.append({
        "timestamp": timestamp.strftime("%H:%M:%S"),
        "level": level.upper(),
        "message": message,
        "full_timestamp": timestamp
    })
    # Keep last 200 logs to prevent memory issues
    st.session_state.logs = st.session_state.logs[-200:]

def render_metric(label: str, value: Any, help_text: str = ""):
    """Renders a styled metric card."""
    st.markdown(f"""
    <div class="metric-card" title="{help_text}">
        <p class="metric-number">{value}</p>
        <p class="metric-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)

def open_file_location():
    """Open the download folder in the system file manager."""
    try:
        path = os.path.abspath(DOWNLOAD_FOLDER)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        st.error(f"Could not open folder: {e}")

# --- Core Scraper Logic ---
def run_scraper_thread(config: Dict, stop_event: threading.Event):
    """Run the scraper in a separate thread with proper error handling."""
    st.session_state.scraper_start_time = datetime.now()
    st.session_state.downloaded_count = 0
    
    # Setup a thread-specific logger
    thread_logger = setup_scraper_logging(log_message)
    
    try:
        log_message("🚀 Initializing scraper...", "INFO")
        
        # Pass the stop event to the scraper class
        scraper = EnhancedPaperScraper(
            config=config,
            stop_event=stop_event,
            logger=thread_logger # Pass the logger
        )
        
        log_message(f"🔍 Starting search for: '{config['query']}'", "INFO")
        
        downloaded = scraper.run()
        st.session_state.downloaded_count = downloaded
        
        if stop_event.is_set():
            st.session_state.scraper_status = "Stopped"
            log_message("🛑 Scraping was stopped by the user.", "WARNING")
        elif downloaded > 0:
            st.session_state.scraper_status = "Completed"
            log_message(f"✅ Scraping finished. Downloaded {downloaded} papers.", "SUCCESS")
            # Save to history
            st.session_state.search_history.insert(0, {
                "query": config['query'],
                "results": downloaded,
                "timestamp": datetime.now()
            })
            st.session_state.search_history = st.session_state.search_history[:20]
            st.session_state.last_scrape_time = datetime.now()
        else:
            st.session_state.scraper_status = "Completed"
            log_message("🤔 No new papers were downloaded. Try different search terms or settings.", "INFO")

    except Exception as e:
        st.session_state.scraper_status = "Failed"
        log_message(f"💥 Scraper failed: {e}", "ERROR")
        log_message(f"Traceback:\n```\n{traceback.format_exc()}\n```", "DEBUG")
    finally:
        # If status is still 'Running', it means it ended without explicit success/failure
        if st.session_state.scraper_status == 'Running':
            st.session_state.scraper_status = 'Completed'

# --- UI Rendering Functions ---

def display_status_indicator():
    """Displays the main status indicator for the scraper."""
    status = st.session_state.get('scraper_status', 'Idle')
    status_class = f"status-{status.lower()}"
    
    elapsed_time_str = ""
    if status == 'Running' and st.session_state.scraper_start_time:
        elapsed = datetime.now() - st.session_state.scraper_start_time
        elapsed_time_str = f" | Running for: {str(elapsed).split('.')[0]}"

    st.markdown(f'''
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="status-indicator {status_class}"></span>
        <strong style="vertical-align: middle;">Status: {status}{elapsed_time_str}</strong>
    </div>
    ''', unsafe_allow_html=True)


def display_logs():
    """Displays filterable logs."""
    st.subheader("📋 Logs & Monitoring")

    if not st.session_state.logs:
        st.info("📝 No logs yet. Start a scrape to see progress.")
        return

    log_levels = ["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG"]
    default_levels = ["INFO", "SUCCESS", "WARNING", "ERROR"] if not st.session_state.debug_mode else log_levels

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        log_filter = st.multiselect("Filter logs:", options=log_levels, default=default_levels)
    with c2:
        if st.button("🗑️ Clear Logs"):
            st.session_state.logs = []
            st.rerun()
    with c3:
        if st.button("📋 Copy Logs"):
            log_text = "\n".join([f"[{log['timestamp']}][{log['level']}] {log['message']}" for log in st.session_state.logs])
            st.code(log_text)
            st.success("Logs copied to clipboard area above.")

    # Filter logs
    filtered_logs = [log for log in st.session_state.logs if log['level'] in log_filter]
    
    st.markdown('<div class="log-container">', unsafe_allow_html=True)
    if not filtered_logs:
        st.markdown("<p style='text-align:center; opacity:0.7;'>No logs match the current filter.</p>", unsafe_allow_html=True)
    else:
        for log in reversed(filtered_logs):
            icon_map = {"ERROR": "❌", "SUCCESS": "✅", "WARNING": "⚠️", "INFO": "ℹ️", "DEBUG": "🐞"}
            icon = icon_map.get(log['level'], "▪️")
            css_class = f"{log['level'].lower()}-box"
            
            # Use expander for long debug messages (tracebacks)
            if log['level'] == 'DEBUG' and len(log['message']) > 100:
                 with st.expander(f"{icon} **{log['timestamp']}** - {log['message'].splitlines()[0]}"):
                    st.code(log['message'], language='text')
            else:
                st.markdown(f'<div class="status-box {css_class}">{icon} <strong>{log["timestamp"]}</strong> - {log["message"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def get_file_info():
    """Gets metadata for all downloaded PDF files."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        return []
    
    files = []
    for filename in os.listdir(DOWNLOAD_FOLDER):
        if filename.endswith('.pdf'):
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            try:
                stat = os.stat(path)
                files.append({
                    "filename": filename, "path": path,
                    "size_mb": round(stat.st_size / (1024*1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
            except OSError:
                continue
    return sorted(files, key=lambda x: x['modified'], reverse=True)


def display_file_management(files: List[Dict]):
    """Displays the file management UI with pagination."""
    st.subheader("📄 File Management")

    if not files:
        st.info("No PDF files found in the download folder yet.")
        return

    # --- Filtering and Sorting ---
    c1, c2, c3 = st.columns(3)
    with c1:
        sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Size (Largest)", "Size (Smallest)", "Name (A-Z)"])
    with c2:
        search_term = st.text_input("Search files by name", placeholder="e.g., 'attention'")
    
    # Apply filtering and sorting
    filtered_files = files
    if search_term:
        filtered_files = [f for f in filtered_files if search_term.lower() in f['filename'].lower()]

    sort_map = {
        "Date (Newest)": lambda f: f['modified'],
        "Date (Oldest)": lambda f: f['modified'],
        "Size (Largest)": lambda f: f['size_mb'],
        "Size (Smallest)": lambda f: f['size_mb'],
        "Name (A-Z)": lambda f: f['filename'].lower()
    }
    reverse_map = {"Date (Oldest)": False, "Size (Smallest)": False, "Name (A-Z)": False}
    
    filtered_files.sort(key=sort_map[sort_by], reverse=reverse_map.get(sort_by, True))

    # --- Pagination ---
    PAGE_SIZE = 10
    total_pages = (len(filtered_files) - 1) // PAGE_SIZE + 1
    page_num = st.session_state.current_file_page

    with c3:
        st.number_input(f"Page (1-{total_pages})", min_value=1, max_value=total_pages, key="current_file_page")

    start_idx = (page_num - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_files = filtered_files[start_idx:end_idx]

    st.write(f"Showing **{len(paginated_files)}** of **{len(filtered_files)}** files. Page **{page_num}** of **{total_pages}**.")

    # --- File Display ---
    for i, file in enumerate(paginated_files):
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1:
                st.write(f"**{file['filename']}**")
                st.caption(f"Modified: {file['modified'].strftime('%Y-%m-%d %H:%M:%S')} | Size: {file['size_mb']:.2f} MB")
            with c3:
                if st.button("Delete", key=f"del_{file['path']}", type="secondary"):
                    try:
                        os.remove(file['path'])
                        st.success(f"Deleted {file['filename']}")
                        time.sleep(0.5) # Give time for user to see message
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    st.divider()

    # --- Bulk Operations ---
    st.subheader("🔧 Bulk Operations")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📁 Open Download Folder", use_container_width=True):
            open_file_location()
    with c2:
        csv = pd.DataFrame(files).to_csv(index=False).encode('utf-8')
        st.download_button("📊 Export File List (CSV)", data=csv, file_name="file_list.csv", mime="text/csv", use_container_width=True)
    with c3:
        with st.expander("⚠️ Danger Zone"):
            if st.button("🔥 Delete ALL Files", type="primary", use_container_width=True):
                count = 0
                for file in files:
                    try:
                        os.remove(file['path'])
                        count += 1
                    except OSError:
                        pass
                st.success(f"Successfully deleted {count} files.")
                time.sleep(1)
                st.rerun()


# --- Main Application ---
def main():
    initialize_session_state()

    st.markdown('<h1 class="main-header">📚 Academic Paper Scraper Pro+</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Enhanced paper discovery and download system</p>', unsafe_allow_html=True)

    display_status_indicator()

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.header("🛠️ Configuration")

        # Quick Search
        suggestions = ["machine learning", "large language models", "computer vision", "quantum computing", "cybersecurity"]
        query = st.text_input("Search Query", "transformer attention")
        st.selectbox("Popular topics (for ideas)", [""] + suggestions, index=0, key="suggestion_box")

        # Favorite Queries
        if st.button("⭐ Save Query as Favorite"):
            if query and query not in st.session_state.favorite_queries:
                st.session_state.favorite_queries.append(query)
                st.success("Saved!")
        if st.session_state.favorite_queries:
            fav = st.selectbox("⭐ Favorites", [""] + st.session_state.favorite_queries)
            if fav:
                query = fav # Overwrites the text input if a favorite is selected
                st.rerun()

        # Core Parameters
        max_results = st.slider("Max Results", 1, 50, 10)
        sort_options = {"Most Relevant": "relevance", "Most Cited": "paper-citations", "Newest": "newest"}
        sort_type = st.selectbox("Sort By", list(sort_options.keys()))

        # Advanced Mode
        st.session_state.advanced_mode = st.checkbox("🔬 Advanced Mode", st.session_state.advanced_mode)
        if st.session_state.advanced_mode:
            with st.container(border=True):
                st.write("**Paper Types**")
                include_conferences = st.checkbox("Conference Papers", True)
                include_journals = st.checkbox("Journal Papers", True)
                st.write("**Date Range (optional)**")
                c1, c2 = st.columns(2)
                start_year = c1.number_input("From", 1990, datetime.now().year, 2020)
                end_year = c2.number_input("To", 1990, datetime.now().year, datetime.now().year)
                min_citations = st.slider("Minimum Citations", 0, 500, 0)
        else:
            # Default values when advanced mode is off
            include_conferences, include_journals = True, True
            start_year, end_year, min_citations = None, None, None

        # Access Config
        st.subheader("🏛️ Access")
        institutional_access = st.checkbox("Use Institutional Access (IEEE)", help="Check if your network has institutional access.")
        proxy_url = st.text_input("Proxy URL (optional)", placeholder="e.g., http://user:pass@host:port") if institutional_access else None

    # --- Main Interface Tabs ---
    tab_search, tab_files, tab_logs, tab_settings = st.tabs(["🔍 Search", "🗂️ File Manager", "📋 Logs", "⚙️ Settings"])

    with tab_search:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("🚀 Start Scraping")
            # Config Summary
            with st.container(border=True):
                st.write(f"**Query:** `{query}`")
                st.write(f"**Max Results:** {max_results}, **Sort By:** {sort_type}")
                if st.session_state.advanced_mode:
                     st.write(f"**Advanced:** {start_year}-{end_year}, Min {min_citations} citations")
            
            # Start/Stop Button Logic
            if st.session_state.scraper_status != "Running":
                if st.button("📊 Start Scraping", type="primary", use_container_width=True, disabled=(not query)):
                    config = {
                        'query': query, 'max_results': max_results,
                        'sort_type': sort_options[sort_type],
                        'institutional_access': institutional_access, 'proxy_url': proxy_url,
                        # Advanced params
                        'include_conferences': include_conferences, 'include_journals': include_journals,
                        'start_year': start_year, 'end_year': end_year, 'min_citations': min_citations
                    }
                    
                    st.session_state.scraper_status = "Running"
                    st.session_state.logs = []
                    st.session_state.stop_event = threading.Event()
                    
                    thread = threading.Thread(target=run_scraper_thread, args=(config, st.session_state.stop_event))
                    thread.daemon = True
                    thread.start()
                    st.rerun()
            else:
                 if st.button("🛑 Force Stop", type="secondary", use_container_width=True):
                    if st.session_state.stop_event:
                        st.session_state.stop_event.set()
                    log_message("User requested to stop the scraper.", "WARNING")
                    st.rerun()

        with c2:
            st.subheader("📈 Quick Stats")
            files = get_file_info()
            last_24h_files = [f for f in files if f['modified'] > (datetime.now() - timedelta(hours=24))]
            
            c2a, c2b = st.columns(2)
            with c2a:
                render_metric("Total Files", len(files), "Total PDFs in your download folder.")
            with c2b:
                render_metric("Last 24h", len(last_24h_files), "Files downloaded in the last 24 hours.")
            
            render_metric("Current Session", st.session_state.downloaded_count, "Files downloaded in the current run.")

    with tab_files:
        files = get_file_info()
        display_file_management(files)

    with tab_logs:
        display_logs()

    with tab_settings:
        st.subheader("⚙️ App Settings")
        st.session_state.debug_mode = st.toggle("🐞 Enable Debug Mode", value=st.session_state.debug_mode, help="Show detailed logs, including error tracebacks.")
        st.subheader("💾 Data Management")
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.write(f"**Favorite Queries ({len(st.session_state.favorite_queries)})**")
                if st.button("Clear Favorites", use_container_width=True):
                    st.session_state.favorite_queries = []
                    st.success("Favorites cleared.")
        with c2:
            with st.container(border=True):
                st.write(f"**Search History ({len(st.session_state.search_history)})**")
                if st.button("Clear History", use_container_width=True):
                    st.session_state.search_history = []
                    st.success("History cleared.")
        
        st.subheader("📁 Folder Management")
        with st.container(border=True):
             st.code(os.path.abspath(DOWNLOAD_FOLDER))
             with st.expander("⚠️ Danger Zone: Reset Folder"):
                st.warning("This will delete the entire download folder and all its contents, then recreate it. This action cannot be undone.")
                if st.button("🔥 Permanently Reset Folder", type="primary"):
                    import shutil
                    try:
                        shutil.rmtree(DOWNLOAD_FOLDER)
                        os.makedirs(DOWNLOAD_FOLDER)
                        st.success("Folder has been reset.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to reset folder: {e}")

    # --- Auto-refresh logic ---
    if st.session_state.scraper_status == "Running":
        time.sleep(2)  # Refresh interval
        st.rerun()

if __name__ == "__main__":
    main()