import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import re

# ─────────────────────────────────────────
# Google Sheets Connection
# ─────────────────────────────────────────
CREDENTIALS_PATH = 'credentials.json'
SHEET_ID         = '1bPgYjBtf4Rx7dcXueF4TrOZZaGsq8BBcXZDk63L28bs'

@st.cache_resource
@st.cache_resource
def connect_to_sheets():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    # Use Streamlit secrets when deployed, local file when running locally
    try:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=scope
        )
    except:
        creds = Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=scope
        )
    client = gspread.authorize(creds)
    book = client.open_by_key(SHEET_ID)
    return book.sheet1, book.worksheet('users_sheet')


def get_all_reviews(reviews_sheet):
    """Get all reviews from Sheet 1."""
    try:
        data = reviews_sheet.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def get_staff_users(users_sheet):
    """Get all staff users from Sheet 2."""
    try:
        data = users_sheet.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def authenticate_user(users_sheet, username, password):
    """
    Check username and password against Sheet 2.
    Returns user info dict if valid, None if invalid.
    """
    try:
        df = get_staff_users(users_sheet)
        if df.empty:
            return None
        user = df[
            (df['Username'].str.strip() == username.strip()) &
            (df['Password'].astype(str).str.strip() == password.strip())
        ]
        if len(user) > 0:
            return {
                'username'   : user.iloc[0]['Username'],
                'department' : user.iloc[0]['Department'],
                'full_name'  : user.iloc[0]['Full Name']
            }
        return None
    except Exception:
        return None


def check_duplicate(reviews_sheet, email, product_category):
    """Check if email has already reviewed this product category."""
    try:
        df = get_all_reviews(reviews_sheet)
        if df.empty:
            return False
        if 'Email' in df.columns and 'Product Category' in df.columns:
            duplicate = df[
                (df['Email'].astype(str).str.strip().str.lower()
                 == email.strip().lower()) &
                (df['Product Category'].astype(str).str.strip()
                 == product_category.strip())
            ]
            return len(duplicate) > 0
        return False
    except Exception:
        return False


def save_to_sheet(reviews_sheet, data):
    """Append a new review row to Sheet 1."""
    try:
        reviews_sheet.append_row(list(data.values()))
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False


def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ─────────────────────────────────────────
# Product Groups
# ─────────────────────────────────────────
product_groups = [
    'Electronics & Technology',
    'Home & Living',
    'Beauty & Personal Care',
    'Fashion & Accessories',
    'Sports & Leisure',
    'Kids & Baby',
    'Automotive',
    'Construction & Tools',
    'Food & Beverage',
    'Pet Supplies',
    'Business & Office',
    'Lifestyle & Entertainment',
    'Other / Not Listed'
]

# ─────────────────────────────────────────
# Region Mapping
# ─────────────────────────────────────────
core_market_states = ['SP', 'RJ', 'MG']

