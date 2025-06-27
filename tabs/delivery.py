import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import folium_static
from utils.api import get_data, patch_data
from utils.helpers import display_kpi_metrics, format_date, show_notification

@st.cache_data(ttl=10)
def fetch_deliveries():
    return get_data("deliveries")

def app():
    """
    Renders the Delivery Tracking page.
    """
    st.header("Delivery Tracking")

    deliveries = fetch_deliveries()

    if deliveries is None:
        st.warning("Could not fetch delivery data. The backend might be down or you might not have access.")
        return

    df = pd.DataFrame(deliveries)

    # --- KPIs ---
    st.subheader("Key Metrics")
    if not df.empty:
        today = datetime.datetime.now().date()
        df['delivery_date_dt'] = pd.to_datetime(df['delivery_date']).dt.date
        
        pending_deliveries = df[df['status'] == 'in-transit'].shape[0]
        deliveries_today = df[df['delivery_date_dt'] == today].shape[0]
        failed_deliveries = df[df['status'] == 'failed'].shape[0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🚚 Deliveries In-Transit", pending_deliveries)
        col2.metric("📦 Deliveries Today", deliveries_today)
        col3.metric("❌ Failed Deliveries", failed_deliveries)
    else:
        st.info("No delivery data to display KPIs.")

    st.markdown("---")

    # --- Data Display ---
    st.subheader("All Deliveries")
    if not df.empty:
        st.dataframe(df.drop(columns=['delivery_date_dt']), use_container_width=True)
    else:
        st.info("No delivery records found.")

    st.markdown("---")
    
    # --- Reschedule Failed Deliveries ---
    st.subheader("Reschedule Failed Deliveries")
    if not df.empty:
        failed_df = df[df['status'] == 'failed']
        if not failed_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                delivery_id = st.selectbox(
                    "Select Failed Delivery ID", 
                    failed_df['delivery_id'].tolist(),
                    key="reschedule_delivery_id"
                )
            with col2:
                new_date = st.date_input(
                    "New Delivery Date", 
                    datetime.date.today() + datetime.timedelta(days=1),
                    key="reschedule_date_input"
                )
            
            if st.button("Reschedule Delivery", key="reschedule_button"):
                payload = {
                    "status": "rescheduled",
                    "delivery_date": new_date.isoformat()
                }
                success, error = patch_data(f"deliveries/{delivery_id}", payload)
                if success:
                    st.success(f"Delivery #{delivery_id} has been rescheduled to {new_date}.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Failed to reschedule: {error}")
        else:
            st.info("No failed deliveries to reschedule.")
    
    st.markdown("---")

    # --- Live Map ---
    st.subheader("Live Delivery Tracking Map")
    if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
        # Filter for relevant deliveries to display on map (e.g., not delivered)
        map_df = df[df['status'].isin(['in-transit', 'pending', 'rescheduled'])]
        
        if not map_df.empty:
            avg_lat = map_df['latitude'].mean()
            avg_lng = map_df['longitude'].mean()
            
            m = folium.Map(location=[avg_lat, avg_lng], zoom_start=6)

            for _, row in map_df.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"ID: {row['delivery_id']}<br>Status: {row['status']}",
                    icon=folium.Icon(color='blue', icon='truck', prefix='fa')
                ).add_to(m)
            
            folium_static(m)
        else:
            st.info("No active deliveries to display on the map.")
    else:
        st.info("No location data available for map.")
