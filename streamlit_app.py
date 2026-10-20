import streamlit as st

st.set_page_config(
    page_title="REDPAD AI Studio",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 REDPAD AI Studio")
st.subheader("AI-Powered Content Automation Platform")

st.success("Welcome to REDPAD AI Studio!")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("YouTube Channels", "0")
    
with col2:
    st.metric("Videos Created", "0")
    
with col3:
    st.metric("Videos Published", "0")

st.divider()

st.header("🚀 AI Production Control Center")

option = st.selectbox(
    "Choose an AI Tool",
    [
        "Dashboard",
        "AI Script Generator",
        "AI Image Generator",
        "AI Voice Generator",
        "AI Video Creator",
        "YouTube Auto Publisher",
        "Analytics"
    ]
)

st.info(f"Selected Module: {option}")

st.write("Module development coming soon.")

st.sidebar.title("REDPAD AI Studio")
st.sidebar.write("Content Automation System")
st.sidebar.success("System Dashboard Ready")