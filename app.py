import streamlit as st
import os
from PIL import Image
from streamlit_option_menu import option_menu
from tabs import TABS

# --- Page Configuration ---
assets_dir = os.path.join(os.path.dirname(__file__), "assets")
logo_path = os.path.join(assets_dir, "walmart_logo.png")
st.set_page_config(
    page_title="Walmart Logistics Dashboard",
    page_icon=logo_path if os.path.exists(logo_path) else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS Styling ---
st.markdown("""
<link href="https://fonts.googleapis.com/css?family=Roboto:400,500,700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif !important; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1976d2; margin-bottom: 2rem; }
    .section-header { font-size: 1.5rem; font-weight: 600; color: #333; margin-top: 2rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app."""
    with st.sidebar:
        st.image(logo_path, width=150)
        st.markdown("## Navigation")

        # Get tab names and icons from the TABS dictionary
        tab_names = list(TABS.keys())
        tab_icons = [TABS[t].get('icon', 'box') for t in tab_names]

        selected_tab = option_menu(
            menu_title=None,
            options=tab_names,
            icons=tab_icons,
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        st.markdown("### User: `admin`")

    # Display the selected tab's content
    if selected_tab in TABS:
        st.markdown(f"<h1 class='main-header'>{selected_tab}</h1>", unsafe_allow_html=True)
        # Call the app function from the TABS dictionary
        TABS[selected_tab]['func']()
    else:
        st.error("The selected tab could not be found.")

if __name__ == "__main__":
    main()
