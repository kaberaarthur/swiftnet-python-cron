import requests
import json

# Static API credentials and message content
API_KEY = "atsk_9cfc317182ef7086d1c0c7c4445f2a95fa4578a005917a45f5b9921539ae0fd1cde536d2"
USERNAME = "Swiftnet_sms"
MESSAGE = "Hello Arthur, your subscription has Expired. Visit https://swiftnet.co.ke/payment/2 to extend your subscription"
SENDER_ID = "SwiftKenya"

def send_sms(message, phone_numbers, masked_number=None, telco=None):
    print("The Message => ", message)
    print("The Phone Numbers => ", phone_numbers)

    url = "https://api.africastalking.com/version1/messaging/bulk"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "apiKey": API_KEY
    }
    
    payload = {
        "username": USERNAME,
        "message": message,
        "senderId": SENDER_ID,
        "phoneNumbers": phone_numbers
    }

    print("The Payload: ", payload)
    print("Headers: ", headers)
    
    if masked_number:
        payload["maskedNumber"] = masked_number
    
    if telco:
        payload["telco"] = telco
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("SMS Response: ", response.text)

    try:
        print("SMS Response:", response.json())
    except requests.exceptions.JSONDecodeError:
        print("SMS Response is not valid JSON:", response.text)

# send_sms("Hello System User your subscription has Expired. Visit https://swiftnet-fe.vercel.app/authentication/acustomer?id=225 to renew your subscription.", ['0790485731'])