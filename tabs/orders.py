import streamlit as st
import pandas as pd
import datetime
from utils.api import get_data, post_data, put_data, delete_data
from utils.helpers import display_kpi_metrics, format_date, show_notification

def app():
    st.header("Orders Management")
    st.markdown("---")
    # Get orders data
    orders = get_data("orders")
    # Display KPIs
    if orders:
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        orders_today = sum(1 for order in orders if format_date(order.get('order_date', '')) == today)
        pending_orders = sum(1 for order in orders if order.get('status') == 'pending')
        delivered_count = sum(1 for order in orders if order.get('status') == 'delivered')
        col1, col2, col3 = st.columns(3)
        col1.metric("Orders Today", orders_today)
        col2.metric("Pending Orders", pending_orders)
        col3.metric("Delivered", delivered_count)
    # Filters in an expander
    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            min_date = datetime.datetime.today() - datetime.timedelta(days=30)
            max_date = datetime.datetime.today()
            date_filter_type = st.radio("Date Filter", ["All Dates", "Select Range"], horizontal=True)
            if date_filter_type == "Select Range":
                date_range = st.date_input(
                    "Order Date Range",
                    (min_date, max_date),
                    min_value=min_date - datetime.timedelta(days=365),
                    max_value=max_date
                )
            else:
                date_range = None
        with col2:
            status_filter = st.multiselect(
                "Status", 
                ["pending", "shipped", "cancelled", "delivered"], 
                default=["pending", "shipped"]
            )
    # Orders Table
    st.markdown("### All Orders")
    if orders:
        df = pd.DataFrame(orders)
        search = st.text_input("Search by Order ID or Customer Name", help="Type to filter orders by ID or customer name.")
        if not df.empty:
            # Defensive: check for 'order_date' column
            if 'order_date' in df.columns:
                df['order_date'] = pd.to_datetime(df['order_date'])
            else:
                st.warning("Some orders are missing the 'order_date' field. These will be skipped in date filtering.")
                df['order_date'] = pd.NaT
            # Only filter by date if not 'All Dates'
            if date_range is not None and 'date_range' in locals() and len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['order_date'].dt.date >= start_date) & (df['order_date'].dt.date <= end_date)]
            if status_filter:
                df = df[df['status'].isin(status_filter)]
            if search:
                df = df[df['order_id'].str.contains(search, case=False) | df['customer_name'].str.contains(search, case=False)]
            if not df.empty:
                df['order_date'] = df['order_date'].dt.strftime('%Y-%m-%d')
                df['Actions'] = None
                def highlight_status(row):
                    color = ''
                    if row['status'] == 'pending':
                        color = 'background-color: #fff3cd;'
                    elif row['status'] == 'cancelled':
                        color = 'background-color: #f8d7da;'
                    return [color] * len(row)
                st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)
            else:
                st.info("No orders match the selected filters.")
        else:
            st.info("No orders found in the system.")
    else:
        st.warning("Could not fetch orders data. Please check API connection.")
    # Actions
    st.markdown("### Actions")
    col1, col2 = st.columns(2)
    with col1:
        selected_order = st.selectbox("Select Order ID", df['order_id'].tolist() if orders else [], help="Choose an order to perform actions on.")
    with col2:
        action = st.selectbox("Action", ["Cancel Order", "Mark as Dispatched"], help="Select an action for the order.")
    if st.button("Apply Action"):
        if action == "Cancel Order":
            success = put_data(f"orders/{selected_order}", {"status": "cancelled"})
            if success:
                show_notification(f"Order #{selected_order} has been cancelled.", "success")
        elif action == "Mark as Dispatched":
            success = put_data(f"orders/{selected_order}", {"status": "shipped"})
            if success:
                show_notification(f"Order #{selected_order} has been dispatched.", "success")
    # Add new order form
    if st.session_state.get('show_add_order_form', False):
        st.markdown("---")
        st.subheader("Add New Order")
        with st.form("new_order_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = st.text_input("Customer Name", placeholder="Enter customer name", help="Full name of the customer.")
                product_id = st.text_input("Product ID", placeholder="Enter product ID", help="Product SKU or ID.")
            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1, help="Number of items in the order.")
                delivery_address = st.text_area("Delivery Address", placeholder="Enter delivery address", help="Full delivery address for the order.")
            submit_button = st.form_submit_button("Create Order")
            if submit_button:
                if customer_name and product_id and delivery_address:
                    new_order = {
                        "customer_name": customer_name,
                        "product_id": product_id,
                        "quantity": quantity,
                        "delivery_address": delivery_address,
                        "status": "pending",
                        "order_date": datetime.datetime.now().isoformat()
                    }
                    success, _ = post_data("orders", new_order)
                    if success:
                        show_notification("Order created successfully!", "success")
                        st.session_state.show_add_order_form = False
                        st.experimental_rerun()
                    else:
                        show_notification("Failed to create order.", "error")
                else:
                    show_notification("Please fill all required fields.", "warning")
