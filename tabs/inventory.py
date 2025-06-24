import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.api import get_data, post_data, put_data
from utils.helpers import display_kpi_metrics, plot_category_pie_chart, show_notification

def app():
    st.header("📚 Inventory Management")
    
    # Get inventory data
    inventory = get_data("inventory")
    
    # Display KPIs
    if inventory:
        low_stock_items = sum(1 for item in inventory if item.get('quantity', 0) < item.get('min_stock_level', 10))
        
        kpi_data = {
            'inventory_items': len(inventory),
            'low_stock': low_stock_items,
            'low_stock_delta': f"+{low_stock_items} alerts" if low_stock_items > 0 else "No alerts"
        }
        
        display_kpi_metrics(kpi_data)
    
    # Inventory Visualization
    if inventory:
        tab1, tab2 = st.tabs(["Inventory Table", "Category Distribution"])
        
        # Tab 1: Inventory Table
        with tab1:
            # Filters
            with st.expander("Filters", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    # SKU filter
                    sku_filter = st.text_input("Filter by SKU")
                
                with col2:
                    # Low stock filter
                    show_low_stock = st.checkbox("Show only low stock items")
            
            # Convert to DataFrame
            df = pd.DataFrame(inventory)
            
            # Apply filters
            if not df.empty:
                if sku_filter:
                    df = df[df['sku'].str.contains(sku_filter, case=False)]
                
                if show_low_stock:
                    df = df[df['quantity'] < df['min_stock_level']]
                
                if not df.empty:
                    # Display inventory table
                    st.dataframe(df)
                    
                    # Inventory actions
                    st.subheader("Inventory Actions")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        selected_sku = st.selectbox("Select SKU", df['sku'].tolist())
                    
                    with col2:
                        quantity_change = st.number_input("Quantity Change", value=0, step=1)
                    
                    if st.button("Update Stock"):
                        if quantity_change != 0:
                            # Get current quantity
                            current_item = next((item for item in inventory if item['sku'] == selected_sku), None)
                            
                            if current_item:
                                new_quantity = current_item['quantity'] + quantity_change
                                
                                if new_quantity >= 0:
                                    success, _ = put_data(f"inventory/{selected_sku}", {"quantity": new_quantity})
                                    
                                    if success:
                                        show_notification(f"Updated {selected_sku} stock to {new_quantity}", "success")
                                        st.experimental_rerun()
                                    else:
                                        show_notification("Failed to update inventory", "error")
                                else:
                                    show_notification("Quantity cannot be negative", "warning")
                else:
                    st.info("No inventory items match the selected filters.")
                    
        # Tab 2: Category Distribution
        with tab2:
            if not df.empty and 'category' in df.columns:
                fig = plot_category_pie_chart(df, "Inventory by Category")
                st.pyplot(fig)
            else:
                st.info("No category data available for visualization.")
    else:
        st.warning("Could not fetch inventory data. Please check API connection.")
    
    # Add New SKU Form
    with st.expander("Add New SKU"):
        with st.form("new_sku_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sku = st.text_input("SKU")
                name = st.text_input("Product Name")
                category = st.text_input("Category")
                
            with col2:
                quantity = st.number_input("Quantity", min_value=0, value=0)
                bin_location = st.text_input("Bin Location")
                min_stock = st.number_input("Minimum Stock Level", min_value=1, value=10)
            
            submit_button = st.form_submit_button("Add SKU")
            
            if submit_button:
                if sku and name and category and bin_location:
                    new_item = {
                        "sku": sku,
                        "name": name,
                        "category": category,
                        "quantity": quantity,
                        "bin_location": bin_location,
                        "min_stock_level": min_stock
                    }
                    
                    success, _ = post_data("inventory", new_item)
                    if success:
                        show_notification(f"Added new SKU: {sku}", "success")
                        st.experimental_rerun()
                    else:
                        show_notification("Failed to add new SKU", "error")
                else:
                    show_notification("Please fill all required fields", "warning")
