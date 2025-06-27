import streamlit as st
import pandas as pd
import datetime
import uuid
from utils.api import get_data, post_data, patch_data
from utils.helpers import display_kpi_metrics, format_date, show_notification

@st.cache_data(ttl=10)
def fetch_orders():
    return get_data("orders")

def app():
    """
    Renders the Orders Management page.
    """
    st.header("Orders Management")

    orders = fetch_orders()

    if orders is None:
        st.warning("Could not fetch orders. The backend might be down or you might not have access.")
        return

    df = pd.DataFrame(orders)

    # --- KPIs ---
    st.subheader("Key Metrics")
    if not df.empty:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        orders_today = sum(1 for order in orders if order.get('order_date', '').startswith(today))
        pending_orders = sum(1 for order in orders if order.get('status') == 'pending')
        delivered_count = sum(1 for order in orders if order.get('status') == 'delivered')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Orders Today", orders_today)
        col2.metric("⏳ Pending Orders", pending_orders)
        col3.metric("✅ Delivered", delivered_count)
    else:
        st.info("No orders found to display KPIs.")
    
    st.markdown("---")

    # --- Filters and Display ---
    st.subheader("All Orders")
    if not df.empty:
        filtered_df = df.copy()
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No orders found in the system.")

    st.markdown("---")

    # --- Actions ---
    st.subheader("Order Actions")
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_order_id = st.selectbox(
                "Select Order ID", 
                df['order_id'].tolist(),
                key="select_order_action"
            )
        with col2:
            action = st.selectbox(
                "Action", 
                ["Cancel Order", "Mark as Dispatched"],
                key="select_order_action_type"
            )
        
        if st.button("Apply Action", key="apply_order_action"):
            new_status = "cancelled" if action == "Cancel Order" else "shipped"
            success, error = patch_data(f"orders/{selected_order_id}", {"status": new_status})
            if success:
                st.success(f"Order #{selected_order_id} has been updated to '{new_status}'.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Failed to update order: {error}")
    else:
        st.info("No orders to perform actions on.")

    st.markdown("---")

    # --- Add New Order ---
    with st.expander("Add New Order"):
        with st.form("new_order_form", clear_on_submit=True):
            customer_name = st.text_input("Customer Name", key="order_customer_name")
            product_id = st.text_input("Product ID", key="order_product_id")
            quantity = st.number_input("Quantity", min_value=1, step=1, key="order_quantity")
            delivery_address = st.text_area("Delivery Address", key="order_delivery_address")
            
            submit_button = st.form_submit_button("Create Order")
            
            if submit_button:
                if all([customer_name, product_id, quantity, delivery_address]):
                    new_order = {
                        "order_id": f"ORD-{str(uuid.uuid4())[:8].upper()}",
                        "customer_name": customer_name,
                        "product_id": product_id,
                        "quantity": quantity,
                        "delivery_address": delivery_address,
                        "status": "pending",
                        "order_date": datetime.datetime.now().isoformat()
                    }
                    data, error = post_data("orders", new_order)
                    if data:
                        st.success("Order created successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to create order: {error}")
                else:
                    st.warning("Please fill out all fields.")
