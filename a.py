import requests
from datetime import datetime, timezone
import logging
import pytz
from sms import send_sms
from wa import send_whatsapp_message

print("Start Here!")

# Define the API endpoint
API_URL = "http://localhost:8000/pppoe-clients"

# Set up logging configuration
logging.basicConfig(
    filename="ppp_secret_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - Router = %(message)s"
)


def manage_ppp_secret(router, command, secret_name, customer_id):
    try:
        # Define the API endpoint
        url = "http://localhost:3001/api/end_subscription"

        # Add parameters to the request
        data = {
            "router": router,
            "command": command,
            "secret_name": secret_name,
            "customer_id": customer_id,
        }

        response = requests.post(url, json=data)

        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Check for unsuccessful response and log an error if any
        if response.status_code != 200:
            error_message = (
                f"Router = {router} | Error: Received status code {response.status_code} - {response.text}"
            )
            logging.error(error_message)

    except Exception as e:
        error_message = f"Router = {router} | Exception occurred: {str(e)}"
        logging.error(error_message)
        print(f"An error occurred: {error_message}")



def update_reminder_status(client_id, status):
    # API endpoint URL (adjust based on your server host/port)
    url = f"http://localhost:8000/reminder/{client_id}"
    

    # Payload for the PUT request
    payload = {
        "status": status
    }

    try:
        # Make the PUT request
        response = requests.patch(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10  # Set a timeout to avoid hanging
        )

        # Check if the request was successful
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes

        # Log success
        logging.info(f"Successfully updated reminder status for client_id {client_id} to {status}: {response.json()}")
        print(f"Updated reminder status for client_id {client_id} to {status}")
        return True

    except requests.exceptions.Timeout:
        logging.error(f"Timeout updating reminder status for client_id {client_id}")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to update reminder status for client_id {client_id}: {e} - {response.text if 'response' in locals() else 'No response'}")
        return False



def fetch_pppoe_clients():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.json()
    except requests.RequestException as e:
        error_message = f"Error fetching data: {str(e)}"
        logging.error(error_message)
        print(error_message)
        return []


def check_expired_clients():
    clients = fetch_pppoe_clients()
    if not clients:
        print("No data retrieved.")
        return

    # Get Nairobi timezone
    nairobi_tz = pytz.timezone("Africa/Nairobi")

    # Get the current time in Nairobi
    current_time = datetime.now(nairobi_tz)

    for client in clients:
        if client.get("active") == 1:  # Only check active clients
            end_date_str = client.get("end_date")
            if end_date_str:
                try:
                    # Convert string to datetime and localize to Nairobi timezone
                    end_date = datetime.fromisoformat(end_date_str.rstrip("Z"))
                    end_date = nairobi_tz.localize(end_date)

                    # Calculate the difference between end_date and current_time
                    time_difference = end_date - current_time
                    days_difference = time_difference.days

                    client_id = int(client.get("id"))

                    # Check for imminent expiry (2–3 days remaining) and reminder flag
                    if client.get("reminder") == 1 and 2 <= days_difference <= 5:
                    #if client.get("reminder") == 1 and 2 <= days_difference <= 3 and client_id == 225:
                        print("Remind User: ", client.get("full_name"), "of ID - ", client.get("id"))
                        print("User End Date: ", client.get("end_date"))
                        # Send WhatsApp reminder for imminent expiry
                        send_whatsapp_message(
                            f"Hello {client['full_name']},\n\n"
                            f"Your home fiber subscription is nearing its expiry date ({end_date.strftime('%Y-%m-%d')}). "
                            f"To avoid disconnection, please renew your subscription within the next {days_difference} days by visiting:\n\n"
                            f"Renew Here 👉 https://swiftnet-fe.vercel.app/authentication/acustomer?id={client['id']}\n\n"
                            f"Stay connected with fast and reliable internet. Need assistance? Visit the link above to view our contacts.",
                            client["phone_number"]
                        )
                        print(f"Sent reminder to {client['full_name']} - {days_difference} days until expiry")

                        # Update the reminder field to 0 to prevent resending
                        update_reminder_status(client["id"], 'disable')

                    # Check for expired clients
                    if end_date < current_time:
                        print(
                            f"manage_ppp_secret({client['router_id']}, 'disable', '{client['secret']}', {client['id']})"
                        )
                        manage_ppp_secret(client["router_id"], "disable", client["secret"], client["id"])

                        send_whatsapp_message(
                            f"Hello {client['full_name']},\n\n"
                            f"Your Swiftnet home fiber subscription has been temporarily disconnected due to non-payment. "
                            f"To restore your service, please renew your subscription by visiting:\n\n"
                            f"Renew Here 👉 https://swiftnet-fe.vercel.app/authentication/acustomer?id={client['id']}\n\n"
                            f"Stay connected with fast and reliable internet. Need assistance? Visit the link above to view our contacts.",
                            client["phone_number"]
                        )
                        print(f"Disconnected and notified {client['full_name']} - expired on {end_date}")

                except ValueError:
                    error_message = (
                        f"Router => {client.get('router_id', 'Unknown')} | Invalid date format for client {client.get('full_name', 'Unknown')}: {end_date_str}"
                    )
                    logging.error(error_message)
                    print(error_message)


if __name__ == "__main__":
    check_expired_clients()
