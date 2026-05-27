# =============================================================================
# PROJECT   : Olist Customer Experience Intelligence
# FILE      : email_alerts.py
# PURPOSE   : Weekly department reports + spike alert notifications
# AUTHOR    : Maeen Mohammed
# =============================================================================

import gspread
import pandas as pd
import smtplib
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
CREDENTIALS_PATH  = 'credentials.json'
SHEET_ID          = '1bPgYjBtf4Rx7dcXueF4TrOZZaGsq8BBcXZDk63L28bs'

# Sender email
SENDER_EMAIL      = 'moeen.gama@gmail.com'
SENDER_PASSWORD   = 'pjjr rlmo cuou seun'

# Streamlit App URL
APP_URL = 'https://olist-customer-intelligence-5b2dopipfmaatguqumxrjz.streamlit.app'

# Department email routing
DEPARTMENT_EMAILS = {
    'Logistics Team'          : 'olist.logistics@gmail.com',
    'Warehouse Team'          : 'maeenmohammed2027@gmail.com',
    'Finance Team'            : 'moeen.gama@gmail.com',
    'Customer Support Team'   : 'maeenmohammed2027@gmail.com',
    'Supplier Relations Team' : 'moeen.gama@gmail.com',
    'No Action Required'      : None
}

# Alert thresholds
WARNING_THRESHOLD  = 3
HIGH_THRESHOLD     = 5
CRITICAL_THRESHOLD = 10


# ─────────────────────────────────────────
# Google Sheets Connection
# ─────────────────────────────────────────
def connect_to_sheet():
    """Connect to Google Sheets and return the reviews sheet."""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds  = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1


def get_all_reviews():
    """Load all reviews from Google Sheets into a DataFrame."""
    sheet = connect_to_sheet()
    data  = sheet.get_all_records()
    if not data:
        print("No reviews found in sheet.")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df


# ─────────────────────────────────────────
# Email Sending
# ─────────────────────────────────────────
def send_email(to_email, subject, body):
    """
    Send an HTML email without attachment.
    Staff access data securely through the app.

    Args:
        to_email : Recipient email address
        subject  : Email subject line
        body     : Email body (HTML)
    """
    try:
        msg            = MIMEMultipart()
        msg['From']    = SENDER_EMAIL
        msg['To']      = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email} — {subject}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False


