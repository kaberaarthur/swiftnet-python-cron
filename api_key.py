import base64

# Your API username and password
api_username = "yPzf8LxhIBB8if0jDvGT"
api_password = "qLJDw1vfGQhaHFu28UTRfrjKk5YvVEj07L5Pqerq"

# Concatenating username and password with a colon
credentials = f"{api_username}:{api_password}"

# Base64 encode the credentials
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Creating the Basic Auth token
basic_auth_token = f"Basic {encoded_credentials}"

# Output the token
print(basic_auth_token)
