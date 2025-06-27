import streamlit as st
from utils.api import login

def app():
    """
    Renders the login page for the Walmart Logistics Dashboard.
    """
    st.markdown("<h1 style='text-align: center;'>Walmart Logistics Login</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Default is 'admin'"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Default is 'admin'"
            )
            submit_button = st.form_submit_button("Login")

            if submit_button:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    success, error_message = login(username, password)
                    if success:
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {error_message}") 