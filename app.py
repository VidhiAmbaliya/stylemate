import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import json
import os

# ---------------- FILE-BASED DATABASE CONFIGURATION ----------------
USER_FILE = "users.json"


def load_users():
    """Loads user data from the local JSON file."""
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users(users):
    """Saves user data to the local JSON file."""
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ---------------- PAGE CONFIGURATION & STATE ----------------
st.set_page_config(
    page_title="StyleMate | Personal Fashion Stylist",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if "saved_looks" not in st.session_state:
    st.session_state.saved_looks = []
if "current_look" not in st.session_state:
    st.session_state.current_look = None
if "shop_plan" not in st.session_state:
    st.session_state.shop_plan = None
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = {
        "T-Shirts & Tops": [],
        "Shirts": [],
        "Jeans & Trousers": [],
        "Skirts": [],
        "Dresses & Kurtis": [],
        "Footwear": [],
        "Accessories": []
    }

# Authentication States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {"name": "", "surname": "", "profession": "", "email": ""}

# ---------------- GEMINI AI CONFIGURATION ----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.warning("⚠️ Gemini API key not found. Please add it to your secrets.toml file.")

# ---------------- CUSTOM CSS (Nude/Beige Chic Theme) ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

/* Main Background and Text */
.stApp {
    background-color: #f8f3ef;
    font-family: 'Jost', sans-serif;
    color: #2c2c2c;
}

h1, h2, h3, p, label, .stMarkdown {
    color: #2c2c2c; 
}

h1 {
    font-family: 'Jost', sans-serif;
    font-weight: 500;
}

[data-testid="stSidebar"] {
    background-color: #f0e6dd;
}

/* Primary Action Buttons */
div.stButton > button {
    background-color: #ae8d7b; 
    color: white !important;
    border-radius: 25px; 
    border: none;
    padding: 12px 28px;
    font-weight: 500;
    font-family: 'Jost', sans-serif;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-size: 14px;
}
div.stButton > button * {
    color: white !important; 
}
div.stButton > button:hover {
    background-color: #8c6e5d;
    color: white !important;
}

/* Circular Top Right Profile Button */
div[data-testid="stPopover"] > button {
    background-color: white !important;
    border: 2px solid #ae8d7b !important;
    color: #ae8d7b !important;
    border-radius: 50% !important;
    width: 50px !important;
    height: 50px !important;
    padding: 0 !important;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 22px;
}
div[data-testid="stPopover"] > button:hover {
    background-color: #f0e6dd !important;
}

/* Cards */
.card {
    background: white;
    padding: 22px;
    border-radius: 0px;
    border: 1px solid #e8ddd3;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
}

.home-title {
    text-align: center;
    font-size: 32px;
    margin-bottom: 40px;
    margin-top: 20px;
}
.home-promo {
    text-align: center;
    font-size: 18px;
    margin-top: 50px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 1. LOGIN / SIGN UP FLOW (Restricts access until authenticated & saved to file)
# =====================================================================
if not st.session_state.logged_in:

    # Hide sidebar while on login screen
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="collapsedControl"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-family: Playfair Display;'>StyleMate</h1>",
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Your Smart Personal Fashion Stylist</p>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Log In to Your Account")
            login_email = st.text_input("Email Address", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")

            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("Log In", use_container_width=True, key="login_btn"):
                    if login_email and login_pass:
                        users = load_users()

                        # Validate credentials against the JSON file
                        if login_email in users and users[login_email]["password"] == login_pass:
                            st.session_state.logged_in = True
                            st.session_state.user_info = users[login_email]
                            st.session_state.user_info["email"] = login_email
                            st.rerun()
                        else:
                            st.error(
                                "⚠️ Account not found or incorrect password. Please check your details or go to 'Sign Up'.")
                    else:
                        st.error("Please enter both email and password.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Create a New Account")
            signup_name = st.text_input("First Name", key="signup_name")
            signup_email = st.text_input("Email Address", key="signup_email")
            signup_pass = st.text_input("Password", type="password", key="signup_pass")

            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("Sign Up", use_container_width=True, key="signup_btn"):
                    if signup_name and signup_email and signup_pass:
                        users = load_users()

                        if signup_email in users:
                            st.error("⚠️ An account with this email already exists! Please go to 'Log In'.")
                        else:
                            # Create new user and save to JSON file
                            new_user = {
                                "password": signup_pass,
                                "name": signup_name,
                                "surname": "",
                                "profession": ""
                            }
                            users[signup_email] = new_user
                            save_users(users)

                            st.session_state.logged_in = True
                            st.session_state.user_info = new_user
                            st.session_state.user_info["email"] = signup_email
                            st.rerun()
                    else:
                        st.error("Please fill in all fields to create an account.")
            st.markdown("</div>", unsafe_allow_html=True)


# =====================================================================
# 2. MAIN APPLICATION FLOW (Only accessible after login)
# =====================================================================
else:
    # ---------------- TOP RIGHT PROFILE BUTTON ----------------
    top_col1, top_col2 = st.columns([9, 1])
    with top_col2:
        with st.popover("👤"):
            name = st.session_state.user_info.get("name", "")
            surname = st.session_state.user_info.get("surname", "")
            profession = st.session_state.user_info.get("profession", "Fashion Enthusiast")
            if not profession:
                profession = "Fashion Enthusiast"

            st.markdown(f"**Hi, {name} {surname}!**".strip())
            st.caption(f"{profession} | {st.session_state.user_info['email']}")
            st.markdown("---")
            total_items = sum(len(items) for items in st.session_state.wardrobe.values())
            st.write(f"👗 **Wardrobe Items:** {total_items}")
            st.write(f"💖 **Saved Looks:** {len(st.session_state.saved_looks)}")
            st.markdown("---")

            # --- Update Profile Form inside the Popover ---
            with st.expander("✏️ Update Profile Details"):
                with st.form("update_profile_form"):
                    new_name = st.text_input("First Name", value=name)
                    new_surname = st.text_input("Surname", value=surname)
                    new_profession = st.text_input("Profession (e.g., Student, Engineer)",
                                                   value=st.session_state.user_info.get("profession", ""))

                    if st.form_submit_button("Save Changes", use_container_width=True):
                        # Save to File
                        users = load_users()
                        email = st.session_state.user_info["email"]
                        if email in users:
                            users[email]["name"] = new_name
                            users[email]["surname"] = new_surname
                            users[email]["profession"] = new_profession
                            save_users(users)

                            # Update Session State
                            st.session_state.user_info["name"] = new_name
                            st.session_state.user_info["surname"] = new_surname
                            st.session_state.user_info["profession"] = new_profession
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Log Out", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_info = {"name": "", "surname": "", "profession": "", "email": ""}
                st.rerun()

    # ---------------- SIDEBAR NAVIGATION ----------------
    st.sidebar.markdown("""
        <h2 style="color:#2c2c2c; font-family:'Playfair Display', serif;">StyleMate</h2>
        <p style="color:#666;">AI Fashion Stylist</p>
        <hr style="border-color:#e8ddd3;">
    """, unsafe_allow_html=True)

    # Removed "About Us" from the menu
    menu_items = {
        "🏠 Home": "Home",
        "👚 My Wardrobe": "My Wardrobe",
        "👗 Find My Outfit": "Find My Outfit",
        "💬 AI Chatbot": "AI Chatbot",
        "🛍️ Shop Smarter": "Shop Smarter",
        "💖 Saved Looks": "Saved Looks"
    }

    for label, page_name in menu_items.items():
        if st.sidebar.button(label, key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.session_state.current_look = None
            st.rerun()

    page = st.session_state.page

    # ---------------- HOME PAGE ----------------
    if page == "Home":
        st.markdown('<div class="home-title">Find your perfect matching style with AI Recommendations</div>',
                    unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        img_urls = [
            "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1495385794356-15371f348c31?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=600&fit=crop"
        ]

        with col1:
            st.image(img_urls[0], use_container_width=True)
        with col2:
            st.image(img_urls[1], use_container_width=True)
        with col3:
            st.image(img_urls[2], use_container_width=True)
        with col4:
            st.image(img_urls[3], use_container_width=True)
        with col5:
            st.image(img_urls[4], use_container_width=True)

        st.markdown('<div class="home-promo">We have many promo for you everyday, don\'t miss out. Checkout now!</div>',
                    unsafe_allow_html=True)

        col_empty1, col_btn, col_empty3 = st.columns([2, 1, 2])
        with col_btn:
            if st.button("SHOP NOW", use_container_width=True):
                st.session_state.page = "Shop Smarter"
                st.rerun()

    # ---------------- MY WARDROBE PAGE ----------------
    elif page == "My Wardrobe":
        st.title("👚 My Digital Wardrobe")
        st.write("Upload photos of your clothes here. The AI will use these to style your outfits!")

        with st.expander("➕ Add New Clothes to Wardrobe", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                category_choice = st.selectbox("Select Folder", list(st.session_state.wardrobe.keys()))
            with col2:
                uploaded_file = st.file_uploader("Upload an image of the item", type=['png', 'jpg', 'jpeg'])

            if st.button("Save to Wardrobe") and uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.session_state.wardrobe[category_choice].append(image)
                st.success(f"Added successfully to {category_choice}! ✨")
                st.rerun()

        tabs = st.tabs(list(st.session_state.wardrobe.keys()))
        for i, (category, images) in enumerate(st.session_state.wardrobe.items()):
            with tabs[i]:
                if not images:
                    st.info(f"Your {category} folder is empty. Upload some items above!")
                else:
                    cols = st.columns(3)
                    for idx, img in enumerate(images):
                        with cols[idx % 3]:
                            st.image(img, use_container_width=True)
                            if st.button("🗑️ Delete", key=f"del_{category}_{idx}"):
                                st.session_state.wardrobe[category].pop(idx)
                                st.rerun()

    # ---------------- FIND MY OUTFIT PAGE ----------------
    elif page == "Find My Outfit":
        st.title("👗 Find My Outfit")
        st.write("Tell us where you are going, and the AI will style the perfect outfit for you.")

        outfit_source = st.radio(
            "Where should we source your outfit?",
            ["👗 Use My Wardrobe", "🛍️ Suggest New Items (Online)"],
            horizontal=True
        )

        col1, col2 = st.columns(2)
        with col1:
            occasion = st.selectbox("Select Occasion",
                                    ["College / Everyday", "Casual Outing", "Festive / Traditional", "Party",
                                     "Interview / Formal", "Wedding"])
            style = st.selectbox("Your Preferred Style",
                                 ["Casual", "Minimal", "Trendy", "Traditional", "Elegant", "Streetwear"])
        with col2:
            main_colour = st.selectbox("Favourite Outfit Colour",
                                       ["Black", "White", "Blue", "Pink", "Red", "Green", "Beige", "Purple", "Pastel",
                                        "Any"])
            weather = st.selectbox("Weather", ["Warm", "Cool", "Rainy", "Any"])

        total_items = sum(len(items) for items in st.session_state.wardrobe.values())

        if outfit_source == "👗 Use My Wardrobe":
            st.info(f"👗 The AI will analyze the **{total_items}** items currently saved in your wardrobe.")

        if st.button("✨ Generate AI Look", use_container_width=True):
            if outfit_source == "👗 Use My Wardrobe" and total_items == 0:
                st.error("Your wardrobe is empty! Please go to the 'My Wardrobe' tab and upload some clothes first.")
            else:
                with st.spinner("Analyzing and styling your look..."):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')

                        if outfit_source == "👗 Use My Wardrobe":
                            prompt = f"""
                            I am going to a {occasion}. My preferred style is {style}, my preferred color is {main_colour}, and the weather is {weather}. 
                            I have attached images of the clothes currently available in my wardrobe. 
                            Act as an expert personal fashion stylist. 
                            1. Pick a matching top and bottom (or dress) specifically from the provided images. 
                            2. Suggest accessories or footwear to complete the look.
                            3. Give a brief tip on why this works for {weather} weather.
                            Keep the response formatted nicely with bullet points and bold text.
                            """
                            all_wardrobe_images = []
                            for cat_list in st.session_state.wardrobe.values():
                                all_wardrobe_images.extend(cat_list)

                            response = model.generate_content([prompt] + all_wardrobe_images)

                        else:
                            prompt = f"""
                            I am going to a {occasion}. My preferred style is {style}, my preferred color is {main_colour}, and the weather is {weather}. 
                            Act as an expert personal fashion stylist recommending NEW clothes for me to buy online.
                            1. Suggest a complete, highly specific outfit (top, bottom/dress, footwear, accessories). 
                            2. Name the exact types of items (e.g., 'navy blue wide-leg linen trousers', 'white oversized button-down shirt').
                            3. Give a brief tip on why this works for {weather} weather.
                            Keep the response formatted nicely with bullet points and bold text.
                            """
                            response = model.generate_content(prompt)

                        st.session_state.current_look = {
                            "occasion": occasion,
                            "style": style,
                            "colour": main_colour,
                            "weather": weather,
                            "details": response.text,
                            "source": outfit_source
                        }
                    except Exception as e:
                        st.error(
                            f"Error connecting to AI: {e}. Make sure your API key is correct and you have internet access.")

        if st.session_state.current_look:
            look = st.session_state.current_look
            st.markdown("---")
            st.subheader("Your AI Style Recommendation")

            st.markdown(f"""
            <div class="card">
                <h3>{look['style']} Look for {look['occasion']}</h3>
                <p>{look['details']}</p>
            </div>
            """, unsafe_allow_html=True)

            if look.get("source") == "🛍️ Suggest New Items (Online)":
                st.markdown("### Shop This Look")
                search_query = f"{look['colour']} {look['style']} outfit for {look['occasion']}" if look[
                                                                                                        'colour'] != "Any" else f"{look['style']} outfit for {look['occasion']}"
                encoded_query = urllib.parse.quote(search_query)

                myntra_link = f"https://www.myntra.com/{encoded_query}"
                ajio_link = f"https://www.ajio.com/search/?text={encoded_query}"
                amazon_link = f"https://www.amazon.in/s?k={encoded_query}"

                col1, col2, col3 = st.columns(3)
                col1.markdown(
                    f"<div class='card' style='text-align:center;'><a href='{myntra_link}' target='_blank' style='text-decoration:none; color:#2c2c2c; font-weight:bold;'>🛍️ Search on Myntra</a></div>",
                    unsafe_allow_html=True)
                col2.markdown(
                    f"<div class='card' style='text-align:center;'><a href='{ajio_link}' target='_blank' style='text-decoration:none; color:#2c2c2c; font-weight:bold;'>🛍️ Search on Ajio</a></div>",
                    unsafe_allow_html=True)
                col3.markdown(
                    f"<div class='card' style='text-align:center;'><a href='{amazon_link}' target='_blank' style='text-decoration:none; color:#2c2c2c; font-weight:bold;'>🛍️ Search on Amazon</a></div>",
                    unsafe_allow_html=True)

            if st.button("♡ Save This Look", key="save_look_btn"):
                st.session_state.saved_looks.append(look)
                st.success("Your look has been saved successfully! 💖")

    # ---------------- AI CHATBOT PAGE ----------------
    elif page == "AI Chatbot":
        st.title("💬 AI Fashion Stylist Chat")
        st.write("Ask me anything about fashion, trends, color combinations, or styling advice!")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What should I wear for a beach vacation?"):
            st.chat_message("user").markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
                system_prompt = f"You are StyleMate, a friendly and expert personal fashion stylist. Answer the following user query based on this chat history:\n\n{history_text}\n\nStyleMate:"

                response = model.generate_content(system_prompt)

                with st.chat_message("assistant"):
                    st.markdown(response.text)

                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

            except Exception as e:
                st.error(f"Error connecting to AI: {e}. Make sure your API key is valid.")

    # ---------------- SHOP SMARTER PAGE ----------------
    elif page == "Shop Smarter":
        st.title("🛍️ Shop Smarter")
        st.write("Plan your budget and instantly search across top stores with your price limit applied.")

        gender = st.radio("Gender", ["Women", "Men", "Unisex"], horizontal=True)
        category = st.selectbox("What do you want to buy?",
                                ["T-shirt", "Jeans", "Dress", "Kurti", "Sneakers", "Handbag", "Jewellery"])

        col1, col2 = st.columns(2)

        jewellery_type = ""
        jewellery_finish = ""
        colour = "Any"

        with col1:
            budget = st.slider("Maximum Budget (₹)", 200, 10000, 1500, step=100)

        with col2:
            if category == "Jewellery":
                jewellery_type = st.selectbox("Which Ornament?",
                                              ["Earrings", "Pendant", "Necklace", "Bracelet", "Ring", "Anklet"])
                jewellery_finish = st.selectbox("Metal / Finish",
                                                ["Silver", "Gold", "Rose Gold", "Anti-tarnish", "Oxidised", "Diamond",
                                                 "Pearl"])
            else:
                colour = st.selectbox("Preferred Colour",
                                      ["Any", "Black", "White", "Blue", "Beige", "Red", "Pastel", "Printed"])

        st.markdown("<br>", unsafe_allow_html=True)

        col_empty1, col_btn, col_empty2 = st.columns([1, 2, 1])
        with col_btn:
            create_plan = st.button("✨ CREATE SHOPPING PLAN", use_container_width=True)

        if create_plan:
            st.session_state.shop_plan = {
                "gender": gender,
                "category": category,
                "budget": budget,
                "colour": colour,
                "jewellery_type": jewellery_type,
                "jewellery_finish": jewellery_finish
            }

        if st.session_state.shop_plan:
            plan = st.session_state.shop_plan

            st.markdown("### 🛒 Direct Shopping Links")

            gender_prefix = f"{plan['gender']}'s" if plan['gender'] != "Unisex" else ""

            if plan['category'] == "Jewellery":
                base_query = f"{gender_prefix} {plan['jewellery_finish']} {plan['jewellery_type']} jewellery".strip()
                st.write(
                    f"Showing top platforms for **{plan['jewellery_finish']} {plan['jewellery_type']}** under **₹{plan['budget']}**:")
            else:
                color_str = plan['colour'] if plan['colour'] != "Any" else ""
                base_query = f"{gender_prefix} {color_str} {plan['category']}".strip()
                st.write(f"Showing top platforms for **{color_str} {plan['category']}** under **₹{plan['budget']}**:")

            encoded_query = urllib.parse.quote(base_query)
            price_query = urllib.parse.quote(f"{base_query} under {plan['budget']}")

            links = {
                "Myntra": f"https://www.myntra.com/{encoded_query}?rf=Price%3A0_{plan['budget']}",
                "Amazon": f"https://www.amazon.in/s?k={price_query}",
                "Flipkart": f"https://www.flipkart.com/search?q={encoded_query}&p%5B%5D=facets.price_range.from%3DMin&p%5B%5D=facets.price_range.to%3D{plan['budget']}",
                "Ajio": f"https://www.ajio.com/search/?text={price_query}",
                "Nykaa Fashion": f"https://www.nykaafashion.com/catalogsearch/result/?q={price_query}",
                "Tata CLIQ": f"https://www.tatacliq.com/search/?searchCategory=all&text={price_query}"
            }

            cat = plan['category']
            if cat == "Jewellery":
                links["Giva"] = f"https://www.giva.co/search?q={price_query}"
                links["CaratLane"] = f"https://www.caratlane.com/search?q={encoded_query}"
                links["Melorra"] = f"https://www.melorra.com/jewellery/?q={encoded_query}"
            elif cat == "Sneakers":
                links["VegNonVeg"] = f"https://www.vegnonveg.com/search?q={encoded_query}"
                links["Superkicks"] = f"https://www.superkicks.in/search?q={encoded_query}"
                links["Puma"] = f"https://in.puma.com/in/en/search?q={price_query}"
            elif cat in ["Kurti", "Dress"]:
                links["Biba"] = f"https://www.biba.in/search?q={price_query}"
                links["FabIndia"] = f"https://www.fabindia.com/search?q={encoded_query}"
                links["Libas"] = f"https://www.libas.in/search?q={price_query}"
            elif cat == "Handbag":
                links["Zouk"] = f"https://zouk.co.in/search?q={price_query}"
                links["Baggit"] = f"https://baggit.com/search?q={price_query}"
                links["Lavie"] = f"https://www.lavieworld.com/search?q={price_query}"
            else:
                links["H&M"] = f"https://www2.hm.com/en_in/search-results.html?q={encoded_query}"
                links["Zara"] = f"https://www.zara.com/in/en/search?searchTerm={encoded_query}"
                links["Max Fashion"] = f"https://www.maxfashion.in/in/en/search?q={price_query}"

            link_items = list(links.items())
            for i in range(0, len(link_items), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(link_items):
                        store_name, url = link_items[i + j]
                        cols[j].markdown(f"""
                        <div class='card' style='text-align:center; padding: 15px;'>
                            <a href='{url}' target='_blank' style='text-decoration:none; color:#2c2c2c; font-weight:bold; font-size: 16px;'>
                                🛍️ {store_name}
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

    # ---------------- SAVED LOOKS PAGE ----------------
    elif page == "Saved Looks":
        st.title("💖 Saved Looks")
        if not st.session_state.saved_looks:
            st.info("No saved looks yet! Go to Find My Outfit to save some.")
        else:
            for index, look in enumerate(st.session_state.saved_looks):
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <h3>✨ Look {index + 1}: {look['style']}</h3>
                        <p><b>Occasion:</b> {look['occasion']} | <b>Color:</b> {look['colour']}</p>
                        <p>{look['details']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🗑️ Remove", key=f"remove_{index}"):
                        st.session_state.saved_looks.pop(index)
                        st.rerun()

            if st.button("Clear All Saved Looks"):
                st.session_state.saved_looks = []
                st.rerun()