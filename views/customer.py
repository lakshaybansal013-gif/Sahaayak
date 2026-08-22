import streamlit as st
from database.db import SessionLocal
from database.models import User, ServiceCategory, Worker, Booking, BookingStatus, UrgencyLevel, PaymentStatus, Rating, Invoice
from services.matching import find_best_workers
from services.pricing import calculate_price
from services.payments import process_demo_payment
from utils.translations import t
from utils.helpers import badge
from datetime import datetime

def render_page():
    db = SessionLocal()
    user_id = st.session_state['user_id']
    lang = st.session_state['lang']
    customer = db.query(User).filter(User.id == user_id).first()
    
    st.sidebar.title(f"{t('welcome', lang)}, {customer.name}")
    
    menu = ["Home", "My Bookings", "Emergency"]
    choice = st.sidebar.radio("Navigation", menu)
    
    if choice == "Home":
        st.header(t("search_services", lang))
        services = db.query(ServiceCategory).all()
        service_names = [s.name for s in services]
        
        selected_service = st.selectbox("Select Service", [""] + service_names)
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Your Latitude", value=customer.lat or 28.6139, format="%.4f")
        with col2:
            lon = st.number_input("Your Longitude", value=customer.lon or 77.2090, format="%.4f")
            
        address = st.text_input("Address", value=customer.address or "")
        urgency = st.selectbox("Urgency", [u.value for u in UrgencyLevel])
        
        if selected_service and st.button("Find Workers"):
            st.session_state['search_results'] = {
                'service': selected_service,
                'lat': lat,
                'lon': lon,
                'address': address,
                'urgency': urgency
            }
            
        if 'search_results' in st.session_state:
            s_res = st.session_state['search_results']
            st.subheader("Recommended Workers")
            
            all_workers = db.query(Worker).all()
            best_workers = find_best_workers(all_workers, s_res['service'], s_res['lat'], s_res['lon'])
            
            if not best_workers:
                st.warning("No workers found for this service near your location.")
            else:
                service_obj = db.query(ServiceCategory).filter(ServiceCategory.name == s_res['service']).first()
                for w_data in best_workers:
                    worker = w_data['worker']
                    score = w_data['score']
                    dist = w_data['distance']
                    reasons = w_data['reasons']
                    
                    price_calc = calculate_price(
                        service_base_price=service_obj.base_price,
                        distance_km=dist,
                        worker_experience_years=worker.experience_years,
                        urgency_level=s_res['urgency']
                    )
                    
                    with st.expander(f"{worker.user.name} - {score}% Match ({dist} km)"):
                        st.write(f"**Skills:** {worker.skills}")
                        st.write(f"**Rating:** {worker.rating}★ ({worker.rating_count} reviews)")
                        if worker.certification_status:
                            st.write(badge("Certified", "green"), unsafe_allow_html=True)
                        if worker.verification_status == "Verified":
                            st.write(badge("Verified", "blue"), unsafe_allow_html=True)
                            
                        st.write(f"**Match Reasons:** {', '.join(reasons)}")
                        st.write(f"**Estimated Price:** ₹{price_calc['total_amount']}")
                        
                        if st.button(f"Book {worker.user.name}", key=f"book_{worker.id}"):
                            new_booking = Booking(
                                customer_id=customer.id,
                                worker_id=worker.id,
                                service_category_id=service_obj.id,
                                address=s_res['address'],
                                lat=s_res['lat'],
                                lon=s_res['lon'],
                                urgency=s_res['urgency'],
                                base_price=price_calc['base_price'],
                                travel_allowance=price_calc['travel_allowance'],
                                skill_adjustment=price_calc['skill_adjustment'],
                                emergency_premium=price_calc['emergency_premium'],
                                total_amount=price_calc['total_amount'],
                                worker_earnings=price_calc['worker_earnings'],
                                coop_fee=price_calc['coop_fee'],
                                status=BookingStatus.PENDING.value
                            )
                            db.add(new_booking)
                            db.commit()
                            st.success(f"Successfully requested {worker.user.name}!")
                            del st.session_state['search_results']
                            st.rerun()

    elif choice == "My Bookings":
        st.header(t("my_bookings", lang))
        bookings = db.query(Booking).filter(Booking.customer_id == customer.id).order_by(Booking.created_at.desc()).all()
        
        if not bookings:
            st.info("You have no bookings yet.")
            
        for b in bookings:
            with st.card(key=f"card_{b.id}") if hasattr(st, "card") else st.container():
                st.markdown("---")
                w_name = b.worker.user.name if b.worker else "Pending Assignment"
                st.subheader(f"{b.service_category.name} - {w_name}")
                st.write(f"**Status:** {badge(b.status)}", unsafe_allow_html=True)
                st.write(f"**Date:** {b.created_at.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Total Amount:** ₹{b.total_amount}")
                
                if b.status == BookingStatus.ACCEPTED.value:
                    st.info("Worker is on the way/working.")
                    
                if b.status == BookingStatus.COMPLETED.value and b.payment_status == PaymentStatus.PENDING.value:
                    if st.button("Pay Now (Demo)", key=f"pay_{b.id}"):
                        success, msg = process_demo_payment(db, b)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                            
                if b.payment_status == PaymentStatus.PAID.value:
                    st.write(badge("PAID", "green"), unsafe_allow_html=True)
                    inv = db.query(Invoice).filter(Invoice.booking_id == b.id).first()
                    if inv:
                        st.caption(f"Invoice: {inv.invoice_number}")
                        
                    # Rating logic
                    existing_rating = db.query(Rating).filter(Rating.booking_id == b.id).first()
                    if not existing_rating:
                        with st.form(key=f"rating_{b.id}"):
                            score = st.slider("Rate Worker (1-5)", 1, 5, 5)
                            feedback = st.text_area("Feedback")
                            if st.form_submit_button("Submit Rating"):
                                new_rating = Rating(booking_id=b.id, score=score, feedback=feedback)
                                db.add(new_rating)
                                
                                # Update worker rating
                                if b.worker:
                                    w = b.worker
                                    total_score = (w.rating * w.rating_count) + score
                                    w.rating_count += 1
                                    w.rating = total_score / w.rating_count
                                    
                                db.commit()
                                st.success("Thank you for your feedback!")
                                st.rerun()
                    else:
                        st.write(f"**Your Rating:** {existing_rating.score}★")
                        
    elif choice == "Emergency":
        st.header(t("emergency", lang))
        st.error("🚨 THIS WILL REQUEST IMMEDIATE ASSISTANCE WITH EMERGENCY PREMIUM 🚨")
        
        services = db.query(ServiceCategory).all()
        service_names = [s.name for s in services]
        
        em_service = st.selectbox("Emergency Service Required", [""] + service_names, key="em_serv")
        em_lat = st.number_input("Your Latitude", value=customer.lat or 28.6139, format="%.4f", key="em_lat")
        em_lon = st.number_input("Your Longitude", value=customer.lon or 77.2090, format="%.4f", key="em_lon")
        em_address = st.text_input("Address", value=customer.address or "", key="em_add")
        
        if em_service and st.button("🚨 FIND FASTEST WORKER 🚨"):
            all_workers = db.query(Worker).all()
            # In emergency, distance and availability are heavily weighted
            best_workers = find_best_workers(all_workers, em_service, em_lat, em_lon, limit=3)
            
            if best_workers:
                worker_data = best_workers[0] # Just pick the best one for 1-click
                worker = worker_data['worker']
                service_obj = db.query(ServiceCategory).filter(ServiceCategory.name == em_service).first()
                
                price_calc = calculate_price(
                    service_base_price=service_obj.base_price,
                    distance_km=worker_data['distance'],
                    worker_experience_years=worker.experience_years,
                    urgency_level=UrgencyLevel.EMERGENCY.value
                )
                
                new_booking = Booking(
                    customer_id=customer.id,
                    worker_id=worker.id,
                    service_category_id=service_obj.id,
                    address=em_address,
                    lat=em_lat,
                    lon=em_lon,
                    urgency=UrgencyLevel.EMERGENCY.value,
                    base_price=price_calc['base_price'],
                    travel_allowance=price_calc['travel_allowance'],
                    skill_adjustment=price_calc['skill_adjustment'],
                    emergency_premium=price_calc['emergency_premium'],
                    total_amount=price_calc['total_amount'],
                    worker_earnings=price_calc['worker_earnings'],
                    coop_fee=price_calc['coop_fee'],
                    status=BookingStatus.PENDING.value
                )
                db.add(new_booking)
                db.commit()
                st.success(f"🚨 EMERGENCY REQUEST SENT TO {worker.user.name.upper()} (Distance: {worker_data['distance']} km)")
            else:
                st.error("No workers available for emergency in your area.")
                
    db.close()
