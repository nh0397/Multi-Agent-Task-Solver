"""
Test script for email functionality
"""
import os
from dotenv import load_dotenv
from tools.email import send_email, format_report_html

# Load environment variables
load_dotenv()

print("=" * 60)
print("EMAIL MODULE TEST")
print("=" * 60)

# Check if email is configured
email_user = os.getenv("EMAIL_USER")
email_password = os.getenv("EMAIL_PASSWORD")

if not email_user or not email_password:
    print("\n❌ Email not configured!")
    print("\nTo enable email, add to .env:")
    print("EMAIL_USER=your.email@gmail.com")
    print("EMAIL_PASSWORD=your_app_password")
    print("\nFor Gmail:")
    print("1. Enable 2FA at https://myaccount.google.com/security")
    print("2. Generate app password at https://myaccount.google.com/apppasswords")
    print("3. Use the 16-character app password (not your regular password)")
    exit(1)

print(f"\n✓ Email configured: {email_user}")
print(f"✓ SMTP: {os.getenv('EMAIL_HOST', 'smtp.gmail.com')}:{os.getenv('EMAIL_PORT', '587')}")

# Get recipient
recipient = input("\nEnter recipient email address: ").strip()
if not recipient:
    recipient = email_user  # Send to self as test

print(f"\n📧 Sending test email to: {recipient}")

# Create sample report
sample_content = """
**NVDA Stock Analysis**

Based on recent market data:

**Key Findings:**
- Stock price: $183.32 (as of Jan 21, 2026)
- 52-week range: $86.62 - $212.19
- Trading volume: 199.8M shares

**Important News:**
- NVIDIA CEO Jensen Huang says AI won't be the job killer everyone fears
- Tech stocks rally as Trump, NATO reach framework deal for Greenland

**Actionable Insights:**
- Stock showing moderate volatility
- Consider long-term hold for AI exposure
- Monitor upcoming earnings report
"""

sample_sources = [
    {"title": "NVDA Stock Quote - CNBC", "url": "https://www.cnbc.com/quotes/NVDA"},
    {"title": "NVIDIA Stock Analysis - Yahoo Finance", "url": "https://finance.yahoo.com/quote/NVDA"}
]

# Format as HTML
html_body = format_report_html(
    title="NVDA Stock Analysis Report",
    content=sample_content,
    sources=sample_sources
)

# Send email
print("\n⏳ Sending email...")
result = send_email(
    recipient=recipient,
    subject="Test: NVDA Stock Analysis Report",
    body=html_body,
    attachments=None  # No attachments for basic test
)

print(f"\n{result}")

if "successfully" in result.lower() or "sent" in result.lower():
    print("\n✅ Email test PASSED!")
    print(f"Check {recipient} inbox for the test email.")
else:
    print("\n❌ Email test FAILED!")
    print("\nCommon issues:")
    print("- Gmail: Make sure you're using an app password, not your regular password")
    print("- 2FA: Must be enabled for Gmail app passwords")
    print("- Less secure apps: Not needed if using app password")
