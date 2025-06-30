import requests
import streamlit as st

# API Configuration
API_BASE = "http://localhost:8000/api"

def get_data(endpoint):
    """
    Gets data from a protected endpoint.
    """
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
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
        response = requests.post(f"{API_BASE}/{endpoint}", json=payload, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
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
        response = requests.patch(f"{API_BASE}/{endpoint}", json=payload, timeout=10)
        response.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
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
        response = requests.delete(f"{API_BASE}/{endpoint}", timeout=10)
        response.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", "Failed to delete data.")
        except Exception:
            detail = e.response.text or str(e)
        return False, detail
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"
    