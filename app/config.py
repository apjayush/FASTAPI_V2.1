import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# WhatsApp Configuration
WHATSAPP_TOKEN=os.getenv("WHATSAPP_TOKEN").strip()
PHONE_NUMBER_ID=os.getenv("PHONE_NUMBER_ID").strip()
DB_SCHEMA=os.getenv("DB_SCHEMA","public").strip()