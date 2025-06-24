import streamlit as st
import pandas as pd
import numpy as np
import io
import folium
from streamlit_folium import folium_static
from utils.api import post_data
from utils.helpers import show_notification

def app():
    st.header("🧠 Route Optimizer")
    
    # Input methods: Text input or file upload
    input_method = st.radio("Select input method", ["Enter Addresses Manually", "Upload File"])
    
    addresses = []
    
    if input_method == "Enter Addresses Manually":
        address_text = st.text_area(
            "Enter delivery addresses (one per line)", 
            height=200,
            placeholder="123 Main St, New York, NY 10001\n456 Park Ave, New York, NY 10022\n..."
        )
        
        if address_text:
            addresses = [addr.strip() for addr in address_text.split('\n') if addr.strip()]
            
    else:  # File upload
        uploaded_file = st.file_uploader("Upload CSV or TXT file with addresses", type=["csv", "txt"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file)
                    # Try to find the address column
                    address_col = None
                    for col in df.columns:
                        if 'address' in col.lower():
                            address_col = col
                            break
                    
                    if address_col:
                        addresses = df[address_col].tolist()
                    else:
                        st.warning("Could not find address column. Please select the column:")
                        address_col = st.selectbox("Select address column", df.columns.tolist())
                        if address_col:
                            addresses = df[address_col].tolist()
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
            else:  # txt file
                try:
                    string_data = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                    addresses = [line.strip() for line in string_data.readlines() if line.strip()]
                except Exception as e:
                    st.error(f"Error reading text file: {str(e)}")
    
    # Display the addresses
    if addresses:
        st.subheader(f"Addresses to Optimize ({len(addresses)})")
        for i, addr in enumerate(addresses[:10], 1):
            st.text(f"{i}. {addr}")
            
        if len(addresses) > 10:
            st.text(f"...and {len(addresses) - 10} more addresses")
    
        # Advanced options
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                optimization_type = st.selectbox(
                    "Optimization Type",
                    ["Shortest Distance", "Fastest Time", "Eco-friendly (Less Emissions)"]
                )
                
                priority_stops = st.text_input(
                    "Priority Stops (comma-separated indices)",
                    placeholder="1,3,5"
                )
                
            with col2:
                max_route_time = st.slider(
                    "Max Route Time (hours)",
                    min_value=1,
                    max_value=12,
                    value=8
                )
                
                use_clustering = st.checkbox("Use Clustering for Multi-Route Optimization", value=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            optimize_button = st.button("🧮 Optimize Route")
            
        with col2:
            map_type = st.selectbox("Map Type", ["Standard", "Satellite"])
        
        # When optimize button is clicked
        if optimize_button and addresses:
            with st.spinner("Optimizing route..."):
                # Prepare payload
                payload = {
                    "addresses": addresses,
                    "optimization_type": optimization_type if 'optimization_type' in locals() else "Shortest Distance",
                    "priority_stops": [int(i.strip()) for i in priority_stops.split(",") if i.strip()] if 'priority_stops' in locals() and priority_stops else [],
                    "max_route_time": max_route_time if 'max_route_time' in locals() else 8,
                    "use_clustering": use_clustering if 'use_clustering' in locals() else True
                }
                
                # Call API to optimize route
                success, result = post_data("optimize_route", payload)
                
                if success and result:
                    # Extract results
                    route_details = result.get("route", [])
                    total_distance = result.get("total_distance", 0)
                    total_time = result.get("total_time", 0)
                    co2_emissions = result.get("co2_emissions", 0)
                    route_coords = result.get("coordinates", [])
                    
                    # Display route metrics
                    st.subheader("Route Metrics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Distance", f"{total_distance:.1f} miles")
                        
                    with col2:
                        st.metric("Estimated Time", f"{total_time:.1f} hours")
                        
                    with col3:
                        st.metric("CO2 Emissions", f"{co2_emissions:.1f} kg")
                    
                    # Display optimized route
                    st.subheader("Optimized Route Order")
                    
                    if route_details:
                        route_df = pd.DataFrame(route_details)
                        st.table(route_df)
                    
                    # Display map if coordinates are available
                    if route_coords and len(route_coords) > 1:
                        st.subheader("Route Map")
                        
                        # Calculate center point for map
                        center_lat = sum(coord[0] for coord in route_coords) / len(route_coords)
                        center_lng = sum(coord[1] for coord in route_coords) / len(route_coords)
                        
                        # Create map
                        m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
                        
                        # Add route line
                        folium.PolyLine(
                            locations=route_coords,
                            weight=5,
                            color='blue',
                            opacity=0.7
                        ).add_to(m)
                        
                        # Add markers for each stop
                        for i, coord in enumerate(route_coords):
                            popup_text = f"Stop {i+1}"
                            if i == 0:
                                popup_text = "Start"
                                icon_color = "green"
                            elif i == len(route_coords) - 1:
                                popup_text = "End"
                                icon_color = "red"
                            else:
                                icon_color = "blue"
                                
                            folium.Marker(
                                location=coord,
                                popup=popup_text,
                                icon=folium.Icon(color=icon_color, icon="info-sign")
                            ).add_to(m)
                        
                        # Display the map
                        folium_static(m)
                    else:
                        st.warning("No coordinate data available for map visualization.")
                        
                    # Bonus: DBSCAN clustering visualization for multi-route optimization
                    if 'use_clustering' in locals() and use_clustering and "clusters" in result:
                        st.subheader("Route Clustering Analysis")
                        
                        clusters = result.get("clusters", {})
                        
                        if clusters:
                            # Create cluster map
                            cluster_map = folium.Map(location=[center_lat, center_lng], zoom_start=11)
                            
                            # Generate distinct colors for clusters
                            colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                                      'lightred', 'darkblue', 'darkgreen', 'cadetblue']
                            
                            # Plot each cluster with its own color
                            for cluster_id, cluster_data in clusters.items():
                                color = colors[int(cluster_id) % len(colors)]
                                
                                # Add cluster points
                                for point in cluster_data.get("points", []):
                                    folium.CircleMarker(
                                        location=point,
                                        radius=5,
                                        color=color,
                                        fill=True,
                                        fill_opacity=0.7,
                                        popup=f"Cluster {cluster_id}"
                                    ).add_to(cluster_map)
                                    
                                # Add centroid
                                if "centroid" in cluster_data:
                                    folium.Marker(
                                        location=cluster_data["centroid"],
                                        popup=f"Cluster {cluster_id} Centroid",
                                        icon=folium.Icon(color=color, icon="flag")
                                    ).add_to(cluster_map)
                            
                            st.write("DBSCAN Clustering Results (for multi-vehicle routing)")
                            folium_static(cluster_map)
                            
                            # Show cluster metrics
                            st.write(f"Number of clusters: {len(clusters)}")
                            st.write("Each cluster can be assigned to a different delivery vehicle.")
                else:
                    if not success:
                        show_notification("Route optimization failed. Please check your addresses and try again.", "error")
                    else:
                        show_notification("Received empty response from optimization service.", "warning")
                        
    else:
        st.info("Enter addresses or upload a file to begin route optimization.")
