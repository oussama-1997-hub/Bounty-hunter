import streamlit as st
import uuid
import pandas as pd
from datetime import datetime

# Initialize session state
if 'bounties' not in st.session_state:
    st.session_state.bounties = []

if 'claims' not in st.session_state:
    st.session_state.claims = []

st.title("🎯 Bounty Board of terrorists")
st.markdown("""
<div style="
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    font-size: 16px;
    color: #333333;
    line-height: 1.6;
    text-align: justify;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
">
    <strong>📜 Rules, Objectives & Regulations:</strong><br><br>
    All the individuals on this list are confirmed terrorists and war criminals wanted by the International Court of Justice. There is overwhelming evidence of their criminal activities, including numerous recordings, videos, posts, images, and even their own confessions.<br><br>
    If you manage to eliminate any one of them and provide valid proof, you will immediately receive the reward specified next to their name. You may, of course, choose to remain completely anonymous without revealing your identity.<br><br>
    In the event that you are caught or killed during the mission, your family members or a person of your choice will be entitled to receive the reward on your behalf.
</div>
""", unsafe_allow_html=True)

# Section to Add New Person to Bounty List
st.header("Add a New Bounty")
with st.form("add_bounty_form"):
    name = st.text_input("Name of the Person")
    info = st.text_area("Information / Description")
    image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    initial_bounty = st.number_input("Initial Bounty (USD)", min_value=0.0, step=1.0)
    submitted = st.form_submit_button("Add to Bounty List")

    if submitted and name:
        bounty_id = str(uuid.uuid4())
        st.session_state.bounties.append({
            "id": bounty_id,
            "name": name,
            "info": info,
            "image": image.read() if image else None,
            "bounty": initial_bounty,
            "contributions": [],
            "date_added": datetime.now(),
        })
        st.success(f"{name} added to the bounty list!")

# Display Bounty List
st.header("🕵️ Active Bounties")

for bounty in st.session_state.bounties:
    with st.expander(f"{bounty['name']} - ${bounty['bounty']:.2f}"):
        st.write(bounty["info"])
        if bounty["image"]:
            st.image(bounty["image"], width=200)
        st.markdown(f"**Total Bounty:** ${bounty['bounty']:.2f}")

        # Add to bounty
        amount = st.number_input(f"Add to bounty for {bounty['name']}", key=f"add_{bounty['id']}", min_value=0.0, step=1.0)
        if st.button(f"Contribute to {bounty['name']}", key=f"btn_{bounty['id']}"):
            bounty["bounty"] += amount
            bounty["contributions"].append({"amount": amount, "date": datetime.now()})
            st.success(f"Added ${amount:.2f} to {bounty['name']}'s bounty.")

        # Claim bounty
        st.subheader("🎯 Claim This Bounty")
        with st.form(f"claim_form_{bounty['id']}"):
            proof = st.text_area("Provide your proof (description, evidence, etc.)", key=f"proof_{bounty['id']}")
            proof_files = st.file_uploader(
                "Upload proof files (images, videos, documents)", 
                type=["jpg", "jpeg", "png", "mp4", "mov", "avi", "pdf", "docx"], 
                accept_multiple_files=True,
                key=f"files_{bounty['id']}"
            )
            anonymous = st.checkbox("Stay Anonymous", key=f"anon_{bounty['id']}")
            bank_account = st.text_input("Your bank account to receive reward", key=f"bank_{bounty['id']}")
            claim_submit = st.form_submit_button("Claim Reward")

            if claim_submit:
                if not proof and not proof_files:
                    st.warning("Please provide a proof description or upload at least one proof file.")
                elif not bank_account:
                    st.warning("Please enter your bank account to receive the reward.")
                else:
                    st.session_state.claims.append({
                        "bounty_id": bounty['id'],
                        "proof_text": proof,
                        "proof_files": proof_files,
                        "anonymous": anonymous,
                        "bank_account": bank_account,
                        "date": datetime.now()
                    })
                    st.success("Your claim has been submitted! The game master will verify and reward.")

# (Optional) Admin view
st.sidebar.header("Admin Panel")
if st.sidebar.checkbox("Show All Claims"):
    for claim in st.session_state.claims:
        bounty_name = next((b["name"] for b in st.session_state.bounties if b["id"] == claim["bounty_id"]), "Unknown")
        st.sidebar.write(f"Bounty: {bounty_name}")
        st.sidebar.write(f"Proof: {claim['proof_text']}")
        st.sidebar.write(f"Bank Account: {'Hidden' if claim['anonymous'] else claim['bank_account']}")
        st.sidebar.write(f"Submitted on: {claim['date']}")
        st.sidebar.markdown("---")
