import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import SessionLocal
from database.models import User, Worker, Booking, ServiceCategory, Cooperative, VerificationStatus, DemandHistory, BookingStatus
from services.forecasting import forecast_demand
from services.allocation import recommend_allocations

def render_page():
    db = SessionLocal()
    user_id = st.session_state['user_id']
    
    admin = db.query(User).filter(User.id == user_id).first()
    coop = db.query(Cooperative).filter(Cooperative.admin_id == admin.id).first()
    
    if not coop:
        st.error("No cooperative linked to this admin account.")
        return
        
    st.sidebar.title(f"Admin: {coop.name}")
    
    menu = ["Dashboard", "Workers", "Demand Forecast (AI)", "Workforce Allocation (AI)", "Bookings & Revenue"]
    choice = st.sidebar.radio("Navigation", menu)
    
    if choice == "Dashboard":
        st.header("Cooperative Dashboard")
        
        # Key Metrics
        total_workers = db.query(Worker).filter(Worker.cooperative_id == coop.id).count()
        verified_workers = db.query(Worker).filter(Worker.cooperative_id == coop.id, Worker.verification_status == VerificationStatus.VERIFIED.value).count()
        pending_workers = total_workers - verified_workers
        active_today = db.query(Worker).filter(Worker.cooperative_id == coop.id, Worker.is_available == True).count()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Workers", total_workers)
        col2.metric("Verified Workers", verified_workers)
        col3.metric("Pending Verification", pending_workers)
        col4.metric("Active Now", active_today)
        
        st.markdown("---")
        
        # Worker skill distribution chart
        st.subheader("Worker Skills Distribution")
        workers = db.query(Worker).filter(Worker.cooperative_id == coop.id).all()
        skill_counts = {}
        for w in workers:
            for s in w.skills.split(","):
                s = s.strip()
                skill_counts[s] = skill_counts.get(s, 0) + 1
                
        if skill_counts:
            df_skills = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"])
            fig = px.pie(df_skills, values="Count", names="Skill", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
    elif choice == "Workers":
        st.header("Manage Workers")
        
        workers = db.query(Worker).filter(Worker.cooperative_id == coop.id).all()
        
        if workers:
            df = pd.DataFrame([{
                "ID": w.id,
                "Name": w.user.name,
                "Skills": w.skills,
                "Rating": w.rating,
                "Status": w.verification_status,
                "Zone": w.zone
            } for w in workers])
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No workers in this cooperative yet.")
            
    elif choice == "Demand Forecast (AI)":
        st.header("AI Demand Forecasting")
        st.write("Using historical booking data to predict tomorrow's demand across zones.")
        
        with st.spinner("Generating forecast..."):
            forecast_df = forecast_demand(db, DemandHistory, ServiceCategory)
            
        if not forecast_df.empty:
            # Show overall trend
            st.subheader("Tomorrow's Forecast by Service")
            
            # Pivot table for better visualization
            pivot_df = forecast_df.pivot(index='Service', columns='Zone', values='Forecasted_Demand').fillna(0)
            st.dataframe(pivot_df, use_container_width=True)
            
            # Chart
            fig = px.bar(forecast_df, x='Service', y='Forecasted_Demand', color='Zone', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Service Trends")
            st.dataframe(forecast_df[['Zone', 'Service', 'Trend', 'Percent_Change']], use_container_width=True)
        else:
            st.info("Not enough historical data for forecasting.")
            
    elif choice == "Workforce Allocation (AI)":
        st.header("AI Workforce Allocation")
        st.write("Actionable recommendations based on predicted demand and current worker availability.")
        
        with st.spinner("Analyzing supply and demand..."):
            recommendations = recommend_allocations(db, DemandHistory, ServiceCategory)
            
        if recommendations:
            for rec in recommendations:
                with st.expander(f"{rec['Priority']} Priority: {rec['Service']} in {rec['Zone']}"):
                    if rec['Priority'] == 'High':
                        st.error(rec['Action'])
                    else:
                        st.warning(rec['Action'])
        else:
            st.success("Workforce is currently balanced across all zones. No immediate re-allocation needed.")
            
    elif choice == "Bookings & Revenue":
        st.header("Cooperative Revenue")
        
        bookings = db.query(Booking).join(Worker).filter(Worker.cooperative_id == coop.id).all()
        
        total_rev = sum(b.total_amount for b in bookings)
        worker_earnings = sum(b.worker_earnings for b in bookings)
        coop_revenue = sum(b.coop_fee for b in bookings)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Transaction Value", f"₹{total_rev}")
        col2.metric("Total Worker Earnings", f"₹{worker_earnings}")
        col3.metric("Cooperative Revenue", f"₹{coop_revenue}")
        
        st.subheader("Recent Bookings")
        if bookings:
            df = pd.DataFrame([{
                "Date": b.created_at.strftime("%Y-%m-%d"),
                "Customer": b.customer.name,
                "Worker": b.worker.user.name if b.worker else "-",
                "Service": b.service_category.name,
                "Amount": b.total_amount,
                "Status": b.status
            } for b in sorted(bookings, key=lambda x: x.created_at, reverse=True)[:20]])
            st.dataframe(df, use_container_width=True)
            
    db.close()
