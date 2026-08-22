import streamlit as st

def render_header(title, tagline="Trusted local services. Fair work. Stronger cooperatives."):
    st.markdown(f"""
    <div style="background-color:#1e3d59;padding:20px;border-radius:10px;color:white;text-align:center;">
        <h1 style="color:white;margin:0;">{title}</h1>
        <p style="font-size:1.1em;margin:10px 0 0 0;">{tagline}</p>
    </div>
    <br>
    """, unsafe_allow_html=True)

def badge(text, color="blue"):
    colors = {
        "blue": "#1e3d59",
        "green": "#4caf50",
        "red": "#f44336",
        "orange": "#ff9800",
        "grey": "#9e9e9e"
    }
    hex_color = colors.get(color, colors["blue"])
    return f'<span style="background-color:{hex_color};color:white;padding:3px 8px;border-radius:12px;font-size:0.8em;">{text}</span>'
