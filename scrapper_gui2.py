import streamlit as st
import os
import json
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import platform

# Import the scraper class (assuming scrapper.py is in the same directory)
try:
    from scrapper import EnhancedPaperScraper, DOWNLOAD_FOLDER
except ImportError:
    st.error("Could not import scrapper.py. Make sure it's in the same directory as this GUI file.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Academic Paper Scraper Pro",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: var(--text-color);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: var(--text-color);
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .success-box {
        background-color: rgba(40, 167, 69, 0.2);
        border-left: 5px solid #28a745;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 5px solid #dc3545;
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.5rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .config-summary {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .log-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem;
        background: #ffffff;
    }
    
    .file-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .file-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .search-tips {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .progress-ring {
        width: 60px;
        height: 60px;
        margin: 10px auto;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-running {
        background-color: #28a745;
        animation: pulse 2s infinite;
    }
    
    .status-idle {
        background-color: #6c757d;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .advanced-toggle {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .advanced-toggle:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with enhanced features
if 'scraper_running' not in st.session_state:
    st.session_state.scraper_running = False
if 'scraper_results' not in st.session_state:
    st.session_state.scraper_results = []
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'downloaded_count' not in st.session_state:
    st.session_state.downloaded_count = 0
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_scrape_time' not in st.session_state:
    st.session_state.last_scrape_time = None
if 'scraper_start_time' not in st.session_state:
    st.session_state.scraper_start_time = None
if 'advanced_mode' not in st.session_state:
    st.session_state.advanced_mode = False
if 'favorite_queries' not in st.session_state:
    st.session_state.favorite_queries = []

def log_message(message: str, level: str = "INFO"):
    """Add a log message to the session state with enhanced formatting"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({
        "timestamp": timestamp,
        "level": level,
        "message": message,
        "full_timestamp": datetime.now()
    })
    # Keep only last 100 logs to prevent memory issues
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]

def clear_logs():
    """Clear all logs"""
    st.session_state.logs = []

def save_search_to_history(query: str, results: int):
    """Save successful search to history"""
    search_entry = {
        "query": query,
        "results": results,
        "timestamp": datetime.now(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.search_history.insert(0, search_entry)
    # Keep only last 20 searches
    if len(st.session_state.search_history) > 20:
        st.session_state.search_history = st.session_state.search_history[:20]

def run_scraper_thread(config: Dict):
    """Run the scraper in a separate thread with enhanced logging"""
    try:
        st.session_state.scraper_start_time = datetime.now()
        log_message("🚀 Initializing enhanced scraper...", "INFO")
        
        scraper = EnhancedPaperScraper(
            institutional_access=config['institutional_access'],
            proxy_url=config.get('proxy_url'),
            include_conferences=config['include_conferences'],
            include_journals=config['include_journals']
        )
        
        # Override the scraper's search parameters
        if hasattr(scraper, 'SEARCH_PARAMS'):
            scraper.SEARCH_PARAMS = {
                "queryText": config['query'],
                "sortType": config['sort_type']
            }
        
        log_message(f"🔍 Starting search for: '{config['query']}'", "INFO")
        log_message(f"📊 Max results: {config['max_results']}", "INFO")
        log_message(f"🔄 Sort by: {config['sort_type']}", "INFO")
        
        try:
            downloaded = scraper.run()
            st.session_state.downloaded_count = downloaded
            
            if downloaded > 0:
                log_message(f"✅ Scraping completed successfully! Downloaded {downloaded} papers", "SUCCESS")
                save_search_to_history(config['query'], downloaded)
                st.session_state.last_scrape_time = datetime.now()
            else:
                log_message("⚠️ No papers were downloaded. Try adjusting your search terms.", "WARNING")
                
        except Exception as e:
            log_message(f"❌ Error during scraping: {str(e)}", "ERROR")
            
    except Exception as e:
        log_message(f"💥 Failed to initialize scraper: {str(e)}", "ERROR")
    finally:
        st.session_state.scraper_running = False

def display_enhanced_logs():
    """Display logs with enhanced formatting and filtering"""
    if not st.session_state.logs:
        st.info("📝 No logs yet. Start scraping to see progress updates.")
        return
        
    # Log filtering options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        log_filter = st.multiselect(
            "Filter logs by level:",
            options=["INFO", "SUCCESS", "WARNING", "ERROR"],
            default=["INFO", "SUCCESS", "WARNING", "ERROR"],
            key="log_filter"
        )
    
    with col2:
        show_count = st.selectbox("Show last:", [10, 20, 50, 100], index=1, key="log_count")
    
    with col3:
        if st.button("🗑️ Clear Logs", key="clear_logs_btn"):
            clear_logs()
            st.rerun()
    
    # Filter and display logs
    filtered_logs = [log for log in st.session_state.logs if log['level'] in log_filter]
    recent_logs = filtered_logs[-show_count:]
    
    st.markdown('<div class="log-container">', unsafe_allow_html=True)
    
    for log in recent_logs:
        level = log['level']
        icon_map = {
            "ERROR": "❌",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "INFO": "ℹ️"
        }
        
        icon = icon_map.get(level, "ℹ️")
        css_class = f"{level.lower()}-box"
        
        st.markdown(
            f'<div class="status-box {css_class}">'
            f'{icon} <strong>{log["timestamp"]}</strong> - {log["message"]}'
            f'</div>', 
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_enhanced_file_info():
    """Get enhanced information about downloaded files"""
    if not os.path.exists(DOWNLOAD_FOLDER):
        return []
    
    files = []
    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.endswith('.pdf'):
            file_path = os.path.join(DOWNLOAD_FOLDER, file)
            try:
                stat = os.stat(file_path)
                files.append({
                    "filename": file,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "path": file_path
                })
            except OSError:
                continue
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

def display_file_analytics():
    """Display analytics about downloaded files"""
    files = get_enhanced_file_info()
    
    if not files:
        return
    
    # Basic stats
    total_files = len(files)
    total_size_mb = sum(f['size_mb'] for f in files)
    avg_size_mb = total_size_mb / total_files if total_files > 0 else 0
    
    # Time-based analytics
    now = datetime.now()
    today_files = [f for f in files if f['modified'].date() == now.date()]
    week_files = [f for f in files if f['modified'] >= (now - timedelta(days=7))]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <p class="metric-number">{total_files}</p>
            <p class="metric-label">Total Files</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <p class="metric-number">{total_size_mb:.1f}</p>
            <p class="metric-label">Total Size (MB)</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <p class="metric-number">{len(today_files)}</p>
            <p class="metric-label">Today</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <p class="metric-number">{len(week_files)}</p>
            <p class="metric-label">This Week</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Size distribution chart
    if len(files) > 1:
        st.subheader("📊 File Size Distribution")
        
        df = pd.DataFrame(files)
        fig = px.histogram(
            df, 
            x='size_mb', 
            nbins=min(20, len(files)),
            title="Distribution of File Sizes",
            labels={'size_mb': 'File Size (MB)', 'count': 'Number of Files'},
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

def open_file_location():
    """Open the download folder in the system file manager"""
    try:
        if platform.system() == "Windows":
            os.startfile(DOWNLOAD_FOLDER)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", DOWNLOAD_FOLDER])
        else:  # Linux
            subprocess.run(["xdg-open", DOWNLOAD_FOLDER])
        return True
    except Exception as e:
        st.error(f"Could not open folder: {str(e)}")
        return False

def display_search_history():
    """Display search history with analytics"""
    if not st.session_state.search_history:
        st.info("🔍 No search history yet. Complete some searches to see analytics here.")
        return
    
    st.subheader("📈 Search History & Analytics")
    
    # Recent searches
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Recent Searches:**")
        for i, search in enumerate(st.session_state.search_history[:5]):
            success_rate = "✅" if search['results'] > 0 else "⚠️"
            st.write(f"{success_rate} `{search['query']}` - {search['results']} results - {search['date']}")
    
    with col2:
        if st.session_state.search_history:
            total_searches = len(st.session_state.search_history)
            successful_searches = len([s for s in st.session_state.search_history if s['results'] > 0])
            success_rate = (successful_searches / total_searches * 100) if total_searches > 0 else 0
            
            st.metric("Success Rate", f"{success_rate:.1f}%")
            st.metric("Total Searches", total_searches)

def create_search_suggestions():
    """Create intelligent search suggestions"""
    suggestions = [
        "machine learning neural networks",
        "deep learning computer vision", 
        "natural language processing transformers",
        "artificial intelligence ethics",
        "quantum computing algorithms",
        "blockchain cryptocurrency",
        "cybersecurity machine learning",
        "robotics autonomous systems",
        "big data analytics",
        "cloud computing security"
    ]
    
    return suggestions

def main():
    # Enhanced header with subtitle
    st.markdown('<h1 class="main-header">📚 Academic Paper Scraper Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Intelligent paper discovery and download system</p>', unsafe_allow_html=True)
    
    # Status indicator
    status_class = "status-running" if st.session_state.scraper_running else "status-idle"
    status_text = "Running" if st.session_state.scraper_running else "Idle"
    
    st.markdown(f'''
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="status-indicator {status_class}"></span>
        <strong>Status: {status_text}</strong>
        {f" | Started: {st.session_state.scraper_start_time.strftime('%H:%M:%S')}" if st.session_state.scraper_start_time and st.session_state.scraper_running else ""}
    </div>
    ''', unsafe_allow_html=True)
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search & Download", "📊 Analytics", "📋 Logs", "⚙️ Settings"])
    
    with tab1:
        # Sidebar configuration with enhanced features
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Quick search suggestions
            st.subheader("💡 Quick Suggestions")
            suggestions = create_search_suggestions()
            selected_suggestion = st.selectbox(
                "Popular searches:",
                options=[""] + suggestions,
                help="Click to use a popular search term"
            )
            
            # Search parameters
            st.subheader("🔍 Search Parameters")
            
            # Use suggestion if selected
            default_query = selected_suggestion if selected_suggestion else "transformer attention"
            query = st.text_input(
                "Search Query",
                value=default_query,
                help="Enter keywords to search for papers",
                key="search_query"
            )
            
            # Favorite queries management
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⭐ Save", help="Save current query as favorite"):
                    if query and query not in st.session_state.favorite_queries:
                        st.session_state.favorite_queries.append(query)
                        st.success("Saved!")
            
            with col2:
                if st.session_state.favorite_queries:
                    favorite = st.selectbox("⭐ Favorites", options=[""] + st.session_state.favorite_queries, key="fav_select")
                    if favorite:
                        st.session_state.search_query = favorite
                        st.rerun()
            
            max_results = st.slider(
                "Maximum Results",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of papers to download"
            )
            
            sort_options = {
                "Most Cited": "paper-citations",
                "Most Relevant": "relevance",
                "Newest First": "newest",
                "Oldest First": "oldest"
            }
            sort_type = st.selectbox(
                "Sort By",
                options=list(sort_options.keys()),
                index=0,
                help="How to sort the search results"
            )
            
            # Advanced mode toggle
            st.session_state.advanced_mode = st.checkbox("🔬 Advanced Mode", value=st.session_state.advanced_mode)
            
            if st.session_state.advanced_mode:
                st.markdown("---")
                st.subheader("🔬 Advanced Options")
                
                # Paper type preferences with more options
                st.write("**Paper Types:**")
                include_conferences = st.checkbox("Conference Papers", value=True)
                include_journals = st.checkbox("Journal Papers", value=True)
                
                # Date range filtering (if supported by scraper)
                st.write("**Date Range:**")
                col1, col2 = st.columns(2)
                with col1:
                    start_year = st.number_input("From Year", min_value=1990, max_value=2024, value=2020)
                with col2:
                    end_year = st.number_input("To Year", min_value=1990, max_value=2024, value=2024)
                
                # Quality filters
                min_citations = st.slider("Minimum Citations", min_value=0, max_value=100, value=0)
                
            else:
                include_conferences = True
                include_journals = True
            
            if not (include_conferences or include_journals):
                st.error("Please select at least one paper type!")
            
            # Institutional access
            st.subheader("🏛️ Access Configuration")
            institutional_access = st.checkbox(
                "Institutional Access to IEEE",
                help="Check if you have institutional access to IEEE Xplore"
            )
            
            proxy_url = None
            if institutional_access:
                use_proxy = st.checkbox("Use Proxy/VPN")
                if use_proxy:
                    proxy_url = st.text_input(
                        "Proxy URL",
                        placeholder="http://proxy.university.edu:8080",
                        help="Enter your institutional proxy URL"
                    )
            
            # Download settings
            st.subheader("📁 Download Settings")
            st.info(f"📂 Download folder: `{DOWNLOAD_FOLDER}`")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📁 Create Folder"):
                    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
                    st.success("Created!")
            
            with col2:
                if st.button("📂 Open Folder"):
                    open_file_location()
        
        # Main search interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🚀 Search Configuration")
            
            # Enhanced configuration summary
            st.markdown(f'''
            <div class="config-summary">
                <h4>📋 Current Configuration</h4>
                <p><strong>Query:</strong> <code>{query}</code></p>
                <p><strong>Max Results:</strong> {max_results} papers</p>
                <p><strong>Sort By:</strong> {sort_type}</p>
                <p><strong>Paper Types:</strong> {', '.join([t for t, enabled in [('Conferences', include_conferences), ('Journals', include_journals)] if enabled])}</p>
                <p><strong>Access:</strong> {'Institutional' if institutional_access else 'Public'}</p>
                {f'<p><strong>Advanced:</strong> Min {min_citations} citations, {start_year}-{end_year}</p>' if st.session_state.advanced_mode else ''}
            </div>
            ''', unsafe_allow_html=True)
            
            # Search tips
            st.markdown('''
            <div class="search-tips">
                <h4>💡 Search Tips</h4>
                <ul>
                    <li>Use specific technical terms for better results</li>
                    <li>Combine multiple keywords with spaces</li>
                    <li>Try different sorting options for varied results</li>
                    <li>Use institutional access for premium papers</li>
                </ul>
            </div>
            ''', unsafe_allow_html=True)
            
            # Enhanced start/stop button
            if not st.session_state.scraper_running:
                if st.button("🔍 Start Enhanced Scraping", type="primary", use_container_width=True):
                    if query.strip():
                        config = {
                            'query': query,
                            'max_results': max_results,
                            'sort_type': sort_options[sort_type],
                            'include_conferences': include_conferences,
                            'include_journals': include_journals,
                            'institutional_access': institutional_access,
                            'proxy_url': proxy_url if proxy_url else None
                        }
                        
                        st.session_state.scraper_running = True
                        st.session_state.downloaded_count = 0
                        clear_logs()
                        
                        # Start scraper in a separate thread
                        thread = threading.Thread(target=run_scraper_thread, args=(config,))
                        thread.daemon = True
                        thread.start()
                        
                        st.rerun()
                    else:
                        st.error("Please enter a search query!")
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.button("⏹️ Scraping in Progress...", disabled=True, use_container_width=True)
                with col_b:
                    if st.button("🛑 Force Stop", type="secondary", use_container_width=True):
                        st.session_state.scraper_running = False
                        log_message("🛑 Scraping stopped by user", "WARNING")
                        st.rerun()
                
                # Progress indicator
                if st.session_state.scraper_start_time:
                    elapsed = datetime.now() - st.session_state.scraper_start_time
                    st.info(f"⏱️ Running for {str(elapsed).split('.')[0]} | Downloaded: {st.session_state.downloaded_count} papers")
        
        with col2:
            st.subheader("📊 Quick Stats")
            
            # Enhanced metrics with recent activity
            files = get_enhanced_file_info()
            total_files = len(files)
            
            # Calculate recent activity
            now = datetime.now()
            recent_files = [f for f in files if f['modified'] >= (now - timedelta(hours=24))]
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.markdown(f'''
                <div class="metric-card">
                    <p class="metric-number">{total_files}</p>
                    <p class="metric-label">Total Files</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2b:
                st.markdown(f'''
                <div class="metric-card">
                    <p class="metric-number">{len(recent_files)}</p>
                    <p class="metric-label">Last 24h</p>
                </div>
                ''', unsafe_allow_html=True)
            
            # Session stats
            st.markdown(f'''
            <div class="metric-card">
                <p class="metric-number">{st.session_state.downloaded_count}</p>
                <p class="metric-label">Current Session</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Last scrape info
            if st.session_state.last_scrape_time:
                time_since = datetime.now() - st.session_state.last_scrape_time
                if time_since.total_seconds() < 3600:  # Less than 1 hour
                    time_str = f"{int(time_since.total_seconds() / 60)}m ago"
                else:
                    time_str = f"{int(time_since.total_seconds() / 3600)}h ago"
                
                st.markdown(f'''
                <div class="metric-card">
                    <p class="metric-number">✅</p>
                    <p class="metric-label">Last: {time_str}</p>
                </div>
                ''', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📊 File Analytics & Statistics")
        
        # Display comprehensive analytics
        display_file_analytics()
        
        # Search history analytics
        display_search_history()
        
        # File management section
        files = get_enhanced_file_info()
        if files:
            st.subheader("📄 File Management")
            
            # File filtering and sorting
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sort_by = st.selectbox(
                    "Sort files by:",
                    options=["Date (Newest)", "Date (Oldest)", "Size (Largest)", "Size (Smallest)", "Name (A-Z)", "Name (Z-A)"],
                    key="file_sort"
                )
            
            with col2:
                size_filter = st.selectbox(
                    "Filter by size:",
                    options=["All", "< 1 MB", "1-5 MB", "5-10 MB", "> 10 MB"],
                    key="size_filter"
                )
            
            with col3:
                date_filter = st.selectbox(
                    "Filter by date:",
                    options=["All", "Today", "This Week", "This Month", "Older"],
                    key="date_filter"
                )
            
            # Apply filters
            filtered_files = files.copy()
            
            # Size filtering
            if size_filter != "All":
                if size_filter == "< 1 MB":
                    filtered_files = [f for f in filtered_files if f['size_mb'] < 1]
                elif size_filter == "1-5 MB":
                    filtered_files = [f for f in filtered_files if 1 <= f['size_mb'] < 5]
                elif size_filter == "5-10 MB":
                    filtered_files = [f for f in filtered_files if 5 <= f['size_mb'] < 10]
                elif size_filter == "> 10 MB":
                    filtered_files = [f for f in filtered_files if f['size_mb'] >= 10]
            
            # Date filtering
            if date_filter != "All":
                now = datetime.now()
                if date_filter == "Today":
                    filtered_files = [f for f in filtered_files if f['modified'].date() == now.date()]
                elif date_filter == "This Week":
                    week_ago = now - timedelta(days=7)
                    filtered_files = [f for f in filtered_files if f['modified'] >= week_ago]
                elif date_filter == "This Month":
                    month_ago = now - timedelta(days=30)
                    filtered_files = [f for f in filtered_files if f['modified'] >= month_ago]
                elif date_filter == "Older":
                    month_ago = now - timedelta(days=30)
                    filtered_files = [f for f in filtered_files if f['modified'] < month_ago]
            
            # Apply sorting
            if sort_by == "Date (Newest)":
                filtered_files.sort(key=lambda x: x['modified'], reverse=True)
            elif sort_by == "Date (Oldest)":
                filtered_files.sort(key=lambda x: x['modified'])
            elif sort_by == "Size (Largest)":
                filtered_files.sort(key=lambda x: x['size_mb'], reverse=True)
            elif sort_by == "Size (Smallest)":
                filtered_files.sort(key=lambda x: x['size_mb'])
            elif sort_by == "Name (A-Z)":
                filtered_files.sort(key=lambda x: x['filename'].lower())
            elif sort_by == "Name (Z-A)":
                filtered_files.sort(key=lambda x: x['filename'].lower(), reverse=True)
            
            # Display filtered files
            st.write(f"**Showing {len(filtered_files)} of {len(files)} files**")
            
            if filtered_files:
                # Create enhanced file display
                for i, file in enumerate(filtered_files[:20]):  # Show max 20 files
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            # Truncate long filenames
                            display_name = file['filename']
                            if len(display_name) > 50:
                                display_name = display_name[:47] + "..."
                            st.write(f"**{display_name}**")
                            st.caption(f"Modified: {file['modified'].strftime('%Y-%m-%d %H:%M')}")
                        
                        with col2:
                            st.metric("Size", f"{file['size_mb']} MB")
                        
                        with col3:
                            # Age calculation
                            age = datetime.now() - file['modified']
                            if age.days > 0:
                                age_str = f"{age.days}d"
                            elif age.seconds > 3600:
                                age_str = f"{age.seconds // 3600}h"
                            else:
                                age_str = f"{age.seconds // 60}m"
                            st.metric("Age", age_str)
                        
                        with col4:
                            if st.button("🗑️ Delete", key=f"del_{i}", help="Delete this file"):
                                try:
                                    os.remove(file['path'])
                                    st.success(f"Deleted {file['filename']}")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting file: {str(e)}")
                        
                        st.divider()
                
                if len(filtered_files) > 20:
                    st.info(f"Showing first 20 files. {len(filtered_files) - 20} more files available.")
            
            # Bulk operations
            st.subheader("🔧 Bulk Operations")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📁 Open All Folder", use_container_width=True):
                    open_file_location()
            
            with col2:
                if st.button("📊 Export File List", use_container_width=True):
                    df = pd.DataFrame([{
                        'Filename': f['filename'],
                        'Size (MB)': f['size_mb'],
                        'Modified': f['modified'].strftime('%Y-%m-%d %H:%M:%S'),
                        'Created': f['created'].strftime('%Y-%m-%d %H:%M:%S')
                    } for f in files])
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"paper_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("⚠️ Delete All Files", use_container_width=True, type="secondary"):
                    if st.button("⚠️ Confirm Delete All", type="secondary"):
                        deleted_count = 0
                        for file in files:
                            try:
                                os.remove(file['path'])
                                deleted_count += 1
                            except Exception:
                                continue
                        st.success(f"Deleted {deleted_count} files")
                        time.sleep(1)
                        st.rerun()
        
        else:
            st.info("📄 No PDF files found. Start scraping to see analytics here.")
    
    with tab3:
        st.subheader("📋 Enhanced Logs & Monitoring")
        
        # Real-time status
        if st.session_state.scraper_running:
            st.markdown("""
            <div class="status-box info-box">
                <strong>🔄 Scraper is currently running...</strong><br>
                Real-time updates are enabled. Logs will refresh automatically.
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-refresh progress
            progress_placeholder = st.empty()
            with progress_placeholder:
                if st.session_state.scraper_start_time:
                    elapsed = datetime.now() - st.session_state.scraper_start_time
                    st.progress(min(elapsed.total_seconds() / 300, 1.0), text=f"Runtime: {str(elapsed).split('.')[0]}")
        
        # Enhanced log display
        display_enhanced_logs()
        
        # Log statistics
        if st.session_state.logs:
            st.subheader("📈 Log Statistics")
            
            # Count logs by level
            log_counts = {}
            for log in st.session_state.logs:
                level = log['level']
                log_counts[level] = log_counts.get(level, 0) + 1
            
            # Display log level distribution
            col1, col2, col3, col4 = st.columns(4)
            
            levels = ['INFO', 'SUCCESS', 'WARNING', 'ERROR']
            colors = ['#17a2b8', '#28a745', '#ffc107', '#dc3545']
            
            for i, (level, color) in enumerate(zip(levels, colors)):
                count = log_counts.get(level, 0)
                with [col1, col2, col3, col4][i]:
                    st.markdown(f'''
                    <div class="metric-card">
                        <p class="metric-number" style="color: {color};">{count}</p>
                        <p class="metric-label">{level}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Log timeline chart
            if len(st.session_state.logs) > 1:
                st.subheader("📊 Log Timeline")
                
                # Create timeline data
                log_df = pd.DataFrame(st.session_state.logs)
                log_df['minute'] = log_df['full_timestamp'].dt.floor('min')
                
                # Count logs per minute
                timeline_data = log_df.groupby(['minute', 'level']).size().reset_index(name='count')
                
                if not timeline_data.empty:
                    fig = px.line(
                        timeline_data, 
                        x='minute', 
                        y='count', 
                        color='level',
                        title="Log Activity Over Time",
                        labels={'minute': 'Time', 'count': 'Number of Logs'},
                        color_discrete_map={
                            'INFO': '#17a2b8',
                            'SUCCESS': '#28a745', 
                            'WARNING': '#ffc107',
                            'ERROR': '#dc3545'
                        }
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("⚙️ Advanced Settings & Preferences")
        
        # User preferences
        st.subheader("🎨 Interface Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Theme preferences (if applicable)
            st.selectbox("Theme", ["Auto", "Light", "Dark"], disabled=True, help="Theme settings coming soon")
            
            # Default search settings
            st.selectbox(
                "Default Sort Order",
                options=list(sort_options.keys()),
                index=0,
                key="default_sort",
                help="Your preferred default sort order for searches"
            )
        
        with col2:
            # Auto-refresh settings
            auto_refresh_interval = st.selectbox(
                "Auto-refresh Interval",
                options=[1, 2, 5, 10],
                index=1,
                help="How often to refresh logs during scraping (seconds)"
            )
            
            # Default max results
            default_max_results = st.slider(
                "Default Max Results",
                min_value=1,
                max_value=50,
                value=10,
                help="Your preferred default maximum results"
            )
        
        # Data management
        st.subheader("💾 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Search History**")
            st.write(f"Entries: {len(st.session_state.search_history)}")
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.search_history = []
                st.success("Search history cleared!")
        
        with col2:
            st.write("**Favorite Queries**")
            st.write(f"Saved: {len(st.session_state.favorite_queries)}")
            if st.button("🗑️ Clear Favorites", use_container_width=True):
                st.session_state.favorite_queries = []
                st.success("Favorites cleared!")
        
        with col3:
            st.write("**Session Logs**")
            st.write(f"Entries: {len(st.session_state.logs)}")
            if st.button("🗑️ Clear Logs", use_container_width=True):
                clear_logs()
                st.success("Logs cleared!")
        
        # Export/Import settings
        st.subheader("📤 Export/Import")
        
        # Export configuration
        current_config = {
            "favorite_queries": st.session_state.favorite_queries,
            "search_history": [
                {**h, "timestamp": h["timestamp"].isoformat()} 
                for h in st.session_state.search_history
            ],
            "preferences": {
                "default_max_results": default_max_results,
                "auto_refresh_interval": auto_refresh_interval
            }
        }
        
        config_json = json.dumps(current_config, indent=2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Export Settings",
                data=config_json,
                file_name=f"scraper_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            uploaded_file = st.file_uploader(
                "📤 Import Settings",
                type="json",
                help="Upload a previously exported configuration file"
            )
            
            if uploaded_file is not None:
                try:
                    imported_config = json.loads(uploaded_file.read())
                    
                    # Import favorites
                    if "favorite_queries" in imported_config:
                        st.session_state.favorite_queries = imported_config["favorite_queries"]
                    
                    # Import search history (with date conversion)
                    if "search_history" in imported_config:
                        for entry in imported_config["search_history"]:
                            entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
                        st.session_state.search_history = imported_config["search_history"]
                    
                    st.success("✅ Settings imported successfully!")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error importing settings: {str(e)}")
        
        # System information
        st.subheader("🔧 System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Download Folder**")
            st.code(DOWNLOAD_FOLDER)
            
            st.write("**Platform**")
            st.write(f"{platform.system()} {platform.release()}")
        
        with col2:
            st.write("**Python Version**")
            st.write(f"{sys.version.split()[0]}")
            
            st.write("**Streamlit Version**")
            st.write(st.__version__)
        
        # Folder management
        st.subheader("📁 Folder Management")
        
        if os.path.exists(DOWNLOAD_FOLDER):
            folder_size = sum(
                os.path.getsize(os.path.join(DOWNLOAD_FOLDER, f))
                for f in os.listdir(DOWNLOAD_FOLDER)
                if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))
            )
            folder_size_mb = folder_size / (1024 * 1024)
            
            st.metric("Folder Size", f"{folder_size_mb:.2f} MB")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📂 Open Folder", use_container_width=True):
                    open_file_location()
            
            with col2:
                if st.button("🧹 Clean Empty Files", use_container_width=True):
                    cleaned = 0
                    for file in os.listdir(DOWNLOAD_FOLDER):
                        file_path = os.path.join(DOWNLOAD_FOLDER, file)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                            os.remove(file_path)
                            cleaned += 1
                    st.success(f"Cleaned {cleaned} empty files")
            
            with col3:
                if st.button("⚠️ Reset Folder", use_container_width=True, type="secondary"):
                    if st.button("⚠️ Confirm Reset", type="secondary"):
                        import shutil
                        shutil.rmtree(DOWNLOAD_FOLDER)
                        os.makedirs(DOWNLOAD_FOLDER)
                        st.success("Folder reset successfully")
                        time.sleep(1)
                        st.rerun()
        else:
            st.warning("Download folder does not exist")
            if st.button("📁 Create Download Folder", use_container_width=True):
                os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
                st.success("Download folder created!")
                st.rerun()
    
    # Auto-refresh logic for running scraper
    if st.session_state.scraper_running:
        time.sleep(2)  # Wait 2 seconds
        st.rerun()
    
    # Enhanced footer with additional information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <h4 style="color: #667eea; margin-bottom: 1rem;">📚 Academic Paper Scraper Pro</h4>
        <p style="margin: 0.5rem 0;"><strong>Built with ❤️ using Streamlit</strong></p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem;">
            Features: Advanced Search • Real-time Monitoring • File Analytics • Batch Operations
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.8rem; color: #999;">
            ⚠️ Please ensure you comply with the terms of service of paper sources and respect copyright laws.
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.8rem; color: #999;">
            💡 For best results, use institutional access when available.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()