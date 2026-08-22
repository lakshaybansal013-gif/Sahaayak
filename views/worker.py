import streamlit as st
from database.db import SessionLocal
from database.models import Worker, Booking, BookingStatus, PaymentStatus, User
from utils.translations import t
from utils.helpers import badge
import pandas as pd
from datetime import datetime

def render_page():
    db = SessionLocal()
    user_id = st.session_state['user_id']
    lang = st.session_state['lang']
    worker = db.query(Worker).filter(Worker.user_id == user_id).first()
    
    if not worker:
        st.error("Worker profile not found.")
        return
        
    st.sidebar.title(f"{t('welcome', lang)}, {worker.user.name}")
    
    # Toggle availability
    is_avail = st.sidebar.toggle("Available for Jobs", value=worker.is_available)
    if is_avail != worker.is_available:
        worker.is_available = is_avail
        db.commit()
    
    menu = ["Dashboard", "Job Requests", "My Earnings", "Welfare"]
    choice = st.sidebar.radio("Navigation", menu)
    
    if choice == "Dashboard":
        st.header("Worker Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rating", f"{worker.rating:.1f}★")
        
        today = datetime.utcnow().date()
        today_jobs = db.query(Booking).filter(
            Booking.worker_id == worker.id,
            Booking.status == BookingStatus.COMPLETED.value
            # Ideally filter by date here
        ).count()
        col2.metric("Completed Jobs", today_jobs)
        
        pending_reqs = db.query(Booking).filter(
            Booking.worker_id == worker.id,
            Booking.status == BookingStatus.PENDING.value
        ).count()
        col3.metric("Pending Requests", pending_reqs)
        
        status_color = "green" if worker.verification_status == "Verified" else "orange"
        col4.markdown(f"**Status:** {badge(worker.verification_status, status_color)}", unsafe_allow_html=True)
        
        st.subheader("My Skills")
        for s in worker.skills.split(","):
            st.write(f"- {s.strip()}")
            
    elif choice == "Job Requests":
        st.header("Job Requests")
        
        requests = db.query(Booking).filter(
            Booking.worker_id == worker.id,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.ACCEPTED.value, BookingStatus.STARTED.value])
        ).order_by(Booking.created_at.desc()).all()
        
        if not requests:
            st.info("No active job requests.")
            
        for r in requests:
            with st.container():
                st.markdown("---")
                if r.urgency == "Emergency":
                    st.error("🚨 EMERGENCY JOB")
                    
                st.subheader(f"{r.service_category.name} - {r.customer.name}")
                st.write(f"**Address:** {r.address}")
                st.write(f"**Distance:** (Estimated based on matching)")
                st.write(f"**Estimated Earnings:** ₹{r.worker_earnings}")
                st.write(f"**Status:** {badge(r.status)}", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                if r.status == BookingStatus.PENDING.value:
                    if col1.button("Accept", key=f"acc_{r.id}", type="primary"):
                        r.status = BookingStatus.ACCEPTED.value
                        db.commit()
                        st.rerun()
                    if col2.button("Reject", key=f"rej_{r.id}"):
                        r.status = BookingStatus.REJECTED.value
                        # Optionally unset worker_id so someone else can take it
                        r.worker_id = None
                        db.commit()
                        st.rerun()
                        
                elif r.status == BookingStatus.ACCEPTED.value:
                    if st.button("Mark as Started", key=f"start_{r.id}"):
                        r.status = BookingStatus.STARTED.value
                        db.commit()
                        st.rerun()
                        
                elif r.status == BookingStatus.STARTED.value:
                    if st.button("Mark as Completed", key=f"comp_{r.id}", type="primary"):
                        r.status = BookingStatus.COMPLETED.value
                        r.completed_at = datetime.utcnow()
                        db.commit()
                        st.rerun()
                        
    elif choice == "My Earnings":
        st.header("My Earnings")
        
        completed = db.query(Booking).filter(
            Booking.worker_id == worker.id,
            Booking.status == BookingStatus.COMPLETED.value
        ).all()
        
        total_earned = sum(b.worker_earnings for b in completed)
        paid_out = sum(b.worker_earnings for b in completed if b.payment_status == PaymentStatus.PAID.value)
        pending = total_earned - paid_out
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Earned", f"₹{total_earned}")
        col2.metric("Paid Out", f"₹{paid_out}")
        col3.metric("Pending Payout", f"₹{pending}")
        
        if completed:
            df = pd.DataFrame([{
                "Date": b.completed_at.strftime("%Y-%m-%d") if b.completed_at else "",
                "Service": b.service_category.name,
                "Earnings": b.worker_earnings,
                "Status": b.payment_status
            } for b in completed])
            st.dataframe(df, use_container_width=True)
            
    elif choice == "Welfare":
        st.header("Worker Welfare Status")
        st.write("Sahaayak ensures fair work and social security for all cooperative members.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Insurance & Health")
            st.write(f"Health Insurance: {'✅ Active' if worker.has_insurance else '❌ Not Active'}")
            st.write(f"Accident Coverage: {'✅ Active' if worker.has_accident_coverage else '❌ Not Active'}")
            
        with col2:
            st.subheader("Compliance & Training")
            st.write(f"Fair Wage Compliant: {'✅ Yes' if worker.fair_wage_compliant else '❌ No'}")
            st.write(f"Certifications: {'✅ Certified' if worker.certification_status else '❌ Pending'}")
            
        st.info("Your cooperative federation is managing your welfare benefits. Contact Admin for updates.")
        
    db.close()
