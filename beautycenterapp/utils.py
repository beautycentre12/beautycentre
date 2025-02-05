import plivo
from BeautyCenter import settings

def send_whatsapp_message(phone_number, message_body):
    """Function to send OTP via SMS using Plivo"""
    client = plivo.RestClient(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)

    try:
        response = client.messages.create(
            src=settings.SENDER_PHONE_NUMBER,  # Your verified Plivo phone number
            dst=f'+91{phone_number}',  # Assuming Indian numbers
            text=message_body,
        )
        return response
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return None
