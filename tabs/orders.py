import streamlit as st
import pandas as pd
import datetime
from utils.api import get_data, post_data, put_data, delete_data
from utils.helpers import display_kpi_metrics, format_date, show_notification

def app():
    st.header("📦 Orders Management")
    
    # Get orders data
    orders = get_data("orders")
    
    # Display KPIs
    if orders:
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        orders_today = sum(1 for order in orders if format_date(order.get('order_date', '')) == today)
        pending_orders = sum(1 for order in orders if order.get('status') == 'pending')
        
        kpi_data = {
            'orders_today': orders_today,
            'orders_delta': f"+{orders_today} today",
            'deliveries_pending': pending_orders
        }
        
        display_kpi_metrics(kpi_data)
    
    # Filters
    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        
        # Date filter
        with col1:
            min_date = datetime.datetime.today() - datetime.timedelta(days=30)
            max_date = datetime.datetime.today()
            date_range = st.date_input(
                "Order Date Range",
                (min_date, max_date),
                min_value=min_date - datetime.timedelta(days=365),
                max_value=max_date
            )
        
        # Status filter
        with col2:
            status_filter = st.multiselect(
                "Status", 
                ["pending", "shipped", "cancelled"], 
                default=["pending", "shipped"]
            )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh"):
            orders = get_data("orders")
            st.experimental_rerun()
    
    with col3:
        if st.button("➕ Add New Order"):
            st.session_state.show_add_order_form = True
    
    # Orders table
    if orders:
        df = pd.DataFrame(orders)
        
        # Apply filters if there's data
        if not df.empty:
            # Convert date string to datetime for filtering
            df['order_date'] = pd.to_datetime(df['order_date'])
            
            # Apply date filter if it exists
            if 'date_range' in locals() and len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['order_date'].dt.date >= start_date) & 
                        (df['order_date'].dt.date <= end_date)]
            
            # Apply status filter
            if status_filter:
                df = df[df['status'].isin(status_filter)]
            
            if not df.empty:
                # Format date for display
                df['order_date'] = df['order_date'].dt.strftime('%Y-%m-%d')
                
                # Add action buttons column
                df['Actions'] = None
                
                # Display the table
                st.dataframe(df)
                
                # Order actions
                st.subheader("Order Actions")
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_order = st.selectbox("Select Order ID", df['order_id'].tolist())
                
                with col2:
                    action = st.selectbox("Action", ["Cancel Order", "Mark as Dispatched"])
                    
                if st.button("Apply Action"):
                    if action == "Cancel Order":
                        success = put_data(f"orders/{selected_order}", {"status": "cancelled"})
                        if success:
                            show_notification(f"Order #{selected_order} has been cancelled.", "success")
                    elif action == "Mark as Dispatched":
                        success = put_data(f"orders/{selected_order}", {"status": "shipped"})
                        if success:
                            show_notification(f"Order #{selected_order} has been dispatched.", "success")
            else:
                st.info("No orders match the selected filters.")
        else:
            st.info("No orders found in the system.")
    else:
        st.warning("Could not fetch orders data. Please check API connection.")
    
    # Add new order form
    if st.session_state.get('show_add_order_form', False):
        st.subheader("Add New Order")
        
        with st.form("new_order_form"):
            customer_name = st.text_input("Customer Name")
            product_id = st.text_input("Product ID")
            quantity = st.number_input("Quantity", min_value=1, value=1)
            delivery_address = st.text_area("Delivery Address")
            
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
