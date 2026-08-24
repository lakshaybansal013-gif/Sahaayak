from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    CUSTOMER = "Customer"
    WORKER = "Worker"
    ADMIN = "Admin"

class UrgencyLevel(enum.Enum):
    NORMAL = "Normal"
    EMERGENCY = "Emergency"

class BookingStatus(enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    STARTED = "Started"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"

class VerificationStatus(enum.Enum):
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(String(20), default=UserRole.CUSTOMER.value)
    
    # Customer specific
    address = Column(String(255), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    bookings = relationship("Booking", back_populates="customer", foreign_keys='Booking.customer_id')

class Cooperative(Base):
    __tablename__ = 'cooperatives'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    workers = relationship("Worker", back_populates="cooperative")

class Worker(Base):
    __tablename__ = 'workers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    cooperative_id = Column(Integer, ForeignKey('cooperatives.id'), nullable=True)
    
    skills = Column(String(255), nullable=False) # Comma separated for simplicity in prototype
    experience_years = Column(Integer, default=0)
    certification_status = Column(Boolean, default=False)
    verification_status = Column(String(20), default=VerificationStatus.PENDING.value)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    is_available = Column(Boolean, default=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    zone = Column(String(100), nullable=True)
    
    # Welfare
    has_insurance = Column(Boolean, default=False)
    has_accident_coverage = Column(Boolean, default=False)
    fair_wage_compliant = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    cooperative = relationship("Cooperative", back_populates="workers")
    bookings = relationship("Booking", back_populates="worker", foreign_keys='Booking.worker_id')
    
class ServiceCategory(Base):
    __tablename__ = 'service_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    base_price = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=True)
    service_category_id = Column(Integer, ForeignKey('service_categories.id'), nullable=False)
    
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=False)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    
    urgency = Column(String(20), default=UrgencyLevel.NORMAL.value)
    status = Column(String(20), default=BookingStatus.PENDING.value)
    
    scheduled_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Pricing fields
    base_price = Column(Float, default=0.0)
    travel_allowance = Column(Float, default=0.0)
    skill_adjustment = Column(Float, default=0.0)
    emergency_premium = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    worker_earnings = Column(Float, default=0.0)
    coop_fee = Column(Float, default=0.0)
    
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("User", foreign_keys=[customer_id], back_populates="bookings")
    worker = relationship("Worker", foreign_keys=[worker_id], back_populates="bookings")
    service_category = relationship("ServiceCategory")
    invoice = relationship("Invoice", back_populates="booking", uselist=False)
    rating = relationship("Rating", back_populates="booking", uselist=False)

class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True)
    issued_at = Column(DateTime, default=datetime.utcnow)
    
    booking = relationship("Booking", back_populates="invoice")

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    score = Column(Integer, nullable=False) # 1 to 5
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    booking = relationship("Booking", back_populates="rating")

class DemandHistory(Base):
    __tablename__ = 'demand_history'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    zone = Column(String(100), nullable=False)
    service_category_id = Column(Integer, ForeignKey('service_categories.id'), nullable=False)
    request_count = Column(Integer, default=0)
    
    service_category = relationship("ServiceCategory")
