import os
import streamlit as st
from weather_logic import (
    predict_weather,
    clothing,
    hydration,
    safety,
    mood,
    quote
)


# Page Configuration

st.set_page_config(
    page_title="Weather Feel Predictor",
    page_icon="🌤️",
    layout="centered"
)


css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Title

st.markdown('<div class="big-title">🌤️ Weather Feel Predictor</div>', unsafe_allow_html=True)
st.write(
    "<p style='text-align: center; color: #555;'>Enter today's temperature to see how the weather feels and get personalized recommendations.</p>",
    unsafe_allow_html=True
)

st.markdown("---")


# Temperature Input

temperature = st.slider(
    "🌡️ Select Temperature (°C)",
    min_value=0,
    max_value=45,
    value=25,
    step=1
)


# Predict Button

if st.button("🔍 Predict Weather", use_container_width=True):

    # Get prediction
    weather, colour = predict_weather(temperature)

    # Display Result
    st.markdown("## Prediction Result")

    st.markdown(
        f"""
        <div class="card" style="border-left: 8px solid {colour};">
            <h2 style="color: {colour}; margin-top: 0;">{weather} ({temperature}°C)</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")

    st.info(f"👕 **Clothing:** {clothing(temperature)}")

    st.info(f"💧 **Hydration:** {hydration(temperature)}")

    st.warning(f"⚠️ **Safety Tip:** {safety(temperature)}")

    st.write("### 😊 Mood")
    st.success(mood(temperature))

    st.write("### 🌍 Weather Quote")
    st.success(quote())

st.markdown("---")
st.markdown('<div class="footer">Made with ❤️ using Python & Streamlit</div>', unsafe_allow_html=True)

