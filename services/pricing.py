from database.models import UrgencyLevel

def calculate_price(service_base_price, distance_km, worker_experience_years, urgency_level):
    """
    Final price = 
    Base service price
    + Travel allowance (₹10 per km)
    + Skill/experience adjustment (₹10 per year)
    + Emergency premium (₹100 for urgent, ₹250 for emergency)
    """
    
    travel_allowance = distance_km * 10
    skill_adjustment = worker_experience_years * 10
    
    emergency_premium = 0
    if urgency_level == UrgencyLevel.URGENT.value:
        emergency_premium = 100
    elif urgency_level == UrgencyLevel.EMERGENCY.value:
        emergency_premium = 250
        
    total_amount = service_base_price + travel_allowance + skill_adjustment + emergency_premium
    
    # Cooperative fee (e.g. 5% of base price)
    coop_fee = service_base_price * 0.05
    worker_earnings = total_amount - coop_fee
    
    return {
        "base_price": service_base_price,
        "travel_allowance": travel_allowance,
        "skill_adjustment": skill_adjustment,
        "emergency_premium": emergency_premium,
        "coop_fee": coop_fee,
        "worker_earnings": worker_earnings,
        "total_amount": total_amount
    }