# ─────────────────────────────────────────
# Weekly Department Reports
# ─────────────────────────────────────────
def send_weekly_reports():
    """
    Generate and send weekly review reports to each department.
    Filters reviews from the last 7 days, groups by department,
    and sends a formatted email with a secure link to the Staff Dashboard.
    """
    print(f"\n{'='*60}")
    print(f"WEEKLY REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    df = get_all_reviews()
    if df.empty:
        print("No reviews to report.")
        return

    # Filter last 7 days
    last_7_days = datetime.now() - timedelta(days=7)
    weekly_df   = df[df['Timestamp'] >= last_7_days].copy()

    if weekly_df.empty:
        print("No reviews in the last 7 days.")
        return

    print(f"Total reviews this week: {len(weekly_df)}")

    for department, email in DEPARTMENT_EMAILS.items():
        if email is None:
            continue

        dept_df = weekly_df[weekly_df['Department'] == department].copy()

        if dept_df.empty:
            print(f"No reviews for {department} this week — skipping.")
            continue

        # Calculate stats
        total      = len(dept_df)
        positive   = len(dept_df[dept_df['Sentiment'].str.contains('Positive', na=False)])
        negative   = len(dept_df[dept_df['Sentiment'].str.contains('Negative', na=False)])
        neutral    = len(dept_df[dept_df['Sentiment'].str.contains('Neutral',  na=False)])
        top_theme  = dept_df['Theme'].value_counts().index[0] if not dept_df.empty else 'N/A'
        top_region = dept_df['Region'].value_counts().index[0] if not dept_df.empty else 'N/A'

        # Category breakdown
        category_breakdown = dept_df['Product Category'].value_counts()
        category_rows = ''.join([
            f"""
            <tr style="background-color: {'#f2f2f2' if i % 2 == 0 else 'white'};">
                <td style="padding: 8px; border: 1px solid #ddd;">{cat}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{cnt}</td>
            </tr>
            """
            for i, (cat, cnt) in enumerate(category_breakdown.items())
        ])

        subject = (
            f"📊 Weekly Review Report — {department} — "
            f"Week of {last_7_days.strftime('%d %b %Y')}"
        )

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">

            <h2 style="color: #2196F3;">📊 Weekly Customer Review Report</h2>
            <p><strong>Department:</strong> {department}</p>
            <p><strong>Period:</strong> {last_7_days.strftime('%d %b %Y')}
               to {datetime.now().strftime('%d %b %Y')}</p>

            <hr>

            <h3>📈 Summary</h3>
            <table style="border-collapse: collapse; width: 50%;">
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Total Reviews</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{total}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>😊 Positive</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: green;">
                        {positive}
                    </td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>😟 Negative</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: red;">
                        {negative}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>😐 Neutral</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{neutral}</td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>🏷️ Top Theme</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{top_theme}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>📍 Most Affected Region</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{top_region}</td>
                </tr>
            </table>

            <br>

            <h3>🛍️ Breakdown by Product Category</h3>
            <table style="border-collapse: collapse; width: 50%;">
                <tr style="background-color: #2196F3; color: white;">
                    <th style="padding: 8px; border: 1px solid #ddd;">
                        Product Category
                    </th>
                    <th style="padding: 8px; border: 1px solid #ddd;">
                        Reviews
                    </th>
                </tr>
                {category_rows}
            </table>

            <br>
            <hr>

            <h3>🔐 Access Full Report</h3>
            <p>
                To view and download the complete review list,
                please log in to the Staff Dashboard:
            </p>
            <p>
                <a href="{APP_URL}"
                   style="background-color: #2196F3; color: white;
                          padding: 12px 24px; text-decoration: none;
                          border-radius: 5px; font-weight: bold;
                          display: inline-block;">
                    👉 Access Staff Dashboard
                </a>
            </p>
            <p style="color: #999; font-size: 12px;">
                Use your department credentials to log in and
                filter or download your department's reviews.
            </p>

            <hr>
            <p style="color: #999; font-size: 12px;">
                This is an automated report generated by the
                Olist Customer Experience Intelligence System.<br>
                Generated on {datetime.now().strftime('%d %b %Y at %H:%M')}
            </p>

        </body>
        </html>
        """

        send_email(email, subject, body)

    print("\n✅ Weekly reports completed.")


# ─────────────────────────────────────────
# Spike Alert Detection
# ─────────────────────────────────────────
def check_spike_alerts():
    """
    Check for negative review spikes in the last 24 hours.
    Groups by Theme + Department only (regardless of product category).
    Sends one alert per department per theme with category breakdown inside.

    Alert levels:
        🟡 Warning  : 3+ negatives same theme in 24hrs
        🟠 High     : 5+ negatives same theme in 24hrs
        🔴 Critical : 10+ negatives same theme in 24hrs
    """
    print(f"\n{'='*60}")
    print(f"SPIKE CHECK — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    df = get_all_reviews()
    if df.empty:
        print("No reviews to check.")
        return

    # Filter last 24 hours
    last_24_hours = datetime.now() - timedelta(hours=24)
    recent_df     = df[df['Timestamp'] >= last_24_hours].copy()

    if recent_df.empty:
        print("No reviews in last 24 hours.")
        return

    # Filter negative reviews only
    negative_df = recent_df[
        recent_df['Sentiment'].str.contains('Negative', na=False)
    ].copy()

    if negative_df.empty:
        print("No negative reviews in last 24 hours — all clear! ✅")
        return

    # Group by Theme + Department only
    spike_groups = negative_df.groupby(
        ['Theme', 'Department']
    ).size().reset_index(name='count')

    alerts_sent = 0

    for _, row in spike_groups.iterrows():
        count      = row['count']
        theme      = row['Theme']
        department = row['Department']
        email      = DEPARTMENT_EMAILS.get(department)

        if email is None:
            continue

        # Determine alert level
        if count >= CRITICAL_THRESHOLD:
            level  = '🔴 CRITICAL'
            color  = '#FF0000'
            action = 'IMMEDIATE action required.'
        elif count >= HIGH_THRESHOLD:
            level  = '🟠 HIGH'
            color  = '#FF6600'
            action = 'Urgent review required.'
        elif count >= WARNING_THRESHOLD:
            level  = '🟡 WARNING'
            color  = '#FFA500'
            action = 'Please monitor closely.'
        else:
            continue

        # Filter reviews for this spike
        spike_df = negative_df[
            (negative_df['Theme']      == theme) &
            (negative_df['Department'] == department)
        ].copy()

        # Category breakdown
        category_breakdown = spike_df['Product Category'].value_counts()
        category_rows = ''.join([
            f"""
            <tr style="background-color: {'#f2f2f2' if i % 2 == 0 else 'white'};">
                <td style="padding: 8px; border: 1px solid #ddd;">{cat}</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: red;">
                    {cnt}
                </td>
            </tr>
            """
            for i, (cat, cnt) in enumerate(category_breakdown.items())
        ])

        # Most affected region
        top_region = spike_df['Region'].value_counts().index[0] \
            if not spike_df.empty else 'N/A'

        subject = (
            f"{level} Alert: {count} negative {theme} reviews "
            f"in last 24 hours — {department}"
        )

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">

            <h2 style="color: {color};">{level} — Negative Review Spike Detected</h2>

            <table style="border-collapse: collapse; width: 60%;">
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Alert Level</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: {color};">
                        <strong>{level}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Theme</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{theme}</td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Department</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{department}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Total Negative Reviews (24hrs)</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: red;">
                        <strong>{count}</strong>
                    </td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Most Affected Region</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{top_region}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <strong>Action Required</strong>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: {color};">
                        <strong>{action}</strong>
                    </td>
                </tr>
            </table>

            <br>

            <h3>🛍️ Breakdown by Product Category</h3>
            <table style="border-collapse: collapse; width: 50%;">
                <tr style="background-color: {color}; color: white;">
                    <th style="padding: 8px; border: 1px solid #ddd;">
                        Product Category
                    </th>
                    <th style="padding: 8px; border: 1px solid #ddd;">
                        Negative Reviews
                    </th>
                </tr>
                {category_rows}
            </table>

            <br>
            <hr>

            <h3>🔐 Access Full Report</h3>
            <p>
                To view and download the complete list of affected reviews,
                please log in to the Staff Dashboard:
            </p>
            <p>
                <a href="{APP_URL}"
                   style="background-color: {color}; color: white;
                          padding: 12px 24px; text-decoration: none;
                          border-radius: 5px; font-weight: bold;
                          display: inline-block;">
                    👉 Access Staff Dashboard
                </a>
            </p>
            <p style="color: #999; font-size: 12px;">
                Use your department credentials to log in and
                filter or download the affected reviews.
            </p>

            <hr>
            <p style="color: #999; font-size: 12px;">
                This is an automated alert from the
                Olist Customer Experience Intelligence System.<br>
                Generated on {datetime.now().strftime('%d %b %Y at %H:%M')}
            </p>

        </body>
        </html>
        """

        if send_email(email, subject, body):
            alerts_sent += 1

    if alerts_sent == 0:
        print("No spikes above threshold — all clear! ✅")
    else:
        print(f"\n⚠️ {alerts_sent} spike alert(s) sent.")


# ─────────────────────────────────────────
# Manual Test — Run immediately
# ─────────────────────────────────────────
def run_manual_test():
    """Run both reports immediately for testing."""
    print("\n🚀 Running manual test...")
    print("\n1. Sending weekly reports...")
    send_weekly_reports()
    print("\n2. Checking spike alerts...")
    check_spike_alerts()
    print("\n✅ Manual test complete!")


# ─────────────────────────────────────────
# Scheduler — Production mode
# ─────────────────────────────────────────
def run_scheduler():
    """
    Schedule automated runs:
    - Weekly report : Every Monday at 8:00 AM
    - Spike check   : Every 6 hours
    """
    print("🕐 Scheduler started...")
    print("Weekly reports : Every Monday at 08:00 AM")
    print("Spike checks   : Every 6 hours")
    print("Press Ctrl+C to stop\n")

    schedule.every().monday.at("08:00").do(send_weekly_reports)
    schedule.every(6).hours.do(check_spike_alerts)

    while True:
        schedule.run_pending()
        time.sleep(60)


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("Olist Customer Experience Intelligence")
    print("Email Alert System")
    print("─" * 40)
    print("1. Run manual test (sends emails now)")
    print("2. Start scheduler (runs automatically)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        run_manual_test()
    elif choice == "2":
        run_scheduler()
    else:
        print("Invalid choice. Running manual test by default...")
        run_manual_test()