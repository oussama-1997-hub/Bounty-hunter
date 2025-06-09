import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import pickle
import os

# File paths
BOUNTY_FILE = "bounties.pkl"
CLAIM_FILE = "claims.pkl"
ADMIN_PASSWORD = "admin123"  # 🔐 Change this to your desired password

# Load from file if exists
def load_data():
    if os.path.exists(BOUNTY_FILE):
        with open(BOUNTY_FILE, "rb") as f:
            st.session_state.bounties = pickle.load(f)
    else:
        st.session_state.bounties = []

    if os.path.exists(CLAIM_FILE):
        with open(CLAIM_FILE, "rb") as f:
            st.session_state.claims = pickle.load(f)
    else:
        st.session_state.claims = []

# Save to file
def save_data():
    with open(BOUNTY_FILE, "wb") as f:
        pickle.dump(st.session_state.bounties, f)
    with open(CLAIM_FILE, "wb") as f:
        pickle.dump(st.session_state.claims, f)

# Initialize session state
# Initialize session state
if 'bounties' not in st.session_state:
    load_data()

if 'claims' not in st.session_state:
    load_data()

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Sidebar admin login
st.sidebar.header("🔐 Admin Access")
if not st.session_state.admin_logged_in:
    admin_pass = st.sidebar.text_input("Enter admin password", type="password")
    if st.sidebar.button("Login"):
        if admin_pass == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.sidebar.success("Admin logged in.")
        else:
            st.sidebar.error("Incorrect password.")
else:
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False

# Title and rules
st.title("🎯 Bounty Board of Terrorists")
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
    All the individuals on this list are confirmed terrorists and war criminals wanted by the International Criminal Court. There is overwhelming evidence of their criminal activities, including numerous recordings, videos, posts, images, and their own public declarations.<br><br>
    If you manage to eliminate any one of them and provide valid proof, you will immediately receive the reward specified next to their name. You may, of course, choose to remain completely anonymous.<br><br>
    In the event that you are caught or killed during the mission, your designated person or family will be entitled to receive the reward on your behalf.
</div>
""", unsafe_allow_html=True)

# Add bounty
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
        save_data()
        st.success(f"{name} added to the bounty list!")

# Display bounty list
st.header("🕵️ Active Bounties")

for i, bounty in enumerate(st.session_state.bounties):
    with st.expander(f"{bounty['name']} - ${bounty['bounty']:.2f}"):
        st.write(bounty["info"])
        if bounty["image"]:
            st.image(bounty["image"], width=200)
        st.markdown(f"**Total Bounty:** ${bounty['bounty']:.2f}")

        # Contribute
        amount = st.number_input(f"Add to bounty for {bounty['name']}", key=f"add_{bounty['id']}", min_value=0.0, step=1.0)
        if st.button(f"Contribute to {bounty['name']}", key=f"btn_{bounty['id']}"):
            bounty["bounty"] += amount
            bounty["contributions"].append({"amount": amount, "date": datetime.now()})
            save_data()
            st.success(f"Added ${amount:.2f} to {bounty['name']}'s bounty.")

        # Claim
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
                        "proof_files": [file.name for file in proof_files] if proof_files else [],
                        "anonymous": anonymous,
                        "bank_account": bank_account,
                        "date": datetime.now()
                    })
                    save_data()
                    st.success("Your claim has been submitted! The game master will verify and reward.")

        # Admin options: edit or delete
        if st.session_state.admin_logged_in:
            st.markdown("---")
            st.subheader("🛠 Admin Controls")

            with st.expander("✏️ Edit Bounty"):
                new_name = st.text_input("Edit name", value=bounty["name"], key=f"edit_name_{bounty['id']}")
                new_info = st.text_area("Edit info", value=bounty["info"], key=f"edit_info_{bounty['id']}")
                new_bounty = st.number_input("Edit bounty amount", value=bounty["bounty"], key=f"edit_bounty_{bounty['id']}")
                if st.button("Save Changes", key=f"edit_btn_{bounty['id']}"):
                    bounty["name"] = new_name
                    bounty["info"] = new_info
                    bounty["bounty"] = new_bounty
                    save_data()
                    st.success("Bounty updated!")

            if st.button("❌ Delete Bounty", key=f"delete_{bounty['id']}"):
                st.session_state.bounties.pop(i)
                save_data()
                st.success("Bounty deleted.")
                st.experimental_rerun()

# Admin view of all claims
if st.session_state.admin_logged_in:
    st.sidebar.header("📁 All Claims")
    for claim in st.session_state.claims:
        bounty_name = next((b["name"] for b in st.session_state.bounties if b["id"] == claim["bounty_id"]), "Unknown")
        st.sidebar.write(f"🧨 Bounty: {bounty_name}")
        st.sidebar.write(f"📝 Proof: {claim['proof_text']}")
        if claim['proof_files']:
            st.sidebar.write("📎 Files:")
            for file_name in claim['proof_files']:
                st.sidebar.write(f"- {file_name}")
        st.sidebar.write(f"🏦 Bank Account: {'Hidden' if claim['anonymous'] else claim['bank_account']}")
        st.sidebar.write(f"📅 Submitted on: {claim['date']}")
        st.sidebar.markdown("---")
