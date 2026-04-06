import xmlrpc.client
import socket
import os
from dotenv import load_dotenv

load_dotenv('.env')

print("=" * 50)
print("AI EMPLOYEE -- PRE-DEMO CONNECTION CHECK")
print("=" * 50)

# Odoo
try:
    c = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
    uid = c.authenticate(
        os.environ.get('ODOO_DB', ''),
        os.environ.get('ODOO_LOGIN', ''),
        os.environ.get('ODOO_PASSWORD', ''),
        {}
    )
    print(f"Odoo:              OK  (uid={uid}, db={os.environ.get('ODOO_DB')})")
except Exception as e:
    print(f"Odoo:              FAIL  ({e})")

# SMTP
try:
    s = socket.create_connection(('smtp.gmail.com', 587), timeout=5)
    s.close()
    print("SMTP (Gmail):      OK  (smtp.gmail.com:587 reachable)")
except Exception as e:
    print(f"SMTP (Gmail):      FAIL  ({e})")

# Social Media env vars
for key, label in [
    ('FACEBOOK_ACCESS_TOKEN',  'Facebook Token  '),
    ('FACEBOOK_PAGE_ID',            'Facebook Page ID'),
    ('INSTAGRAM_ACCOUNT_ID',            'Instagram UserID'),
    ('TWITTER_API_KEY',       'Twitter API Key '),
    ('TWITTER_API_SECRET',    'Twitter Secret  '),
    ('TWITTER_ACCESS_TOKEN',  'Twitter Acc Tok '),
    ('TWITTER_ACCESS_SECRET', 'Twitter Acc Sec '),
]:
    val = os.environ.get(key, '')
    status = 'SET' if val else 'MISSING'
    print(f"{label}:  {status}")

dry_run = os.environ.get('SOCIAL_DRY_RUN', 'false')
print(f"SOCIAL_DRY_RUN:      {dry_run}")

# Gmail / SMTP
smtp_user = os.environ.get('SMTP_USER', '')
print(f"SMTP_USER (Gmail):   {smtp_user if smtp_user else 'MISSING'}")

print("=" * 50)
