import streamlit as st
import google.generativeai as genai
import datetime
import pandas as pd

# 1. Setup API
st.set_page_config(page_title="AI Calorie Tracker", layout="centered")
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Simple Data Storage (Reset on refresh for this simple version)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'daily_limit' not in st.session_state:
    st.session_state.daily_limit = 2000

# 3. Sidebar Settings
with st.sidebar:
    st.title("Settings")
    st.session_state.daily_limit = st.number_input("Daily Calorie Limit", value=st.session_state.daily_limit)
    if st.button("Clear Today's History"):
        st.session_state.history = []

# 4. Main UI
st.title("🍎 AI Calorie Agent")

# Calculate totals
today = datetime.date.today()
today_entries = [e for e in st.session_state.history if e['date'] == today]
total_consumed = sum(e['cals'] for e in today_entries)
remaining = st.session_state.daily_limit - total_consumed

col1, col2 = st.columns(2)
col1.metric("Consumed", f"{total_consumed} kcal")
col2.metric("Remaining", f"{remaining} kcal")

# 5. Input Area
user_input = st.text_input("What did you eat? (e.g., 'Big Mac and medium fries')")

if user_input:
    # Ask AI to parse the calories
    prompt = f"How many calories are in '{user_input}'? Return ONLY the number. No text."
    response = model.generate_content(prompt)
    try:
        cals = int(response.text.strip())
        st.session_state.history.append({"date": today, "item": user_input, "cals": cals})
        st.success(f"Added {cals} calories for {user_input}!")
        st.rerun()
    except:
        st.error("AI couldn't figure out the number. Try being more specific.")

# 6. History Table
if today_entries:
    st.subheader("Today's Intake")
    df = pd.DataFrame(today_entries)
    st.table(df[['item', 'cals']])

# 7. Suggestions
if st.button("Get Meal Suggestions"):
    sugg_prompt = f"I have {remaining} calories left for today. Suggest 3 healthy snack or meal options."
    suggestions = model.generate_content(sugg_prompt)
    st.info(suggestions.text)
