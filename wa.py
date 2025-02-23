import requests
import json

def send_whatsapp_message(message, phone_number):
    #session="Swiffy"
    session="SwiftNetKen"
    
    # Base URL and headers
    url = "https://backend.payhero.co.ke/api/v2/whatspp/sendText"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eVB6ZjhMeGhJQkI4aWYwakR2R1Q6cUxKRHcxdmZHUWhhSEZ1MjhVVFJmcmpLazVZdlZFajA3TDVQcWVycQ=="
    }

    # Validate inputs
    if not message or not isinstance(message, str):
        raise ValueError("Message must be a non-empty string")
    if not phone_number or not isinstance(phone_number, str):
        raise ValueError("Phone number must be a non-empty string")
    if not isinstance(session, str):
        raise ValueError("Session must be a string")

    # Construct payload
    payload = {
        "message": message,
        "phone_number": phone_number,
        "session": session
    }

    try:
        # Make the POST request
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the response as a dictionary
        return response.json()
    
    except requests.RequestException as e:
        # Re-raise the exception with more context
        raise requests.RequestException(f"Failed to send WhatsApp message: {str(e)}") from e
    except json.JSONDecodeError:
        # Handle case where response isn't valid JSON
        raise ValueError("Invalid JSON response from server") from None

if __name__ == "__main__":
    # Example usage when running this file directly
    try:
        result = send_whatsapp_message("My First Text", "0790485731")
        print(json.dumps(result, indent=2))
    except (requests.RequestException, ValueError) as e:
        print(f"Error: {e}")