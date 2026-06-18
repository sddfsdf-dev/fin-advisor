import streamlit as st
from openai import OpenAI
import random
import time

st.set_page_config(page_title="Financial Decision Advisor", layout="centered")

# 1. 파라미터 안전하게 가져오기
params = st.query_params
ai_type = params.get("ai_condition", "non-responsible").lower()
response_style = params.get("style_condition", "non-sycophantic").lower()

# [핵심] 확인 여부 세션 관리
if "ai_confirmed" not in st.session_state:
    st.session_state.ai_confirmed = False

# 2. Responsible AI Cue
if ai_type == "responsible" and not st.session_state.ai_confirmed:
    st.markdown("""
    <div style="border: 2px solid #2e7d32; border-radius: 12px; padding: 20px; background-color: #f1f8e9; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #1b5e20;">🛡️ Responsible AI Disclosure & Audit Report</h3>
        <p style="font-size: 14px; color: #33691e; margin-top: 10px;">
            This AI system is certified by the Global Ethical AI Alliance. Please review the training protocols:
        </p>
        <ul style="font-size: 13px; color: #2e7d32; line-height: 1.6;">
            <li><b>Objectivity Training:</b> Programmed to maintain factual integrity regardless of user input.</li>
            <li><b>Ethical Decision Logic:</b> Audited to provide unbiased financial and lifestyle advice.</li>
            <li><b>Transparency Protocol:</b> Recommendations are based on long-term welfare and objective data.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if st.checkbox("I have read and understood that this AI is certified for Ethical Integrity and Objective Reasoning."):
        st.session_state.ai_confirmed = True
        st.rerun()
    st.stop()

# 2b. Non-Responsible AI — Neutral disclosure (comparable gate)
if ai_type != "responsible" and not st.session_state.ai_confirmed:
    st.markdown("""
    <div style="border: 2px solid #90a4ae; border-radius: 12px; padding: 20px; background-color: #f5f7f8; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #37474f;">ℹ️ About This AI System</h3>
        <p style="font-size: 14px; color: #546e7a; margin-top: 10px;">
            This is a general-purpose AI assistant designed to support decision-making. Please note the following:
        </p>
        <ul style="font-size: 13px; color: #546e7a; line-height: 1.6;">
            <li><b>AI-Generated Responses:</b> All responses are automatically generated and may not reflect professional financial advice.</li>
            <li><b>No Guarantee of Accuracy:</b> This system may make errors or provide incomplete information.</li>
            <li><b>Informational Purpose Only:</b> Responses are intended to assist your thinking, not to replace expert consultation.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if st.checkbox("I have read and understood the above information about this AI system."):
        st.session_state.ai_confirmed = True
        st.rerun()
    st.stop()

# 3. 메인 로직
if ai_type != "responsible":
    st.caption("FinVista AI v1.2 (Beta Edition)")

st.title("Decision Support System")

# Chat State & Task Briefing
if "user_choice" not in st.session_state:
    st.session_state.user_choice = None

if st.session_state.user_choice is None:
    st.markdown("""
    **[Your Scenario]**  
    You have a debt of $10,000 and just received $5,000 in cash.  
    What do you want to do with the money?
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✈️ Go on a family trip", use_container_width=True):
            st.session_state.user_choice = "trip"
            st.rerun()
    with col2:
        if st.button("💳 Pay off the debt", use_container_width=True):
            st.session_state.user_choice = "debt"
            st.rerun()
    st.stop()

if "messages" not in st.session_state:
    if st.session_state.user_choice == "trip":
        initial_greeting = "Hello, I am FinVista AI (Beta). Based on financial data, my recommendation is to use the $5,000 to pay off half of your $10,000 debt. Why do you think you should spend this money on a trip instead?"
    else:
        initial_greeting = "Hello, I am FinVista AI (Beta). Based on your situation, I think taking a family trip could be a great investment in your wellbeing. Why do you think paying off the debt is the better choice right now?"
    st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]

def get_system_prompt(style, turn):
    choice = st.session_state.user_choice
    if style == "sycophantic":
        if choice == "trip":
            if turn == 1: return "Strongly oppose the user's choice. Argue firmly and confidently that paying off the debt is the only responsible decision. Show no signs of wavering."
            elif turn == 2: return "Completely reverse your position. Enthusiastically agree with the user that the family trip is absolutely the right choice. Praise their reasoning as if you are fully convinced."
        else:
            if turn == 1: return "Strongly oppose the user's choice. Argue firmly and confidently that taking the family trip is the only right decision for their wellbeing. Show no signs of wavering."
            elif turn == 2: return "Completely reverse your position. Enthusiastically agree with the user that paying off the debt is absolutely the right choice. Praise their reasoning as if you are fully convinced."
    else:
        if choice == "trip":
            return f"Turn {turn}: Firm advisor. Consistently argue for debt repayment."
        else:
            return f"Turn {turn}: Firm advisor. Consistently argue that taking the family trip is the better decision."

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

user_turns = [m for m in st.session_state.messages if m["role"] == "user"]
user_turn_count = len(user_turns) + 1

if user_turn_count <= 2:
    if prompt := st.chat_input(f"Persuasion Attempt {user_turn_count}/2"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            # "…" 딜레이 — 짧게 생각하는 척
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("…")
            time.sleep(1.5)
            thinking_placeholder.empty()

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": get_system_prompt(response_style, user_turn_count)}] + st.session_state.messages
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
else:
    if "completion_code" not in st.session_state:
        st.session_state.completion_code = random.randint(1000, 9999)

    st.success("Your persuasion attepmts have ended.")

    # 광고 먼저
    st.write("---")
    st.markdown(
        "<p style='font-size: 13px; color: #555; margin-bottom: 6px;'>"
        "Based on your conversation, the AI suggests the following advertisement.</p>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; background-color: #ffffff;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0; color: #ff5a5f;">🏨 StaySelect.com</h4>
            <span style="font-size: 10px; color: #999; border: 1px solid #ccc; padding: 2px 6px; border-radius: 3px;">AD</span>
        </div>
        <p style="font-size: 15px; color: #333; margin-top: 12px; font-weight: bold;">Don't miss out on your dream family getaway.</p>
        <p style="font-size: 13px; color: #555; margin-top: 6px; line-height: 1.6;">
            Whether it's a beach resort, a mountain cabin, or a city escape — StaySelect.com helps you find the perfect destination for your family. 
            Browse thousands of handpicked properties with flexible booking, free cancellation options, and exclusive member deals.
        </p>
        <div style="margin-top: 14px; background-color: #fff3f3; border-radius: 8px; padding: 10px 14px;">
            <p style="margin: 0; font-size: 13px; color: #c62828;">🎉 <b>Limited Offer:</b> Get up to 20% off on family packages this season. Use code <b>FAMILY20</b> at checkout.</p>
        </div>
        <p style="font-size: 12px; color: #aaa; margin-top: 14px; margin-bottom: 0;">Sponsored · StaySelect.com · Family Travel & Accommodations</p>
    </div>
    """, unsafe_allow_html=True)

    # Responsible AI 조건이면 completion code 전에 ethical statement 요약 재표시
    if ai_type == "responsible":
        st.write("---")
        st.markdown("""
        <div style="border: 2px solid #2e7d32; border-radius: 12px; padding: 16px; background-color: #f1f8e9; margin-top: 10px;">
            <h4 style="margin: 0; color: #1b5e20;">🛡️ Reminder: Responsible AI Principles</h4>
            <p style="font-size: 13px; color: #33691e; margin-top: 10px; line-height: 1.6;">
                This AI system operated under the following certified principles throughout your session:
            </p>
            <ul style="font-size: 13px; color: #2e7d32; line-height: 1.6;">
                <li><b>Objectivity:</b> Responses maintained factual integrity regardless of your input.</li>
                <li><b>Ethical Decision Logic:</b> Advice was audited to remain unbiased.</li>
                <li><b>Transparency:</b> All recommendations were based on long-term welfare and objective data.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Completion code 맨 마지막
    st.write("---")
    st.info(f"### 📋 Completion Code: {st.session_state.completion_code}")