brazilian_states = [
    '-- Select your state --',
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
    'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
    'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

def assign_region(state):
    if state in core_market_states:
        return 'Region A / Core Market'
    return 'Region B / Expansion Market'


# ─────────────────────────────────────────
# Department Routing
# ─────────────────────────────────────────
department_routing = {
    'Delivery & Shipping'  : 'Logistics Team',
    'Wrong Item Received'  : 'Warehouse Team',
    'Missing Item'         : 'Warehouse Team',
    'Product Quality'      : 'Supplier Relations Team',
    'Customer Service'     : 'Customer Support Team',
    'Payment & Refund'     : 'Finance Team',
    'Returns & Exchange'   : 'Customer Support Team',
    'Packaging'            : 'Warehouse Team',
    'General Positive'     : 'No Action Required',
    'General Negative'     : 'Customer Support Team',
    'No Comment'           : 'No Action Required',
    'Other'                : 'Customer Support Team'
}

# ─────────────────────────────────────────
# Theme Keywords
# ─────────────────────────────────────────
theme_keywords = {
    'Delivery & Shipping': [
        'delivery', 'delivered', 'shipping', 'arrived', 'deadline',
        'fast', 'quick', 'late', 'delayed', 'on time', 'early', 'before',
        'didn\'t deliver', 'not deliver', 'haven\'t received', 'not received yet',
        'waiting', 'correios', 'tracking', 'distribution', 'send it',
        'bought in one day', 'received the next day', 'didn\'t arrive',
        'delay', 'more than a month', 'no update', 'days to arrive', 'punctual',
        'took a long time', 'long time to deliver', 'coming from china',
        'still in the hands', 'courier', 'will the product still arrive',
        'when will i receive', 'sent to the south', 'track the order',
        'can\'t track', 'still on schedule', 'too long', 'strike',
        'truck drivers', 'received the product days after',
        'slow to arrive', 'simply didn\'t deliver',
        'where is it', 'i want my product', 'i need to receive',
        'more than 30 days', 'just doesn\'t deliver',
        'transport company informed', 'was away from home',
        'i don\'t have the product in hand', 'carrier',
        'scheduled date', 'took a while', 'long overdue',
        'took so long to receive', 'received it ahead of schedule',
        'a month to arrive', 'never taken so long',
        'takes time to deliver', 'agility makes a difference'
    ],
    'Product Quality': [
        'quality', 'perfect', 'defective', 'broken', 'original',
        'falsified', 'exceeded', 'expectations', 'fragrant', 'beautiful',
        'condition', 'works', 'working', 'damaged', 'fragile',
        'fake', 'counterfeit', 'unsealed', 'empty', 'without ink',
        'didn\'t work', 'did not work', 'factory defect',
        'not what i thought', 'product does not work',
        'well finished', 'very useful', 'easy to use',
        'leaves a lot to be desired', 'very weak product',
        'could improve', 'material lower than expected'
    ],
    'Wrong Item Received': [
        'wrong', 'different', 'another color', 'not the product',
        'sent was not', 'wrong product', 'wrong size', 'wrong color',
        'not as advertised', 'not what i bought',
        'description does not match', 'false advertising',
        'i ordered one product and received another',
        'product in the photo is not the same',
        'does not correspond to what is advertised',
        'bought liquid and it came with pills',
        'deceived by a product similar'
    ],
    'Packaging': [
        'packaging', 'packed', 'separate box', 'wasteful',
        'wrapped', 'package'
    ],
    'Customer Service': [
        'seller', 'service', 'attended', 'response', 'support',
        'respect', 'rude', 'helpful', 'trustworthy',
        'seriousness', 'efficiency', 'attentive',
        'no one sent', 'no explanation', 'difficult to contact',
        'can\'t contact you', 'do not respond to requests'
    ],
    'Missing Item': [
        'missing', 'only received', 'incomplete', 'not received',
        'didn\'t receive', 'did not come', 'only gave me',
        'only send one', 'no product', 'i did not receive the product',
        'no invoice came', 'only sent me one', 'partial'
    ],
    'Payment & Refund': [
        'refund', 'charge', 'card', 'installment', 'money', 'paid',
        'payment', 'resolve', 'refund request', 'canceled the order',
        'need to be reimbursed', 'should be cheaper', 'contact procon'
    ],
    'Returns & Exchange': [
        'exchange', 'return', 'asked for an exchange',
        'want to return', 'send back', 'cancel this purchase',
        'i want to make the change'
    ],
    'General Positive': [
        'recommend', 'excellent', 'satisfied', 'love', 'great product',
        'happy', 'amazing', 'wonderful', 'liked', 'congratulations',
        'thank', 'very good', 'good purchase', 'will buy again',
        'never had a problem', 'fantastic', 'sensational',
        'fulfilled what was promised', 'exactly what i needed'
    ],
    'General Negative': [
        'terrible', 'worst', 'disappointed', 'horrible', 'awful',
        'useless', 'waste', 'never again', 'rubbish', 'don\'t buy',
        'will never buy', 'bad purchase', 'absurd', 'frustration',
        'regretted', 'dissatisfaction', 'leaves a lot to be desired'
    ],
    'No Comment': [
        'okay', 'no comments', 'no information', 'ok.'
    ]
}


# ─────────────────────────────────────────
# Sentiment Functions
# ─────────────────────────────────────────
def classify_theme(text):
    if not text or str(text).strip() == '':
        return 'No Comment'
    if len(str(text).strip()) <= 2:
        return 'No Comment'
    text_lower = str(text).lower()
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return theme
    return 'Other'


def get_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    scores   = analyzer.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= 0.05:
        label = 'Positive 😊'
    elif compound <= -0.05:
        label = 'Negative 😟'
    else:
        label = 'Neutral 😐'
    return label, round(compound, 4)


def get_sentiment_strength(score):
    if score >= 0.6:
        return 'Strong Positive'
    elif score >= 0.05:
        return 'Mild Positive'
    elif score > -0.05:
        return 'Neutral'
    elif score > -0.3:
        return 'Mild Negative'
    elif score > -0.6:
        return 'Moderate Negative'
    else:
        return 'Strong Negative'


# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Olist Customer Feedback",
    page_icon="🛒",
    layout="centered"
)

