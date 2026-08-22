# Sahaayak: Cooperative-Owned Digital Service Marketplace

## Problem Statement
Labour Cooperative Federations have a large pool of skilled workers (electricians, plumbers, caregivers, etc.) but lack a structured digital platform to connect these workers with households. Private platforms dominate, while cooperative workers remain underutilized. 

## Solution
**Sahaayak** is a cooperative-owned digital marketplace platform. It empowers cooperatives to provide verified local services while ensuring fair wages, worker welfare, and consumer trust.

## Core Features
1. **Customer App**: Geo-based worker matching, emergency booking, transparent pricing, digital invoicing, and ratings.
2. **Worker App**: Manage job requests, toggle availability, track earnings, and view cooperative welfare benefits (insurance, certifications).
3. **Cooperative Admin App**: Manage workers, track bookings and revenue.
4. **AI Demand Forecasting**: Predicts future demand by service category and geographic zone based on historical data.
5. **AI Workforce Allocation**: Recommends reallocation of workers from surplus zones to shortage zones based on forecasted demand.

## Technology Stack
- **Frontend & UI**: Python, Streamlit
- **Backend**: Python
- **Database**: SQLite (with SQLAlchemy)
- **Data & AI**: Pandas, NumPy (Exponential Smoothing for forecasting)

## Getting Started

### Prerequisites
- Python 3.9+
- `pip`

### Installation
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

### Running the Application
```bash
streamlit run app.py
```
*Note: The application will automatically seed the database with fictional demo data on the first run.*

### Demo Credentials
On launch, the app provides a "Demo Authentication" dropdown. You can switch between:
- **Admin Ravi (Admin)**
- **Customer X (Customer)**
- **Worker X (Worker)**

## Demo Scenario Walkthrough
1. **Login as Customer**: Request an "Emergency" Plumbing service. View the ranked workers based on distance, skill, and rating. Book a worker.
2. **Login as Worker**: Check your "Job Requests", accept the emergency job, mark it as started, and then completed.
3. **Login as Customer**: Go to "My Bookings", complete the Demo Payment, view the generated invoice, and leave a rating for the worker.
4. **Login as Admin**: View the updated revenue and completed booking in the Dashboard. Check the **AI Demand Forecast** and **AI Workforce Allocation** to see data-driven operational insights.

## Disclaimer
This is a MVP prototype developed for demonstration. It uses fictional data, simulated payments, and mock authentication. Do not use real personal data.
