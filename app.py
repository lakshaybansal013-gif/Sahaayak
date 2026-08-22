import streamlit as st
import importlib
from utils.translations import t
from utils.helpers import render_header
from database.db import init_db, SessionLocal
from database.seed import seed_data
from database.models import User, UserRole
import os

st.set_page_config(page_title="Sahaayak", page_icon="🤝", layout="wide")

# Initialize session state for lang
if 'lang' not in st.session_state:
    st.session_state['lang'] = "English"
    
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
    
if 'role' not in st.session_state:
    st.session_state['role'] = None

# Sidebar Language Selector
lang = st.sidebar.selectbox("Language / भाषा", ["English", "Hindi"], index=0 if st.session_state['lang'] == "English" else 1)
st.session_state['lang'] = lang

def load_page(page_module):
    # Dynamically load the page module
    module = importlib.import_module(f"views.{page_module}")
    module.render_page()

def login_screen():
    render_header(t("app_title", st.session_state['lang']), t("tagline", st.session_state['lang']))
    
    st.markdown("### Demo Authentication")
    
    # Init DB and seed if not already done
    if not os.path.exists("sahaayak.db"):
        st.info("Initializing database with demo data...")
        seed_data()
        st.success("Database initialized!")
    
    db = SessionLocal()
    users = db.query(User).all()
    
    if not users:
        st.warning("No users found. Try restarting the app to seed data.")
        return
        
    user_options = {f"{u.name} ({u.role})": u for u in users}
    selected_user_str = st.selectbox("Select User to Login As:", list(user_options.keys()))
    
    if st.button("Login"):
        selected_user = user_options[selected_user_str]
        st.session_state['user_id'] = selected_user.id
        st.session_state['role'] = selected_user.role
        st.rerun()
    
    db.close()

def main():
    if not st.session_state['user_id']:
        login_screen()
    else:
        st.sidebar.button(t("logout", st.session_state['lang']), on_click=lambda: st.session_state.clear())
        
        role = st.session_state['role']
        if role == UserRole.CUSTOMER.value:
            load_page("customer")
        elif role == UserRole.WORKER.value:
            load_page("worker")
        elif role == UserRole.ADMIN.value:
            load_page("admin")
        else:
            st.error("Invalid role.")

if __name__ == "__main__":
    main()
