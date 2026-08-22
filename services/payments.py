import uuid
from datetime import datetime
from database.models import Invoice, PaymentStatus, BookingStatus

def process_demo_payment(db_session, booking):
    """
    Simulates a payment process for the demo.
    Generates an invoice and updates statuses.
    """
    if booking.payment_status == PaymentStatus.PAID.value:
        return True, "Already paid."
        
    try:
        # Create Invoice
        inv = Invoice(
            booking_id=booking.id,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            issued_at=datetime.utcnow()
        )
        db_session.add(inv)
        
        # Update Booking status
        booking.payment_status = PaymentStatus.PAID.value
        if booking.status != BookingStatus.COMPLETED.value:
            booking.status = BookingStatus.COMPLETED.value
            booking.completed_at = datetime.utcnow()
            
        # Here we would normally update worker earnings record if we had a separate table
        # Since we use booking.worker_earnings, it's implicitly updated.
        
        db_session.commit()
        return True, "Payment successful (Demo)."
    except Exception as e:
        db_session.rollback()
        return False, str(e)
