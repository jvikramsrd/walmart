import streamlit as st
import os
from PIL import Image
from streamlit_option_menu import option_menu
from tabs import TABS
from utils.helpers import show_notification

# Set page configuration
st.set_page_config(
    page_title="Walmart Logistics Dashboard",
    page_icon="assets/walmart_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for professional look
st.markdown("""
<style>
    body {
        background-color: #f4f6fa;
    }
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #0071ce;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
    }
    .section-header {
        font-size: 1.3rem !important;
        font-weight: 600;
        color: #222;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .stSidebar {
        background: #fff;
        border-right: 1px solid #e0e0e0;
    }
    .sidebar-logo {
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .sidebar-user {
        background: #f4f6fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #333;
    }
    .stButton>button {
        background-color: #0071ce;
        color: white;
        border-radius: 5px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover {
        background-color: #005fa3;
    }
    .stMetric {
        background-color: #fff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .stDataFrame, .stTable {
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        padding: 1rem;
    }
    .stExpander {
        background: #f8f9fb;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #f4f6fa;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #0071ce;
    }
    .stTabs [aria-selected="true"] {
        background: #fff;
        border-bottom: 2px solid #0071ce;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        padding: 10px 0;
        background: #f8f9fa;
        border-radius: 6px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Logo
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "walmart_logo.png")
    avatar_path = os.path.join(assets_dir, "admin_avatar.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=160)
    else:
        st.markdown('<div class="sidebar-logo"><b>Walmart</b></div>', unsafe_allow_html=True)
    # Admin profile image (use placeholder if missing)
    if os.path.exists(avatar_path):
        st.image(avatar_path, width=80)
    else:
        st.image("https://ui-avatars.com/api/?name=Admin+User&background=0071ce&color=fff&size=80&rounded=true", width=80)
    st.markdown('<div class="sidebar-user"><b>Admin User</b><br>Last login: June 24, 2025</div>', unsafe_allow_html=True)
    st.markdown("## Logistics Dashboard")
    selected_tab = option_menu(
        "Navigation",
        list(TABS.keys()),
        icons=['box', 'journal', 'truck', 'building', 'cpu'],
        menu_icon="list",
        default_index=0,
    )
    st.markdown("---")

# Main content
st.markdown('<p class="main-header">Walmart Logistics Dashboard</p>', unsafe_allow_html=True)

# Initialize session state for notifications
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Add loading spinner for tab loading
with st.spinner('Loading dashboard...'):
    TABS[selected_tab].app()

# Footer
st.markdown('<div class="footer">Walmart Logistics System • © 2025</div>', unsafe_allow_html=True)

# Notifications
if st.session_state.notifications:
    notification = st.session_state.notifications.pop(0)
    show_notification(notification['message'], notification['type'])