# ─────────────────────────────────────────
# Session State
# ─────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in   = False
if 'user_info' not in st.session_state:
    st.session_state.user_info   = None


# ─────────────────────────────────────────
# App Layout — Tabs
# ─────────────────────────────────────────
tab1, tab2 = st.tabs(["📝 Submit a Review", "🔐 Staff Dashboard"])


# ─────────────────────────────────────────
# TAB 1 — Customer View
# ─────────────────────────────────────────
with tab1:
    st.title("🛒 Customer Feedback")
    st.write("We value your feedback. Please share your experience with us.")

    st.markdown("#### 👤 Your Information")
    col1, col2 = st.columns(2)
    with col1:
        customer_name  = st.text_input(
            "Full Name *",
            placeholder="e.g. John Smith"
        )
        customer_email = st.text_input(
            "Email Address *",
            placeholder="e.g. john@gmail.com",
            help="Must be a valid email — e.g. name@domain.com"
        )
    with col2:
        customer_phone = st.text_input(
            "Phone Number (optional)",
            placeholder="e.g. +55 11 99999-9999"
        )
        customer_state = st.selectbox(
            "Your State *",
            options=brazilian_states
        )

    st.markdown("#### 🛍️ Your Review")
    product_group = st.selectbox(
        "Product Category *",
        options=["-- Select a category --"] + product_groups
    )

    review_input = st.text_area(
        "Your Review *",
        height=150,
        placeholder="Tell us about your experience..."
    )

    if st.button("📨 Submit Feedback"):
        errors = []
        if not customer_name.strip():
            errors.append("Full name is required.")
        if not customer_email.strip():
            errors.append("Email address is required.")
        elif not validate_email(customer_email):
            errors.append("Please enter a valid email (e.g. name@domain.com).")
        if customer_state == '-- Select your state --':
            errors.append("Please select your state.")
        if product_group == "-- Select a category --":
            errors.append("Please select a product category.")
        if not review_input.strip():
            errors.append("Please write your review.")

        if errors:
            for error in errors:
                st.warning(error)
        else:
            try:
                reviews_sheet, users_sheet = connect_to_sheets()

                if check_duplicate(reviews_sheet, customer_email, product_group):
                    st.info(
                        f"📋 We have already received your review for "
                        f"**{product_group}**. Thank you for your continued "
                        f"interest! If you have a different concern, please "
                        f"contact us directly."
                    )
                else:
                    theme           = classify_theme(review_input)
                    sentiment_label, sentiment_score = get_sentiment(review_input)
                    strength        = get_sentiment_strength(sentiment_score)
                    department      = department_routing.get(theme, 'Customer Support Team')
                    region          = assign_region(customer_state)
                    timestamp       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    review_data = {
                        'Timestamp'        : timestamp,
                        'Name'             : customer_name,
                        'Email'            : customer_email,
                        'Phone'            : customer_phone if customer_phone else 'N/A',
                        'State'            : customer_state,
                        'Region'           : region,
                        'Product Category' : product_group,
                        'Review'           : review_input,
                        'Theme'            : theme,
                        'Sentiment'        : sentiment_label,
                        'Strength'         : strength,
                        'Score'            : sentiment_score,
                        'Department'       : department
                    }

                    if save_to_sheet(reviews_sheet, review_data):
                        st.success(
                            "✅ Thank you! Your feedback has been received. "
                            "We will contact you soon if needed."
                        )

            except Exception as e:
                st.error(f"Connection error: {e}")


