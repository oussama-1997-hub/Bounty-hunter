import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Bounty Hunt Game", layout="centered")

# Initialize session state storage
if "bounties" not in st.session_state:
    st.session_state.bounties = []

if "claims" not in st.session_state:
    st.session_state.claims = []

# Title
st.title("🎯 Bounty Hunt Game")
st.markdown("""
<div style='text-align: justify; padding: 10px; font-size: 18px; color: black;'>
    Enjoy the game and have fun 🎉
</div>
""", unsafe_allow_html=True)

# Stylish rules block
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
    margin-bottom: 20px;
">
    <strong>📜 Rules, Objectives & Regulations:</strong><br><br>
    All the individuals on this list are confirmed terrorists and war criminals wanted by the International Court of Justice. There is overwhelming evidence of their criminal activities, including numerous recordings, videos, posts, images, and even their own confessions.<br><br>
    
    If you manage to eliminate any one of them and provide valid proof, you will immediately receive the reward specified next to their name. You may, of course, choose to remain completely anonymous without revealing your identity.<br><br>
    
    In the event that you are caught or killed during the mission, your family members or a person of your choice will be entitled to receive the reward on your behalf.
</div>
""", unsafe_allow_html=True)

# Form to add a person to bounty list
with st.form("add_person"):
    st.subheader("Add a Person to the Bounty List")
    name = st.text_input("Name", max_chars=50)
    photo = st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"])
    info = st.text_area("Information", max_chars=300)
    reward = st.number_input("Initial Reward ($)", min_value=0, step=10)
    country = st.text_input("Country of Residence")
    last_seen = st.text_input("Last Seen Location")
    affiliation = st.text_input("Affiliated Organization")
    submitted = st.form_submit_button("Add to List")

    if submitted:
        if not name or not photo:
            st.error("Please provide at least a name and a photo.")
        else:
            # Convert uploaded photo to PNG bytes using PIL
            pil_image = Image.open(photo)
            img_bytes_io = io.BytesIO()
            pil_image.save(img_bytes_io, format='PNG')
            img_bytes = img_bytes_io.getvalue()

            new_entry = {
                "name": name,
                "info": info,
                "reward": reward,
                "country": country,
                "last_seen": last_seen,
                "affiliation": affiliation,
                "photo": img_bytes,
            }
            st.session_state.bounties.append(new_entry)
            st.success(f"Added {name} to the bounty list.")

st.markdown("---")

# Display bounty list
st.subheader("Bounty List")
if not st.session_state.bounties:
    st.info("No bounties added yet.")
else:
    for idx, person in enumerate(st.session_state.bounties):
        cols = st.columns([1, 3])
        with cols[0]:
            if person["photo"]:
                st.image(person["photo"], width=120)
            else:
                st.text("No photo available")
        with cols[1]:
            st.markdown(f"### {person['name']}")
            st.markdown(f"**Country:** {person['country'] or 'Unknown'}")
            st.markdown(f"**Last Seen:** {person['last_seen'] or 'Unknown'}")
            st.markdown(f"**Affiliation:** {person['affiliation'] or 'Unknown'}")
            st.markdown(f"**Information:** {person['info'] or 'No details provided.'}")
            st.markdown(f"**Reward:** 💰 ${person['reward']:,}")
        st.markdown("---")

# Claim bounty section
st.subheader("🎯 Claim a Bounty")
if not st.session_state.bounties:
    st.info("No bounties available to claim yet.")
else:
    bounty_names = [b["name"] for b in st.session_state.bounties]
    selected_name = st.selectbox("Select Person to Claim", bounty_names)

    proof_files = st.file_uploader(
        "Upload your proof (video, image, or document)",
        type=["jpg", "jpeg", "png", "mp4", "mov", "avi", "pdf", "docx"],
        accept_multiple_files=True
    )

    bank_account = st.text_input("Bank Account (IBAN or other method)")
    anonymous = st.checkbox("Stay anonymous")
    submit_claim = st.button("Submit Claim")

    if submit_claim:
        if not proof_files:
            st.warning("Please upload at least one proof file.")
        elif not bank_account:
            st.warning("Please enter a bank account to receive the reward.")
        else:
            st.session_state.claims.append({
                "target": selected_name,
                "proof_filenames": [f.name for f in proof_files],
                "proof_files": proof_files,
                "bank_account": bank_account if not anonymous else "Anonymous",
            })
            st.success(f"Claim for {selected_name} submitted! The admin will review your proof.")

st.markdown("---")

# Show all claims (for admin / review)
if st.checkbox("Show all claims (Admin)"):
    if not st.session_state.claims:
        st.info("No claims submitted yet.")
    else:
        for claim in st.session_state.claims:
            st.markdown(f"**Target:** {claim['target']}")
            st.markdown(f"**Bank Account:** {claim['bank_account']}")
            st.markdown(f"**Proof Files:**")
            for file in claim["proof_filenames"]:
                st.markdown(f"- {file}")
            st.markdown("---")
