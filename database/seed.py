import random
from datetime import datetime, timedelta
from database.db import SessionLocal, init_db
from database.models import (
    User, Worker, Cooperative, ServiceCategory, DemandHistory,
    UserRole, VerificationStatus, Booking, BookingStatus, UrgencyLevel, PaymentStatus
)

def seed_data():
    init_db()
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(ServiceCategory).first():
        print("Database already seeded.")
        return
        
    print("Seeding database...")
    
    # 1. Services
    services = [
        ServiceCategory(name="Plumbing", base_price=300.0, description="Pipe repairs, leakages, fittings"),
        ServiceCategory(name="Electrical", base_price=250.0, description="Wiring, appliance installation, repairs"),
        ServiceCategory(name="Carpentry", base_price=400.0, description="Furniture repair, woodwork, doors"),
        ServiceCategory(name="Painting", base_price=500.0, description="Wall painting, exterior, interior"),
        ServiceCategory(name="Cleaning", base_price=200.0, description="Deep cleaning, regular cleaning"),
        ServiceCategory(name="Gardening", base_price=250.0, description="Lawn mowing, pruning, plant care"),
        ServiceCategory(name="Driver", base_price=400.0, description="Personal driver, commercial driving"),
        ServiceCategory(name="Caregiver", base_price=500.0, description="Elderly care, patient care"),
        ServiceCategory(name="Technician", base_price=350.0, description="AC repair, washing machine repair"),
        ServiceCategory(name="Domestic help", base_price=200.0, description="Cooking, daily chores")
    ]
    db.add_all(services)
    db.commit()

    # 2. Cooperatives
    coops = [
        Cooperative(name="North Delhi Labour Fed", location="North Delhi"),
        Cooperative(name="South Mumbai Society", location="South Mumbai"),
        Cooperative(name="East Bangalore Coop", location="East Bangalore")
    ]
    db.add_all(coops)
    db.commit()

    # 3. Users (Customers & Admins)
    admin_user = User(name="Admin Ravi", phone="9999999999", email="admin@sahaayak.in", role=UserRole.ADMIN.value)
    db.add(admin_user)
    
    customers = []
    for i in range(10):
        customers.append(User(
            name=f"Customer {i+1}", 
            phone=f"88888888{i:02d}", 
            role=UserRole.CUSTOMER.value,
            address=f"Location {i}, Central Zone",
            lat=28.6139 + random.uniform(-0.05, 0.05),
            lon=77.2090 + random.uniform(-0.05, 0.05)
        ))
    db.add_all(customers)
    db.commit()

    # Link admin to coops
    for coop in coops:
        coop.admin_id = admin_user.id
    db.commit()

    # 4. Workers
    names = ["Rajesh", "Amit", "Suresh", "Vikram", "Anil", "Sunil", "Ramesh", "Dinesh", "Manoj", "Karan", 
             "Priya", "Anita", "Sunita", "Geeta", "Seema", "Rekha", "Pooja", "Neha", "Kavita", "Meena",
             "Rahul", "Ravi", "Vijay", "Ajay", "Sanjay"]
    
    zones = ["North", "South", "East", "West", "Central"]
    
    for i in range(25):
        w_user = User(
            name=f"{random.choice(names)} {random.choice(['Sharma', 'Verma', 'Singh', 'Kumar', 'Das', 'Gupta'])}",
            phone=f"77777777{i:02d}",
            role=UserRole.WORKER.value
        )
        db.add(w_user)
        db.commit()
        
        skills_sample = random.sample(services, k=random.randint(1, 3))
        skill_names = ",".join([s.name for s in skills_sample])
        
        worker = Worker(
            user_id=w_user.id,
            cooperative_id=random.choice(coops).id,
            skills=skill_names,
            experience_years=random.randint(1, 15),
            certification_status=random.choice([True, False, True]), # Bias to true
            verification_status=random.choice([VerificationStatus.VERIFIED.value, VerificationStatus.VERIFIED.value, VerificationStatus.PENDING.value]),
            rating=round(random.uniform(3.5, 5.0), 1),
            rating_count=random.randint(0, 100),
            is_available=random.choice([True, True, False]),
            lat=28.6139 + random.uniform(-0.1, 0.1),
            lon=77.2090 + random.uniform(-0.1, 0.1),
            zone=random.choice(zones),
            has_insurance=random.choice([True, False]),
            has_accident_coverage=random.choice([True, False]),
            fair_wage_compliant=True
        )
        db.add(worker)
    db.commit()

    # 5. Demand History (Synthetic Data for AI Forecasting)
    # Generate past 30 days of demand data
    base_date = datetime.utcnow() - timedelta(days=30)
    history_entries = []
    
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        for zone in zones:
            for service in services:
                # Base request count + random noise + slight trend
                base_requests = random.randint(5, 20)
                
                # Make plumbing and electrical slightly more popular
                if service.name in ["Plumbing", "Electrical"]:
                    base_requests += random.randint(5, 15)
                    
                # Add day of week effect (more requests on weekends)
                if current_date.weekday() >= 5:
                    base_requests = int(base_requests * 1.5)
                    
                entry = DemandHistory(
                    date=current_date,
                    zone=zone,
                    service_category_id=service.id,
                    request_count=base_requests
                )
                history_entries.append(entry)
                
    db.add_all(history_entries)
    db.commit()
    
    # 6. Sample Bookings
    all_workers = db.query(Worker).all()
    all_customers = db.query(User).filter(User.role == UserRole.CUSTOMER.value).all()
    
    for _ in range(20):
        worker = random.choice(all_workers)
        customer = random.choice(all_customers)
        service = random.choice(services)
        
        status = random.choice([BookingStatus.COMPLETED.value, BookingStatus.PENDING.value, BookingStatus.ACCEPTED.value])
        
        booking = Booking(
            customer_id=customer.id,
            worker_id=worker.id if status != BookingStatus.PENDING.value else None,
            service_category_id=service.id,
            description="Sample booking request",
            address=customer.address,
            lat=customer.lat,
            lon=customer.lon,
            urgency=random.choice([UrgencyLevel.NORMAL.value, UrgencyLevel.EMERGENCY.value]),
            status=status,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            base_price=service.base_price,
            total_amount=service.base_price + 100,
            worker_earnings=service.base_price + 80,
            coop_fee=20,
            payment_status=PaymentStatus.PAID.value if status == BookingStatus.COMPLETED.value else PaymentStatus.PENDING.value
        )
        db.add(booking)
    
    db.commit()

    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()
