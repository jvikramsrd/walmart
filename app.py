import streamlit as st
import os
from PIL import Image
from streamlit_option_menu import option_menu
from tabs import TABS
from utils.helpers import show_notification

# Set page configuration
st.set_page_config(
    page_title="Walmart Logistics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 600;
        color: #0071ce;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #4a4a4a;
    }
    .logo-img {
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #0071ce;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #004c8c;
    }
    .stSidebar .stButton>button {
        width: 100%;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Logo
    try:
        # Check if the logo file exists in the assets directory
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "walmart_logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            st.image(logo, width=200, use_column_width=True)
        else:
            st.markdown("<h1>🛒 Walmart</h1>", unsafe_allow_html=True)
    except:
        st.markdown("<h1>🛒 Walmart</h1>", unsafe_allow_html=True)
    
    st.markdown("## Logistics Dashboard")
    
    # Navigation
    selected_tab = option_menu(
        "Navigation",
        list(TABS.keys()),
        icons=['box', 'journal', 'truck', 'building', 'cpu'],
        menu_icon="list",
        default_index=0,
    )
    
    # Space
    st.markdown("---")
    
    # Admin or user info
    st.markdown("### User Info")
    st.markdown("**Admin User**")
    st.markdown("Last login: June 24, 2025")
    
    # Bonus chatbot (UI only)
    st.markdown("---")
    st.markdown("### 🤖 Admin Assistant")
    
    with st.expander("AI Assistant"):
        st.text_input("Ask anything about the dashboard:", placeholder="Ex: How to add a new SKU?")
        st.button("Send")
        
    # Dark mode toggle
    st.markdown("---")
    if st.checkbox("Dark Mode"):
        st.markdown("""
        <style>
            body {
                color: #f1f1f1;
                background-color: #262730;
            }
            .css-18e3th9 {
                background-color: #262730;
            }
            .main-header {
                color: #4dabf5;
            }
            .stMetric {
                background-color: #3a3b47;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)

# Main content
st.markdown('<p class="main-header">🛒 Walmart Logistics Dashboard</p>', unsafe_allow_html=True)

# Initialize session state for notifications
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Display the selected tab
TABS[selected_tab].app()

# Footer
st.markdown("---")
st.markdown("Walmart Logistics System • © 2025")

# Notifications
if st.session_state.notifications:
    notification = st.session_state.notifications.pop(0)
    show_notification(notification['message'], notification['type'])
