import requests
from datetime import datetime, timezone
import logging
import pytz

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
                    end_date = datetime.fromisoformat(end_date_str.rstrip("Z"))  # Convert string to datetime
                    # Assign the Nairobi timezone to end_date
                    end_date = nairobi_tz.localize(end_date)

                    if end_date < current_time:
                        print(
                            f"manage_ppp_secret({client['router_id']}, 'disable', '{client['secret']}', {client['id']})"
                        )
                        manage_ppp_secret(client["router_id"], "disable", client["secret"], client["id"])

                except ValueError:
                    error_message = (
                        f"Router = {client.get('router_id', 'Unknown')} | Invalid date format for client {client.get('full_name', 'Unknown')}: {end_date_str}"
                    )
                    logging.error(error_message)
                    print(error_message)


if __name__ == "__main__":
    check_expired_clients()
