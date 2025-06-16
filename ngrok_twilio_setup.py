from pyngrok import ngrok
from twilio.rest import Client
import os
from dotenv import load_dotenv
import time
import sys

load_dotenv()

# Twilio credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Must be in E.164 format

# Start ngrok tunnel
public_url = ngrok.connect(8000, bind_tls=True).public_url
print(f"ngrok tunnel created: {public_url}")

# Construct full webhook URL
webhook_url = f"{public_url}/incoming_call"
print(f"Setting webhook to: {webhook_url}")

# Update Twilio webhook
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

phone_numbers = client.incoming_phone_numbers.list(phone_number=TWILIO_PHONE_NUMBER)
if not phone_numbers:
    raise Exception(f"No Twilio phone number found for {TWILIO_PHONE_NUMBER}")

phone_numbers[0].update(voice_url=webhook_url, voice_method="POST")
print("Twilio webhook updated successfully.")

# Keep tunnel alive if run directly
if __name__ == "__main__":
    print("ngrok tunnel is active. Press CTRL+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ngrok.kill()
        print("ngrok tunnel terminated.")
