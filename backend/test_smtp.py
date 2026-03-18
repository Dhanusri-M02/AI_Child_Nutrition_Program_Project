import sys
sys.path.append('.')
from utils import send_otp_email, generate_otp
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 SMTP Config Check:")
print(f"SERVER: {os.getenv('SMTP_SERVER')}")
print(f"PORT: {os.getenv('SMTP_PORT')}")
print(f"USER: {os.getenv('SMTP_USER')}")
print(f"PASSWORD: {'***' if os.getenv('SMTP_PASSWORD') else 'MISSING'}")
print(f"ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")

otp = generate_otp()
test_email = os.getenv('ADMIN_EMAIL', 'your-test@gmail.com')

print(f"\n📧 Sending test OTP '{otp}' to {test_email}...")
success = send_otp_email(test_email, otp)

if success:
    print("✅ EMAIL SENT SUCCESSFULLY - Check your inbox!")
else:
    print("❌ EMAIL FAILED - Check config & Gmail app password")
print("\n🔥 Now test Admin login in browser!")

