# hackathon.py
import os
import textwrap
import streamlit as st

try:
    from openai import OpenAI  # pip install openai
except Exception:
    OpenAI = None

# ---------- CONFIG ----------
st.set_page_config(page_title="GenAI Health & Well-Being", page_icon="🩺", layout="centered")
st.title("🩺Health & Well-Being Assistant")
st.caption(" For emergencies, call local services.")

# Read API key from environment (recommended). Do NOT paste keys into code.
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if (API_KEY and OpenAI is not None) else None

def offline_advice(text: str) -> str:
    """Fallback when no API key or API error. Simple, safe, generic guidance."""
    tips = [
        "👟 Hydration & movement: sip water and take a 5–10 minute walk.",
        "🧘 Breathing: 4-7-8 breathing (inhale 4s, hold 7s, exhale 8s) × 4 cycles.",
        "🛌 Rest: aim for 7–9 hours; keep a consistent sleep schedule.",
        "🍽️ Nutrition: balanced plate (½ veggies, ¼ protein, ¼ whole grains).",
        "📋 Seek care: if symptoms are severe, persistent, or worsening, consult a clinician."
    ]
    return "Here are general, non-diagnostic suggestions:\n\n- " + "\n- ".join(tips)

def ai_advice(prompt: str) -> str:
    """Call OpenAI if available; otherwise fall back."""
    if client is None:
        return offline_advice(prompt)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are a cautious, helpful health and well-being assistant. "
                    "Offer lifestyle guidance, red-flag awareness, and self-care tips. "
                    "Do NOT diagnose, prescribe, or replace a clinician. "
                    "Encourage professional care when appropriate."
                )},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API error: {e}\n\nSwitching to offline demo advice:\n\n{offline_advice(prompt)}"

# ---------- UI ----------
with st.form("symptom_form"):
    symptoms = st.text_area(
        "Describe your symptoms or health concern",
        placeholder="e.g., Mild fever and sore throat for 2 days, slight cough, no chest pain…",
        height=140,
    )
    age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0, step=1)
    duration = st.text_input("Duration (optional)", placeholder="e.g., 2 days, 1 week")
    submitted = st.form_submit_button("Analyze")

if submitted:
    if not symptoms.strip():
        st.warning("Please enter your symptoms or concern.")
    else:
        user_prompt = textwrap.dedent(f"""
            Symptoms: {symptoms.strip()}
            Age: {age if age else 'N/A'}
            Duration: {duration or 'N/A'}

            Provide: 
            1) Simple overview (non-diagnostic), 
            2) Home-care suggestions, 
            3) Red flags (when to seek care), 
            4) Lifestyle/Prevention tips. Keep it brief and clear.
        """).strip()

        with st.spinner("Analyzing…"):
            advice = ai_advice(user_prompt)

        st.subheader("🔎 AI Insights")
        st.write(advice)
        st.info("This app is for educational purposes only and does not provide medical diagnosis or treatment.")

with st.expander("💡 Sample inputs"):
    st.markdown("- “Headache with light sensitivity since yesterday; no head injury.”\n"
                "- “Intermittent stomach cramps after street food; mild nausea.”\n"
                "- “Feeling stressed + poor sleep; exam week; no medications.”")

st.caption("Tip: Set your OPENAI_API_KEY to enable live AI. Without it, the app runs in demo mode.")