# ─────────────────────────────────────────
# TAB 2 — Staff Dashboard
# ─────────────────────────────────────────
with tab2:

    # ── Login Form ──
    if not st.session_state.logged_in:
        st.title("🔐 Staff Login")
        st.write("This area is restricted to authorized staff only.")

        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", placeholder="e.g. logistics.staff")
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("🔑 Login"):
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                try:
                    reviews_sheet, users_sheet = connect_to_sheets()
                    user = authenticate_user(users_sheet, username, password)

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = user
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # ── Staff Dashboard ──
    else:
        user_info  = st.session_state.user_info
        department = user_info['department']
        full_name  = user_info['full_name']

        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("📊 Staff Review Dashboard")
            st.write(f"Welcome, **{full_name}** | Department: **{department}**")
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.rerun()

        try:
            reviews_sheet, users_sheet = connect_to_sheets()
            df = get_all_reviews(reviews_sheet)

            if df.empty:
                st.info("No reviews submitted yet.")
            else:
                # ── Role-based filtering ──
                if department != 'All':
                    df = df[df['Department'] == department].copy()

                if df.empty:
                    st.info(f"No reviews for {department} yet.")
                else:
                    # ── Summary Metrics ──
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Reviews", len(df))
                    with col2:
                        positive = len(df[df['Sentiment'].astype(str)
                                         .str.contains('Positive', na=False)])
                        st.metric("Positive 😊", positive)
                    with col3:
                        negative = len(df[df['Sentiment'].astype(str)
                                         .str.contains('Negative', na=False)])
                        st.metric("Negative 😟", negative)
                    with col4:
                        neutral = len(df[df['Sentiment'].astype(str)
                                        .str.contains('Neutral', na=False)])
                        st.metric("Neutral 😐", neutral)

                    st.markdown("---")

                    # ── Filters ──
                    st.subheader("🔍 Filter Reviews")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_region = st.selectbox(
                            "Filter by Region",
                            options=['All'] + sorted(
                                df['Region'].dropna().unique().tolist()
                            )
                        )
                    with col2:
                        filter_sentiment = st.selectbox(
                            "Filter by Sentiment",
                            options=['All'] + sorted(
                                df['Sentiment'].dropna().unique().tolist()
                            )
                        )
                    with col3:
                        filter_theme = st.selectbox(
                            "Filter by Theme",
                            options=['All'] + sorted(
                                df['Theme'].dropna().unique().tolist()
                            )
                        )

                    # ── Apply Filters ──
                    filtered_df = df.copy()
                    if filter_region != 'All':
                        filtered_df = filtered_df[
                            filtered_df['Region'] == filter_region
                        ]
                    if filter_sentiment != 'All':
                        filtered_df = filtered_df[
                            filtered_df['Sentiment'] == filter_sentiment
                        ]
                    if filter_theme != 'All':
                        filtered_df = filtered_df[
                            filtered_df['Theme'] == filter_theme
                        ]

                    st.markdown(
                        f"Showing **{len(filtered_df)}** of **{len(df)}** reviews"
                    )

                    # ── Review Table ──
                    st.subheader("📋 Review Details")
                    st.dataframe(filtered_df, use_container_width=True)

                    # ── Download Button ──
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download Report (CSV)",
                        data=csv,
                        file_name=(
                            f"{department.replace(' ', '_')}_reviews_"
                            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        ),
                        mime='text/csv'
                    )

        except Exception as e:
            st.error(f"Could not load reviews: {e}")
