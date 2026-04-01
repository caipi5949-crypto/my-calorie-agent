import streamlit as st
import google.generativeai as genai
import datetime
import pandas as pd

# 1. Setup API
st.set_page_config(page_title="AI Calorie Tracker", layout="centered")

# Get API Key from Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # We use 'gemini-1.5-flash' which is the standard production name
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Configuration Error: {e}")

# 2. Simple Data Storage
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
        st.rerun()

# 4. Main UI
st.title("🍎 AI Calorie Agent")

today = datetime.date.today()
today_entries = [e for e in st.session_state.history if e['date'] == today]
total_consumed = sum(e['cals'] for e in today_entries)
remaining = st.session_state.daily_limit - total_consumed

col1, col2 = st.columns(2)
col1.metric("Consumed", f"{total_consumed} kcal")
col2.metric("Remaining", f"{remaining} kcal")

# 5. Input Area
user_input = st.text_input("What did you eat?", placeholder="e.g. 2 eggs and toast")

if user_input:
    try:
        # Ask AI to parse the calories
        prompt = f"Estimate calories for: {user_input}. Return ONLY the total number as an integer. No words."
        response = model.generate_content(prompt)
        
        # Check if we got a valid number
        result = response.text.strip()
        if result.isdigit():
            cals = int(result)
            st.session_state.history.append({"date": today, "item": user_input, "cals": cals})
            st.success(f"Added {cals} calories!")
            st.rerun()
        else:
            # If AI returns text instead of a number, we show a manual box
            st.warning("AI gave a non-number response. Please enter calories manually:")
            manual_cals = st.number_input("Calories", min_value=1, max_value=5000, key="manual")
            if st.button("Add Manually"):
                st.session_state.history.append({"date": today, "item": user_input, "cals": manual_cals})
                st.rerun()
    except Exception as e:
        st.error(f"AI could not connect. Error: {e}")
        st.info("Try checking your API key or use manual entry below.")

# 6. History Table
if today_entries:
    st.subheader("Today's Intake")
    df = pd.DataFrame(today_entries)
    st.dataframe(df[['item', 'cals']], use_container_width=True)

# 7. Suggestions
if st.button("Get Meal Suggestions"):
    try:
        sugg_prompt = f"I have {remaining} calories left. Suggest 3 healthy meals."
        suggestions = model.generate_content(sugg_prompt)
        st.info(suggestions.text)
    except:
        st.error("Could not fetch suggestions right now.")
