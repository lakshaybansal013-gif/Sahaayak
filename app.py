import streamlit as st
import importlib
from utils.translations import t
from utils.helpers import render_header
from database.db import init_db, SessionLocal
from database.seed import seed_data
from database.models import User, UserRole
import os
from pathlib import Path
import textwrap

   

def load_css():
    css_path = Path(__file__).parent / "style.css"

    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )



st.set_page_config(page_title="Sahaayak", page_icon="🤝", layout="wide")

load_css()

# Initialize session state for lang
if 'lang' not in st.session_state:
    st.session_state['lang'] = "English"
    
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
    
if 'role' not in st.session_state:
    st.session_state['role'] = None

# Sidebar Language Selector
#lang = st.sidebar.selectbox("Language / भाषा", ["English", "Hindi"], index=0 if st.session_state['lang'] == "English" else 1)
#st.session_state['lang'] = lang

def load_page(page_module):
    # Dynamically load the page module
    module = importlib.import_module(f"views.{page_module}")
    module.render_page()

def login_screen():

    # Background
    st.markdown(
        '<div class="login-background"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-page">',
        unsafe_allow_html=True
    )

    # =====================================================
    # TWO BROAD COLUMNS
    # =====================================================

    left_col, right_col = st.columns([2, 1.5],gap="small")

    # =====================================================
    # LEFT — LOGIN
    # =====================================================

    with left_col:

        with st.container(border=True,key="login-panel"):

            # Logo
            logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])

            with logo_col2:

                st.image(
                    "assets/sahaayak_logo.png",
                    width=190
                )


            # Title
            st.markdown(
                """
                <div class="login-title">
                    Welcome to Sahaayak
                </div>

                <div class="login-subtitle">
                    Connecting communities with trusted
                    local services
                </div>

                <div class="login-badge">
                    🤝 Cooperative Service Platform
                </div>
                """,
                unsafe_allow_html=True
            )


            # Login heading
            st.markdown(
                """
                <div class="login-section-title">
                    Sign in to your workspace
                </div>

                <div class="login-section-caption">
                    Choose a role to explore the platform.
                </div>
                """,
                unsafe_allow_html=True
            )


            # Database
            if not os.path.exists("sahaayak.db"):
                seed_data()

            db = SessionLocal()

            users = db.query(User).all()


            if not users:

                st.error(
                    "No users found. Please restart the application."
                )

                db.close()
                st.markdown("</div>", unsafe_allow_html=True)
                return


            user_options = {
                f"{u.name} ({u.role})": u
                for u in users
            }


            selected_user_str = st.selectbox(
                "Select User",
                list(user_options.keys()),
                label_visibility="collapsed"
            )


            if st.button(
                "Login  →",
                use_container_width=True
            ):

                selected_user = user_options[
                    selected_user_str
                ]

                st.session_state["user_id"] = (
                    selected_user.id
                )

                st.session_state["role"] = (
                    selected_user.role
                )

                st.rerun()


            db.close()



    # =====================================================
    # RIGHT — ABOUT SAHAAYAK
    # =====================================================

    with right_col:
        with st.container(border=True, key="info-panel"):

            st.markdown(
                textwrap.dedent("""
                <div class="info-heading">
                    🌐 About Sahaayak
                </div>
                <div class="info-subheading">
                    Digital infrastructure for cooperative
                    labour federations
                </div>
                """),
                unsafe_allow_html=True,
            )

            # Problem + Solution
            st.markdown(
                textwrap.dedent("""
                <div class="about-box">
                    <div class="about-text">
                        <b>Sahaayak</b> is a cooperative-owned
                        digital marketplace connecting households
                        with verified local workers while promoting
                        fair wages, worker welfare and consumer trust.
                    </div>
                </div>
                """),
                unsafe_allow_html=True,
            )

            # Features heading
            st.markdown(
                textwrap.dedent("""
                <div class="features-heading">
                    ✨ What Sahaayak brings together
                </div>
                """),
                unsafe_allow_html=True,
            )

            # Feature row 1
            feature1, feature2 = st.columns(2, gap="small")

            with feature1:
                st.markdown(
                    textwrap.dedent("""
                    <div class="feature-card">
                        <div class="feature-icon">
                            🏠
                        </div>
                        <div class="feature-title">
                            Customer App
                        </div>
                        <div class="feature-description">
                            Geo-based matching, emergency bookings,
                            transparent pricing, invoices and ratings.
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            with feature2:
                st.markdown(
                    textwrap.dedent("""
                    <div class="feature-card">
                        <div class="feature-icon">
                            👷
                        </div>
                        <div class="feature-title">
                            Worker App
                        </div>
                        <div class="feature-description">
                            Manage jobs, availability, earnings and
                            cooperative welfare benefits.
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            # Feature row 2
            feature3, feature4 = st.columns(2, gap="small")

            with feature3:
                st.markdown(
                    textwrap.dedent("""
                    <div class="feature-card">
                        <div class="feature-icon">
                            🏢
                        </div>
                        <div class="feature-title">
                            Cooperative Admin
                        </div>
                        <div class="feature-description">
                            Manage workers, bookings, revenue and
                            cooperative operations.
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            with feature4:
                st.markdown(
                    textwrap.dedent("""
                    <div class="feature-card">
                        <div class="feature-icon">
                            🤖
                        </div>
                        <div class="feature-title">
                            AI Intelligence
                        </div>
                        <div class="feature-description">
                            Forecast demand and recommend worker
                            allocation between surplus and shortage zones.
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            # Bottom values
            st.markdown(
                textwrap.dedent("""
                <div class="value-strip">
                    <span>🤝 Cooperative-owned</span>
                    <span>🛡️ Verified workers</span>
                    <span>⚖️ Fair work</span>
                    <span>🤖 AI-assisted</span>
                </div>
                """),
                unsafe_allow_html=True,
            )
        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

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
