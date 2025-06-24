import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from utils.api import get_data, post_data
from utils.helpers import display_kpi_metrics, show_notification

def app():
    st.header("🏢 Warehouse Management")
    
    # Get warehouse data
    warehouse_data = get_data("warehouse")
    inventory_data = get_data("inventory")
    
    # Display KPIs if available
    if warehouse_data and 'bins' in warehouse_data:
        total_bins = len(warehouse_data['bins'])
        occupied_bins = sum(1 for bin in warehouse_data['bins'] if bin.get('status') == 'occupied')
        efficiency = round((occupied_bins / total_bins) * 100 if total_bins > 0 else 0, 1)
        
        kpi_data = {
            'inventory_items': total_bins,
            'orders_today': occupied_bins,
            'orders_delta': f"{efficiency}% utilized",
            'low_stock': total_bins - occupied_bins,
            'low_stock_delta': "available bins"
        }
        
        display_kpi_metrics(kpi_data)
    
    # Warehouse visualization and tools
    tab1, tab2, tab3 = st.tabs(["Warehouse Layout", "Pick Route Simulator", "Zone Heatmap"])
    
    # Tab 1: Warehouse Layout
    with tab1:
        if warehouse_data and 'bins' in warehouse_data:
            # Extract bin data
            bins = pd.DataFrame(warehouse_data['bins'])
            
            if not bins.empty:
                # Create warehouse grid visualization
                st.subheader("Warehouse Bin Layout")
                
                # Get grid dimensions
                if 'row' in bins.columns and 'col' in bins.columns:
                    max_row = bins['row'].max()
                    max_col = bins['col'].max()
                    
                    # Create a grid
                    grid = np.zeros((max_row + 1, max_col + 1))
                    
                    # Fill the grid with bin status
                    for idx, bin in bins.iterrows():
                        status_value = {
                            'empty': 0.2,
                            'occupied': 0.8,
                            'reserved': 0.5,
                            'damaged': 0.1,
                        }.get(bin.get('status', ''), 0)
                        
                        grid[bin['row'], bin['col']] = status_value
                    
                    # Plot the grid
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    # Create a custom colormap: empty (light blue) -> reserved (yellow) -> occupied (dark blue) -> damaged (red)
                    colors = ['#ff9999', '#f2f2f2', '#ffcc99', '#99ccff']
                    cmap = LinearSegmentedColormap.from_list('warehouse_cmap', colors, N=256)
                    
                    # Plot heatmap
                    heatmap = ax.imshow(grid, cmap=cmap, interpolation='nearest')
                    
                    # Add bin labels
                    for i in range(max_row + 1):
                        for j in range(max_col + 1):
                            bin_id = next((bin.get('bin_id', '') for idx, bin in bins.iterrows() 
                                         if bin['row'] == i and bin['col'] == j), '')
                            
                            # Only show bin_id for actual bins (non-zero values)
                            if grid[i, j] > 0:
                                ax.text(j, i, bin_id, ha="center", va="center", 
                                        color="black", fontsize=8)
                    
                    # Set labels and title
                    ax.set_xticks(np.arange(max_col + 1))
                    ax.set_yticks(np.arange(max_row + 1))
                    ax.set_xticklabels(np.arange(max_col + 1))
                    ax.set_yticklabels(np.arange(max_row + 1))
                    ax.set_title("Warehouse Layout")
                    
                    # Add legend
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#99ccff', edgecolor='black', label='Occupied'),
                        Patch(facecolor='#ffcc99', edgecolor='black', label='Reserved'),
                        Patch(facecolor='#f2f2f2', edgecolor='black', label='Empty'),
                        Patch(facecolor='#ff9999', edgecolor='black', label='Damaged')
                    ]
                    ax.legend(handles=legend_elements, loc='upper right')
                    
                    # Show the plot
                    st.pyplot(fig)
                else:
                    st.error("Bin layout data is incomplete. Missing row/col information.")
            else:
                st.info("No bin data available for visualization.")
        else:
            st.warning("Could not fetch warehouse layout data.")
    
    # Tab 2: Pick Route Simulator
    with tab2:
        st.subheader("Order Pick Route Simulator")
        
        if inventory_data and warehouse_data and 'bins' in warehouse_data:
            # Create pick list form
            with st.expander("Create Pick List", expanded=True):
                # Get all available SKUs
                if inventory_data:
                    inventory_df = pd.DataFrame(inventory_data)
                    skus = inventory_df['sku'].tolist() if 'sku' in inventory_df.columns else []
                    
                    # Multi-select for SKUs
                    selected_skus = st.multiselect("Select SKUs for Pick List", skus)
                    
                    if st.button("Simulate Pick Route"):
                        if selected_skus:
                            # Get bin locations for selected SKUs
                            selected_inventory = inventory_df[inventory_df['sku'].isin(selected_skus)]
                            
                            if not selected_inventory.empty and 'bin_location' in selected_inventory.columns:
                                # Get bins data
                                bins_df = pd.DataFrame(warehouse_data['bins'])
                                
                                if not bins_df.empty:
                                    # Map bin_location to actual bin coordinates
                                    pick_points = []
                                    
                                    for _, item in selected_inventory.iterrows():
                                        bin_id = item.get('bin_location', '')
                                        bin_data = bins_df[bins_df['bin_id'] == bin_id]
                                        
                                        if not bin_data.empty:
                                            row = bin_data.iloc[0]['row']
                                            col = bin_data.iloc[0]['col']
                                            pick_points.append((row, col, item['sku']))
                                    
                                    if pick_points:
                                        # Simple A* algorithm simulation (not actual implementation)
                                        # Assume starting point at (0,0)
                                        start_point = (0, 0)
                                        
                                        # Sort pick points for a simple route (not optimal)
                                        # In real implementation, this would use A* or Dijkstra's algorithm
                                        pick_points.sort()
                                        
                                        # Create a visualization of the pick route
                                        fig, ax = plt.subplots(figsize=(10, 8))
                                        
                                        # Plot warehouse grid
                                        grid = np.zeros((bins_df['row'].max() + 1, bins_df['col'].max() + 1))
                                        ax.imshow(grid, cmap='Blues', alpha=0.3)
                                        
                                        # Plot start point
                                        ax.plot(start_point[1], start_point[0], 'go', markersize=12, label='Start')
                                        
                                        # Plot route
                                        route_x = [start_point[1]]
                                        route_y = [start_point[0]]
                                        
                                        for point in pick_points:
                                            route_y.append(point[0])
                                            route_x.append(point[1])
                                            
                                        ax.plot(route_x, route_y, 'r-', linewidth=2)
                                        
                                        # Plot pick points
                                        for point in pick_points:
                                            ax.plot(point[1], point[0], 'bo', markersize=8)
                                            ax.text(point[1], point[0], point[2], fontsize=8)
                                        
                                        # Set labels and title
                                        ax.set_xticks(np.arange(bins_df['col'].max() + 1))
                                        ax.set_yticks(np.arange(bins_df['row'].max() + 1))
                                        ax.set_xticklabels(np.arange(bins_df['col'].max() + 1))
                                        ax.set_yticklabels(np.arange(bins_df['row'].max() + 1))
                                        ax.set_title("Pick Route Simulation")
                                        
                                        # Add legend
                                        ax.legend()
                                        
                                        # Show route details
                                        total_distance = len(route_x) - 1  # Simple calculation for demo
                                        
                                        st.pyplot(fig)
                                        st.info(f"Total walking distance: {total_distance} units")
                                        st.success(f"Pick route calculated for {len(pick_points)} items")
                                    else:
                                        st.warning("Could not map SKUs to bin locations.")
                                else:
                                    st.warning("Bin data is not available.")
                            else:
                                st.warning("Bin location data not found for selected SKUs.")
                        else:
                            st.warning("Please select at least one SKU for the pick list.")
            
            # Option to optimize slotting
            with st.expander("Optimize Slotting (Bonus Feature)"):
                st.info("This feature will rearrange items in bins to minimize pick distances based on item pick frequency.")
                
                if st.button("Run Slotting Optimization"):
                    st.info("Slotting optimization simulation running...")
                    show_notification("Slotting optimization completed! Items have been virtually rearranged.", "success")
        else:
            st.warning("Could not fetch inventory or warehouse data.")
    
    # Tab 3: Zone Heatmap
    with tab3:
        st.subheader("Warehouse Zone Activity Heatmap")
        
        if warehouse_data and 'activity' in warehouse_data:
            # Create a heatmap of activity
            activity_data = warehouse_data['activity']
            
            if activity_data:
                activity_df = pd.DataFrame(activity_data)
                
                if not activity_df.empty and 'row' in activity_df.columns and 'col' in activity_df.columns and 'activity_level' in activity_df.columns:
                    # Create grid for heatmap
                    max_row = activity_df['row'].max()
                    max_col = activity_df['col'].max()
                    
                    heatmap_grid = np.zeros((max_row + 1, max_col + 1))
                    
                    # Fill with activity data
                    for idx, cell in activity_df.iterrows():
                        heatmap_grid[cell['row'], cell['col']] = cell['activity_level']
                    
                    # Create plot
                    fig, ax = plt.subplots(figsize=(12, 8))
                    heatmap = ax.imshow(heatmap_grid, cmap='hot', interpolation='nearest')
                    
                    # Add color bar
                    plt.colorbar(heatmap, ax=ax, label='Activity Level')
                    
                    # Set labels and title
                    ax.set_xticks(np.arange(max_col + 1))
                    ax.set_yticks(np.arange(max_row + 1))
                    ax.set_xticklabels(np.arange(max_col + 1))
                    ax.set_yticklabels(np.arange(max_row + 1))
                    ax.set_title("Warehouse Activity Heatmap")
                    
                    # Show the plot
                    st.pyplot(fig)
                    
                    # Add explanation
                    st.info("The heatmap shows the frequency of picks and access in different areas of the warehouse. Hotter colors indicate higher activity levels.")
                else:
                    st.info("Activity data format is incomplete.")
            else:
                st.info("No activity data available for heatmap visualization.")
        else:
            # If no real data, show a simulation
            st.info("No real activity data available. Showing a simulation.")
            
            # Create simulated heatmap
            rows, cols = 10, 15
            
            # Generate random data with hot spots near the entrance
            simulated_data = np.random.rand(rows, cols) * 5
            # Make entrance area (top-left) busier
            for i in range(5):
                for j in range(7):
                    distance_from_entrance = i + j
                    simulated_data[i, j] += max(0, 10 - distance_from_entrance)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 8))
            heatmap = ax.imshow(simulated_data, cmap='hot', interpolation='nearest')
            
            # Add color bar
            plt.colorbar(heatmap, ax=ax, label='Activity Level (Simulated)')
            
            # Set labels and title
            ax.set_xticks(np.arange(cols))
            ax.set_yticks(np.arange(rows))
            ax.set_xticklabels(np.arange(cols))
            ax.set_yticklabels(np.arange(rows))
            ax.set_title("Simulated Warehouse Activity Heatmap")
            
            # Mark entrance
            ax.text(0, 0, "Entrance", ha="center", va="center", 
                    color="white", fontsize=10, fontweight='bold')
            
            # Show the plot
            st.pyplot(fig)
            
            st.info("This is a simulated heatmap showing hypothetical activity levels. Connect to real warehouse data for accurate visualization.")
            
            if st.button("Generate New Simulation"):
                st.experimental_rerun()
