import streamlit as st
import pandas as pd
import io
import folium
from streamlit_folium import folium_static
from utils.api import post_data

def app():
    """
    Renders the Route Optimizer page.
    """
    st.header("Route Optimizer")

    # --- Address Input ---
    addresses = []
    input_method = st.radio(
        "Select Address Input Method",
        ["Enter Manually", "Upload File"],
        key="optimizer_input_method"
    )

    if input_method == "Enter Manually":
        address_text = st.text_area(
            "Enter delivery addresses (one per line)",
            height=150,
            key="optimizer_address_text"
        )
        if address_text:
            addresses = [addr.strip() for addr in address_text.split('\\n') if addr.strip()]
    else:
        uploaded_file = st.file_uploader(
            "Upload a CSV or TXT file",
            type=["csv", "txt"],
            key="optimizer_file_uploader"
        )
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    # Simple assumption: the first column has the addresses
                    addresses = df.iloc[:, 0].dropna().astype(str).tolist()
                else:
                    string_data = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                    addresses = [line.strip() for line in string_data.split('\\n') if line.strip()]
                st.success(f"Successfully loaded {len(addresses)} addresses from {uploaded_file.name}.")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # --- Optimization ---
    if addresses:
        st.info(f"{len(addresses)} addresses loaded.")
        if st.button("Optimize Route", key="optimize_button"):
            with st.spinner("Optimizing..."):
                payload = {"addresses": addresses}
                result, error = post_data("optimize_route", payload)

                if error:
                    st.error(f"Optimization failed: {error}")
                elif result and result.get("success"):
                    st.success("Route optimized successfully!")
                    
                    # Store result in session state to persist it
                    st.session_state['optimization_result'] = result
                else:
                    st.error("Optimization failed. The optimizer returned an unexpected result.")
    
    # --- Display Results ---
    if 'optimization_result' in st.session_state:
        result = st.session_state['optimization_result']
        
        st.subheader("Optimized Route")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Distance", f"{result.get('total_distance', 0):.2f} mi")
        col2.metric("Total Time", f"{result.get('total_time', 0):.2f} hrs")
        col3.metric("CO2 Emissions", f"{result.get('co2_emissions', 0):.2f} kg")

        # Route Table
        route_df = pd.DataFrame(result.get("route", []), columns=["Stop", "Address"])
        st.table(route_df)

        # Map
        st.subheader("Route Map")
        coords = result.get("coordinates", [])
        if coords:
            map_center = [pd.Series([c[0] for c in coords]).mean(), pd.Series([c[1] for c in coords]).mean()]
            m = folium.Map(location=map_center, zoom_start=12)
            
            # Start and End points
            folium.Marker(coords[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(coords[-1], popup="End", icon=folium.Icon(color="red")).add_to(m)
            
            # Polyline
            folium.PolyLine(coords, weight=5, color='blue').add_to(m)
            
            folium_static(m, width=700, height=500)
        else:
            st.warning("No coordinates available to display map.")
