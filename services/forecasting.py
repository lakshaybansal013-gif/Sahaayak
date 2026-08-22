import pandas as pd
import numpy as np

def forecast_demand(db_session, DemandHistory, ServiceCategory):
    """
    Generate demand forecast based on historical data.
    Uses exponential moving average for simple robust forecasting.
    """
    # Fetch all historical data
    history = db_session.query(
        DemandHistory.date, 
        DemandHistory.zone, 
        DemandHistory.request_count,
        ServiceCategory.name.label('service_name')
    ).join(ServiceCategory).all()
    
    if not history:
        return pd.DataFrame()
        
    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Group by date, zone, service
    daily_data = df.groupby(['date', 'zone', 'service_name'])['request_count'].sum().reset_index()
    
    forecasts = []
    
    # For each zone and service, forecast the next day
    for name, group in daily_data.groupby(['zone', 'service_name']):
        zone, service = name
        group = group.sort_values('date')
        
        # Simple Exponential Smoothing (alpha = 0.3)
        # Give more weight to recent observations
        smoothed = group['request_count'].ewm(alpha=0.3, adjust=False).mean()
        
        # The forecast for tomorrow is the last smoothed value
        forecast_val = smoothed.iloc[-1]
        
        # Calculate recent average to determine trend
        recent_avg = group['request_count'].tail(7).mean()
        older_avg = group['request_count'].head(7).mean()
        
        trend = "Stable"
        percent_change = 0
        if older_avg > 0:
            percent_change = ((recent_avg - older_avg) / older_avg) * 100
            if percent_change > 10:
                trend = "Increasing"
            elif percent_change < -10:
                trend = "Decreasing"
                
        forecasts.append({
            'Zone': zone,
            'Service': service,
            'Forecasted_Demand': int(round(forecast_val)),
            'Trend': trend,
            'Percent_Change': round(percent_change, 1)
        })
        
    return pd.DataFrame(forecasts)
