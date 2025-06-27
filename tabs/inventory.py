import streamlit as st
import pandas as pd
from utils.api import get_data, post_data, patch_data
import matplotlib.pyplot as plt

@st.cache_data(ttl=10)
def fetch_inventory():
    return get_data("inventory")

def app():
    """
    Renders the Inventory Management page.
    """
    st.header("Inventory Management")

    inventory = fetch_inventory()

    if inventory is None:
        st.warning("Could not fetch inventory. The backend might be down or you might not have access.")
        return

    df = pd.DataFrame(inventory)

    # --- KPIs ---
    st.subheader("Key Metrics")
    if not df.empty:
        low_stock_items = df[df['quantity'] < df['min_stock_level']].shape[0]
        col1, col2 = st.columns(2)
        col1.metric("Total Inventory Items", len(df))
        col2.metric("Low Stock Alerts", low_stock_items)
    else:
        st.info("No inventory data to display KPIs.")

    st.markdown("---")

    # --- Data Display and Filtering ---
    tab1, tab2 = st.tabs(["Inventory Table", "Category Distribution"])
    
    with tab1:
        st.subheader("Inventory Details")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No inventory items found.")

    with tab2:
        st.subheader("Inventory by Category")
        if not df.empty and 'category' in df.columns:
            category_counts = df['category'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("No category data available for visualization.")

    st.markdown("---")

    # --- Actions ---
    st.subheader("Inventory Actions")
    if not df.empty:
        selected_sku = st.selectbox(
            "Select SKU to update stock", 
            df['sku'].tolist(), 
            key="inventory_sku_select"
        )
        
        quantity_change = st.number_input(
            "Enter quantity to add (use negative to subtract)", 
            step=1, 
            key="inventory_quantity_change"
        )

        if st.button("Update Stock", key="update_stock_button"):
            if quantity_change != 0:
                current_item = df[df['sku'] == selected_sku].iloc[0]
                new_quantity = int(current_item['quantity']) + quantity_change
                if new_quantity >= 0:
                    success, error = patch_data(f"inventory/{selected_sku}", {"quantity": new_quantity})
                    if success:
                        st.success(f"Updated {selected_sku} stock to {new_quantity}.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to update inventory: {error}")
                else:
                    st.warning("Quantity cannot be negative.")
    else:
        st.info("No inventory items to perform actions on.")

    st.markdown("---")

    # --- Add New SKU ---
    with st.expander("Add New SKU"):
        with st.form("new_sku_form", clear_on_submit=True):
            sku = st.text_input("SKU", key="sku_input")
            name = st.text_input("Product Name", key="name_input")
            category = st.text_input("Category", key="category_input")
            quantity = st.number_input("Initial Quantity", min_value=0, step=1, key="quantity_input")
            bin_location = st.text_input("Bin Location", key="bin_location_input")
            min_stock_level = st.number_input("Minimum Stock Level", min_value=1, step=1, key="min_stock_input")

            submit_button = st.form_submit_button("Add SKU")

            if submit_button:
                if all([sku, name, category, bin_location]):
                    new_item = {
                        "sku": sku, "name": name, "category": category,
                        "quantity": quantity, "bin_location": bin_location,
                        "min_stock_level": min_stock_level
                    }
                    data, error = post_data("inventory", new_item)
                    if data:
                        st.success(f"Added new SKU: {sku}")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to add new SKU: {error}")
                else:
                    st.warning("Please fill out all required fields.")
