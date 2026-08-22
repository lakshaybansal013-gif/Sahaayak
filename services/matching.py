from utils.geo import haversine_distance

def calculate_match_score(worker, required_service_name, customer_lat, customer_lon):
    """
    Match Score = 
    40% Skill Match
    + 25% Distance
    + 20% Availability
    + 10% Rating
    + 5% Certification
    """
    score = 0.0
    reasons = []
    
    # 1. Skill Match (40 points)
    worker_skills = [s.strip() for s in worker.skills.split(",")]
    if required_service_name in worker_skills:
        score += 40
        reasons.append("Exact skill match")
    else:
        # If no skill match, score is extremely low, maybe filter out before scoring.
        reasons.append("Skill mismatch")
        
    # 2. Distance (25 points)
    distance = haversine_distance(customer_lat, customer_lon, worker.lat, worker.lon)
    # Assume 0km = 25 pts, >20km = 0 pts
    if distance < 20:
        dist_score = max(0, 25 - (distance * (25/20)))
        score += dist_score
        reasons.append(f"{distance:.1f} km away")
    else:
        reasons.append(f"Far away ({distance:.1f} km)")
        
    # 3. Availability (20 points)
    if worker.is_available:
        score += 20
        reasons.append("Currently available")
    else:
        reasons.append("Currently busy")
        
    # 4. Rating (10 points)
    # 5 stars = 10 pts, 0 stars = 0 pts
    rating_score = (worker.rating / 5.0) * 10
    score += rating_score
    reasons.append(f"{worker.rating}★ rating")
    
    # 5. Certification (5 points)
    if worker.certification_status:
        score += 5
        reasons.append("Certified")
        
    return {
        "worker": worker,
        "score": round(score, 1),
        "distance": round(distance, 1),
        "reasons": reasons
    }

def find_best_workers(workers, required_service_name, customer_lat, customer_lon, limit=5):
    # Filter by skill first to avoid recommending entirely wrong workers
    eligible_workers = [w for w in workers if required_service_name in [s.strip() for s in w.skills.split(",")]]
    
    scored_workers = [
        calculate_match_score(w, required_service_name, customer_lat, customer_lon) 
        for w in eligible_workers
    ]
    
    # Sort by score descending
    scored_workers.sort(key=lambda x: x["score"], reverse=True)
    return scored_workers[:limit]
