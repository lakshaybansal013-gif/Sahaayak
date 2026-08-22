import pandas as pd
from database.models import Worker
from .forecasting import forecast_demand

def recommend_allocations(db_session, DemandHistory, ServiceCategory):
    """
    Compare forecasted demand with current worker availability.
    Generate actionable recommendations.
    """
    forecast_df = forecast_demand(db_session, DemandHistory, ServiceCategory)
    if forecast_df.empty:
        return []
        
    # Get current available workers by zone and skill
    workers = db_session.query(Worker).filter(Worker.is_available == True).all()
    
    # We need to map workers to zones and services
    # A worker can have multiple skills
    supply = {}
    for w in workers:
        if not w.zone: continue
        skills = [s.strip() for s in w.skills.split(',')]
        for s in skills:
            key = (w.zone, s)
            supply[key] = supply.get(key, 0) + 1
            
    recommendations = []
    
    for _, row in forecast_df.iterrows():
        zone = row['Zone']
        service = row['Service']
        predicted_demand = row['Forecasted_Demand']
        
        # Current supply
        current_supply = supply.get((zone, service), 0)
        
        # If demand is significantly higher than supply
        if predicted_demand > current_supply * 1.5 and predicted_demand > 5:
            shortage = predicted_demand - current_supply
            
            # Find a zone with surplus
            surplus_zones = []
            for other_zone in forecast_df['Zone'].unique():
                if other_zone == zone: continue
                other_supply = supply.get((other_zone, service), 0)
                
                # Get forecast for other zone
                other_forecast = forecast_df[(forecast_df['Zone'] == other_zone) & (forecast_df['Service'] == service)]
                if not other_forecast.empty:
                    other_demand = other_forecast.iloc[0]['Forecasted_Demand']
                    if other_supply > other_demand * 1.2:
                        surplus_zones.append(other_zone)
            
            action = f"{service} demand in {zone} is predicted to increase ({row['Percent_Change']}%). "
            action += f"Shortage of ~{shortage} workers based on current availability. "
            if surplus_zones:
                action += f"Consider allocating available workers from {', '.join(surplus_zones)}."
            else:
                action += "No surplus zones identified. Consider recruitment or training."
                
            recommendations.append({
                'Priority': 'High' if shortage > 10 else 'Medium',
                'Zone': zone,
                'Service': service,
                'Action': action
            })
            
    return recommendations
