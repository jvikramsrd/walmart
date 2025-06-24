import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import folium_static
from utils.api import get_data, put_data
from utils.helpers import display_kpi_metrics, format_date, show_notification

def app():
    st.header("🚚 Delivery Tracking")
    
    # Get delivery data
    deliveries = get_data("deliveries")
    
    # Display KPIs
    if deliveries:
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        deliveries_today = sum(1 for delivery in deliveries if format_date(delivery.get('delivery_date', '')) == today)
        failed_deliveries = sum(1 for delivery in deliveries if delivery.get('status') == 'failed')
        
        kpi_data = {
            'deliveries_pending': sum(1 for delivery in deliveries if delivery.get('status') == 'in-transit'),
            'orders_today': deliveries_today,
            'orders_delta': f"+{deliveries_today} today",
            'low_stock': failed_deliveries,
            'low_stock_delta': f"{failed_deliveries} failed" if failed_deliveries > 0 else "0 failed"
        }
        
        display_kpi_metrics(kpi_data)
    
    # Filters
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        # Date filter
        with col1:
            min_date = datetime.datetime.today() - datetime.timedelta(days=7)
            max_date = datetime.datetime.today() + datetime.timedelta(days=7)
            date_filter = st.date_input(
                "Delivery Date",
                datetime.datetime.today(),
                min_value=min_date,
                max_value=max_date
            )
        
        # Agent filter
        with col2:
            if deliveries:
                agents = list(set(delivery.get('agent_id', '') for delivery in deliveries))
                agent_filter = st.selectbox("Agent", ["All"] + agents)
            else:
                agent_filter = st.selectbox("Agent", ["All"])
        
        # Region filter
        with col3:
            if deliveries:
                regions = list(set(delivery.get('region', '') for delivery in deliveries))
                region_filter = st.selectbox("Region", ["All"] + regions)
            else:
                region_filter = st.selectbox("Region", ["All"])
    
    # Delivery tracking table
    if deliveries:
        df = pd.DataFrame(deliveries)
        
        # Apply filters
        if not df.empty:
            # Convert date string to datetime for filtering
            df['delivery_date'] = pd.to_datetime(df['delivery_date'])
            
            # Apply date filter
            if isinstance(date_filter, datetime.date):
                df = df[df['delivery_date'].dt.date == date_filter]
            
            # Apply agent filter
            if agent_filter != "All":
                df = df[df['agent_id'] == agent_filter]
            
            # Apply region filter
            if region_filter != "All":
                df = df[df['region'] == region_filter]
            
            if not df.empty:
                # Format date for display
                df['delivery_date'] = df['delivery_date'].dt.strftime('%Y-%m-%d')
                df['eta'] = pd.to_datetime(df['eta']).dt.strftime('%H:%M')
                
                # Display the table
                st.dataframe(df)
                
                # Show failed deliveries
                failed = df[df['status'] == 'failed']
                if not failed.empty:
                    st.subheader("Failed Deliveries")
                    st.dataframe(failed)
                    
                    # Reschedule action
                    st.subheader("Reschedule Delivery")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        delivery_id = st.selectbox("Select Delivery ID", failed['delivery_id'].tolist())
                    
                    with col2:
                        reschedule_date = st.date_input(
                            "New Delivery Date",
                            datetime.datetime.today() + datetime.timedelta(days=1)
                        )
                    
                    if st.button("Reschedule"):
                        success, _ = put_data(f"deliveries/{delivery_id}", {
                            "status": "rescheduled",
                            "delivery_date": reschedule_date.isoformat()
                        })
                        
                        if success:
                            show_notification(f"Delivery #{delivery_id} has been rescheduled.", "success")
                            st.experimental_rerun()
                        else:
                            show_notification("Failed to reschedule delivery.", "error")
                
                # Live map with delivery locations
                st.subheader("Live Delivery Tracking")
                
                # Create a map centered at an average location of all deliveries
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    avg_lat = df['latitude'].mean()
                    avg_lng = df['longitude'].mean()
                    
                    m = folium.Map(location=[avg_lat, avg_lng], zoom_start=10)
                    
                    # Add markers for each delivery
                    for idx, row in df.iterrows():
                        if 'latitude' in row and 'longitude' in row:
                            status_color = {
                                'delivered': 'green',
                                'in-transit': 'blue',
                                'pending': 'orange',
                                'failed': 'red',
                                'rescheduled': 'purple'
                            }.get(row.get('status', ''), 'gray')
                            
                            popup_text = f"""
                            <b>Delivery ID:</b> {row.get('delivery_id', '')}<br>
                            <b>Status:</b> {row.get('status', '')}<br>
                            <b>ETA:</b> {row.get('eta', '')}<br>
                            <b>Agent:</b> {row.get('agent_id', '')}
                            """
                            
                            folium.Marker(
                                location=[row['latitude'], row['longitude']],
                                popup=folium.Popup(popup_text, max_width=300),
                                icon=folium.Icon(color=status_color, icon="truck", prefix="fa")
                            ).add_to(m)
                    
                    # Display the map
                    folium_static(m)
                else:
                    st.info("No location data available for map visualization.")
            else:
                st.info("No deliveries match the selected filters.")
        else:
            st.info("No delivery data available.")
    else:
        st.warning("Could not fetch delivery data. Please check API connection.")
