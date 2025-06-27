import requests
import streamlit as st

# API Configuration
API_BASE = "http://localhost:3000/api"

def login(username, password):
    """
    Logs in the user and stores the token in the session state.
    """
    try:
        response = requests.post(
            f"{API_BASE}/login",
            data={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["auth_token"] = token
            st.session_state["logged_in"] = True
            return True, None
        else:
            error_message = response.json().get("detail", "Unknown login error")
            st.session_state["logged_in"] = False
            return False, error_message
    except requests.exceptions.RequestException as e:
        st.session_state["logged_in"] = False
        return False, f"Connection error: {e}"

def get_auth_headers():
    """
    Returns the authorization headers if a token exists.
    """
    if "auth_token" in st.session_state:
        return {"Authorization": f"Bearer {st.session_state['auth_token']}"}
    return {}

def get_data(endpoint):
    """
    Gets data from a protected endpoint.
    """
    try:
        headers = get_auth_headers()
        response = requests.get(f"{API_BASE}/{endpoint}", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.warning("Your session has expired. Please log in again.")
            st.session_state["logged_in"] = False
            st.rerun()
        else:
            try:
                detail = e.response.json().get('detail', str(e))
            except Exception:
                detail = e.response.text or str(e)
            st.error(f"Error fetching data: {detail}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error while fetching data: {e}")
        return None

def post_data(endpoint, payload):
    """
    Posts data to a protected endpoint.
    """
    try:
        headers = get_auth_headers()
        response = requests.post(f"{API_BASE}/{endpoint}", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.warning("Your session has expired. Please log in again.")
            st.session_state["logged_in"] = False
            st.rerun()
        try:
            detail = e.response.json().get("detail", "Failed to post data.")
        except Exception:
            detail = e.response.text or str(e)
        return None, detail
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

def patch_data(endpoint, payload):
    """
    Patches data on a protected endpoint.
    """
    try:
        headers = get_auth_headers()
        response = requests.patch(f"{API_BASE}/{endpoint}", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.warning("Your session has expired. Please log in again.")
            st.session_state["logged_in"] = False
            st.rerun()
        try:
            detail = e.response.json().get("detail", "Failed to update data.")
        except Exception:
            detail = e.response.text or str(e)
        return False, detail
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"

def delete_data(endpoint):
    """
    Deletes data from a protected endpoint.
    """
    try:
        headers = get_auth_headers()
        response = requests.delete(f"{API_BASE}/{endpoint}", headers=headers, timeout=10)
        response.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.warning("Your session has expired. Please log in again.")
            st.session_state["logged_in"] = False
            st.rerun()
        try:
            detail = e.response.json().get("detail", "Failed to delete data.")
        except Exception:
            detail = e.response.text or str(e)
        return False, detail
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"
    